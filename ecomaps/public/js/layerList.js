"use strict";

/*jslint onevar: false*/

/**
 * Maintains an array of OpenLayers.Layer objects which are coupled to a YUI
 * draggable list. The Layer objects aren't created by this class but added via
 * the 'NEW_LAYER' event.
 * 
 * @class
 * 
 * @requires OpenLayers/Events.js
 * @requires OpenLayers/Class.js
 * 
 * @author P Norton
 */

/*globals WMSC: false, YAHOO: false, OpenLayers: false, document: false, 
          Utils:false, alert:false*/


var DDM = YAHOO.util.DragDropMgr;

var LayerList = OpenLayers.Class.create();

LayerList.prototype = {

	/** The Events raised by this object,
	 *    SELECTED_LAYER_CHANGED is raised when the selected layer is changed
	 *    LAYER_ORDER_CHANGED is raised when the order of the layers is changed
	 */
    EVENTS_RAISED: ['SELECTED_LAYER_CHANGED', 'LAYER_ORDER_CHANGED', 'LAYER_REMOVED'],

    MAX_LAYERS: 10,
    
    /**
     * OpenLayers Events object managing EVENTS_RAISED
     */ 
    events: null,
    
    SELECTED_CLASS: "selected",
    
    /**
     * Constructor to initialise layer control
     * @constructor
     *
     * @param dragListId - ID of the ul that is being used for the drag list
     */
    initialize: function (dragListId, outlineOnTopCheckboxId, eventsManager) {
    
		this._dragList = document.getElementById(dragListId);
		this._outlineOnTopChk = document.getElementById(outlineOnTopCheckboxId);
		this.eventsManager = eventsManager;
		
		// remove any initial children
		while (this._dragList.childNodes[0]) {
		    this._dragList.removeChild(this._dragList.childNodes[0]);
		}
		
	    this._layers = [];
	    
	    this.target = new YAHOO.util.DDTarget(dragListId);
	    this.removeLayerBtn = document.getElementById('btn_remove_selected_layer');
	    Utils.addHTMLEventListener(this.removeLayerBtn, 'click', this._onRemoveClick, this);
	    Utils.addHTMLEventListener(this._outlineOnTopChk, 'click', this._onOutlineOnTopClick, this);
	    
	    this.eventsManager.register("NEW_OUTLINE", this, this.onNewLayer);
	    this.eventsManager.register("NEW_LAYER", this, this.onNewLayer);
	},
    
	
	/**
	 * Adds the this._onItemClick event handler to all the current list items. 
	 */
	_addOnClickListeners: function () {
		var currentItems = this._getCurrentListItems();
		for (var i = 0; i < currentItems.length; i++) {
			Utils.addHTMLEventListener(currentItems[i], 'click', this._onItemClick, this);
		}
	},

	/**
	 * Handles the 'click' event for a list item, this selects any item that is
	 * clicked on
	 */
	_onItemClick: function (e) {
	    var target = e.target || e.srcElement;
		this._selectItem(target);
	},
	
	/**
	 * Handlese the drag end event when one of the list items has stoped 
	 * being dragged.
	 */
	_onDragEnd: function (item) {
		this._selectItem(item);
		
		if (this._outlineOnTopChk.checked && this._isOutlineInList()) {
		    if (! this._isOutlineOnTop()) {
		        this._moveOutlineToTop();
		    }
		}
		
		this._triggerLayerOrderChange();
	},
	
	/**
	 * Handles the remove button click event, this removes the currently 
	 * selected layer (if there is a currently selected layer).
	 */
	_onRemoveClick: function (event, target) {
	     
	    var selectedLayer = this.getSelectedLayer();
		if (selectedLayer !== null) {
		    var id = selectedLayer.id;
			this._removeSelectedItem();
			
			var items = this._getCurrentListItems(); 
			if (items.length > 1) {
			    
			    if (items[0].id === 'outline_layer') {
			        this._selectItem(items[1]);
			    }
			    else {
			        this._selectItem(items[0]);
			    }
				
			}
			else if (items.length === 1) {
			    this._selectItem(items[0]);
			}
			
			this._triggerLayerRemoved(id);
			this._triggerLayerOrderChange();
			this._triggerSelectedLayerChange();	//selected layer should now be null
		}
	},
	
	_onOutlineOnTopClick: function (event) {
	    if (this._outlineOnTopChk.checked && this._isOutlineInList()) {
	        if (! this._isOutlineOnTop()) {
	            this._moveOutlineToTop();
	            this._triggerLayerOrderChange();
	        }
	    }
	},
	
	/**
	 * Selects a given list item, does nothing if the item is already selected
	 */
	_selectItem: function (item) {

		if (! this._isSelected(item)) {
			this._unselectAll();
			item.className = this.SELECTED_CLASS + " " + item.className;
			this._triggerSelectedLayerChange();				
		}

	},
	
	/**
	 * unselects all of the current items in the list
	 */
	_unselectAll: function () {
		var currentItems = this._getCurrentListItems();
		for (var i in currentItems) {
			this._unselectItem(currentItems[i]);
		}
	},

	/**
	 * unselects a given item by removign the SELECTED_CLASS from the 
	 * item.className property. Does nothing if the item isn't selected.
	 */
	_unselectItem: function (item) {

		if (this._isSelected(item)) {
			item.className = item.className.slice(this.SELECTED_CLASS.length);
		}

	},
	
	/**
	 * Checks if an item is selected by checking the start of the .className for
	 * the SELECTED_CLASS class.
	 */
	_isSelected: function (item) {
	    if (item.className !== undefined) {
	        return item.className.slice(0, this.SELECTED_CLASS.length) === this.SELECTED_CLASS;
	    }
	    return false;
	},
	
	/**
	 * Finds the selected item from the currently selected items. As only one
	 * item can be selected at a time will return the first selected item
	 * it comes across.
	 */
	_getSelectedItem: function () {

		var currentItems = this._getCurrentListItems();
		for (var i in currentItems) {
			if (this._isSelected(currentItems[i])) {
				return currentItems[i];
			}
		}
		return null;
	},
	
	/**
	 * Removes the currently selected item from the list
	 */
	_removeSelectedItem: function () {
		var item = this._getSelectedItem();
		this._removeItem(item);
	},
	
	/**
	 * Removes a given item from the drag list
	 */
	_removeItem: function (item) {
		if (item !== null) {
			var x = DDM.getDDById(item.id);
			if (x !== null) {
			    x.unreg();
			}
			this._removeLayer(item.id);
			this._dragList.removeChild(item);
		}
	},
	
	/**
	 * removes the openlayers layer with the given layerId from the layer list.
	 */
	_removeLayer: function (layerId) {
		var oldLayers = this._layers;
		var newLayers = [];
		for (var i = 0; i < oldLayers.length; i++) {
		    
			var layer = oldLayers[i];
			
			if (layer.id !== layerId) {
				newLayers.push(layer);
			}
		}
		
		this._layers = newLayers;
	},
	
    /**
     * Adds a new list item to the draglist. 
     *
     * @param layerId - the id of the layer that this list item will correspond to
     */
	_addListItem: function (layer) {

		var currentItems = this._getCurrentListItems();
		
		var onDrag = Utils.buildScopedFunction(this._onDragEnd, this);
		
		var lItem = new YAHOO.example.DDList(layer.id, onDrag);
		
		var li = document.createElement('li');
		
		// if this is the first layer or an outline layer add it to the top
		// of the list.
		
		var firstItem = this._dragList.firstChild;
		if (firstItem === null) {
		    this._dragList.appendChild(li);
		}
		else if (layer.id === 'outline_layer') {
		    // the outline is always added to the top of the list
		    this._dragList.insertBefore(li, firstItem);
		}
		else if (this._outlineOnTopChk.checked && this._isOutlineInList()) {
		    
		    // make sure the outline is at the top
		    if (firstItem.id !== 'outline_layer') {
		        this._moveOutlineToTop();
		    }
		    
		    this._dragList.insertBefore(li, firstItem.nextSibling);
		    
		}
		else {
		    // add to top of list
		    this._dragList.insertBefore(li, firstItem);
		}
		
		
			
		li.className = "list";
		li.id = layer.id;
		li.appendChild(document.createTextNode(layer.name));

		this._addOnClickListeners();
		return li;
	},

	/**
	 * Returns the current list items in the draglist, these items are
	 * Element objects corresponding to the '<li>' items in the list.
	 */
	_getCurrentListItems: function () {
		var items = [];
		for (var i = 0; i < this._dragList.childNodes.length; i++) {
		    
			var child = this._dragList.childNodes[i];
			
			if (child.nodeType === 1 && child.nodeName === 'LI') {
				items.push(child);
			}
		}
		
		return items;
	},

    /**
     * Handles the NEW_LAYER event, adds the new layer to the list
     */
    onNewLayer: function (e) {
        
        if (this._layers.length >= this.MAX_LAYERS) {
            alert("Can't have more than " + this.MAX_LAYERS + " layers in the list.");
        }
        else {
            //check if this layer has already been added
            var duplicateId = false;
            for (var i = 0; i < this._layers.length; i++)  {
                if (this._layers[i].id === e.layer.id) {
                    duplicateId = true;
                }
            }
            
            if (duplicateId) {
                alert("Layer with id = " + e.layer.id + " already in the list");
            }
            else {
                this._addLayer(e.layer);
            }
        }
        
    },

    /**
     * Adds a new layer to the list, this adds a new 'li' element to the draglist
     * and adds the openlayers layer to the layer list.
     */
    _addLayer: function (layer) {

        this._layers.push(layer);
        var item = this._addListItem(layer);

        this._triggerLayerOrderChange();
        this._selectItem(item);
    },
    
    /**
     * Triggers the LAYER_ORDER_CHANGED event which occurs when the order
     * of the layers in the list has been changed.
     */
    _triggerLayerOrderChange: function () {
    	this.eventsManager.triggerEvent("LAYER_ORDER_CHANGED", {layers: this._getOrderedLayers()});	
    },
    
    /**
     * Triggers the SELECTED_LAYER_CHANGED event, this occurs when a different 
     * layer has been selected. 
     */
    _triggerSelectedLayerChange: function () {
    	this.eventsManager.triggerEvent("SELECTED_LAYER_CHANGED", {layer: this.getSelectedLayer()});
    },
    
    _triggerLayerRemoved: function (id) {
        this.eventsManager.triggerEvent("LAYER_REMOVED", {layer_id: id});
    },

    /**
     * Returns the openlayers layer objects in the order corresponding to the
     * current draglist items (with the top item in the list coming at the start
     * of the array). 
     * 
     * This is done by checking the id of the draglist items and retriving the
     * layers using the id.
     */
    _getOrderedLayers: function () {
    	var currentItems = this._getCurrentListItems();
    	
    	var layers = [];
		for (var i = 0; i < currentItems.length; i++) {
			var layerId = currentItems[i].id;
			layers.push(this._getLayerById(layerId));
		}

		return layers;
    },
    
    /**
     * Gets a openlayers layer form the layer list with the given id.
     */
    _getLayerById: function (id) {
    	for (var i = 0; i < this._layers.length; i++)  {
    		if (this._layers[i].id === id) {
    			return this._layers[i];
    		}
    	}
    	return null;
    },
    
    /**
     * Gets the openlayers layer that corresponds to the currently selected
     * list item.
     */
    getSelectedLayer: function () {
    	
    	var item = this._getSelectedItem();
    	var layer;
    	
    	if (item === null) {
    		layer = null;
    	} else {
    		layer = this._getLayerById(item.id);
    	}
    	return layer;
    },

	destroy: function () {
    	this.target.unreg();
    	this._removeAllItems();
	},
	
	_isOutlineInList: function () {
	    return this._getLayerById('outline_layer') !== null;
	},
	
	_isOutlineOnTop: function () {
        return this._dragList.firstChild.id === 'outline_layer';
	},
	
	_moveOutlineToTop: function () {
	    var firstItem = this._dragList.firstChild;
	    
        if (firstItem.id === 'outline_layer') {
            return; // don't need to move it
        }
        
        var outlineItem = null;
        
        for (var i = 1; i < this._dragList.childNodes.length; i++) {
            var child = this._dragList.childNodes[i];
            if (child.id === 'outline_layer') {
                outlineItem = child;
                break;
            }
        }
        
        if (outlineItem !== null) {
            this._dragList.insertBefore(outlineItem, firstItem);
        }
        
	},
	
	/**
	 * Removes all the items from the drag list.
	 */
	_removeAllItems: function () {
    	var currentItems = this._getCurrentListItems();
    	
		for (var i = 0; i < currentItems.length; i++) {
			this._removeItem(currentItems[i]);
		}	
	}
};
