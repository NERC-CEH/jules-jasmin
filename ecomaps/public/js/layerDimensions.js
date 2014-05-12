"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, OpenLayers: false, document: false, Utils: false, 
  AxisConfigRetriever:false, SplitAxisSelect:false */

/**
 * @requires Openlayer.Event
 * @requires utils
 * 
 */

/**
 * @constructor
 */
var LayerDimensions = function (layerDimensionsFormId, eventsManager) {
    this._form = document.getElementById(layerDimensionsFormId);
    this.eventsManager = eventsManager;
    this._handlerLookup  = null;
    this._retriever = new AxisConfigRetriever();
    
    this.eventsManager.register('CURRENT_WMCLAYER_CHANGED', this, this._onCurrentLayerChanged);
    
};

LayerDimensions.prototype = {
    
    EVENTS_RAISED: ['LAYER_DIMENSION_CHANGED'],
    
    
    _onCurrentLayerChanged: function (e) {
        this._clearForm();
        
        if (e.wmcLayer !== null && e.olLayer !== null) {
            var configURL = e.wmcLayer.getAxisConfigURL();
            
            if (configURL === null) {
                this._buildForm(e.wmcLayer, e.olLayer);
            }
            else {
                
                var onRetrieveAxisConfig = function (axisConfig) {
                    this._buildForm(e.wmcLayer, e.olLayer, axisConfig);
                };
                
                this._retriever.getResponse(
                        configURL, 
                        onRetrieveAxisConfig.bindAsEventListener(this)
                );
            }
        }
    },
    
    _clearForm: function () {
        
        if (this._handlerLookup !== null) {
            Utils.removeEventHandlersFromLookup(this._handlerLookup, 'change');
        	this._handlerLookup = null;
        }
        
        this._form.innerHTML = "";
    },    
    
    _buildForm: function (wmcLayer, olLayer, axisConfig) {
        
        var dims = wmcLayer.getDimensions();
        var div = document.createElement('div');
        
        for (var id in dims) { 
            
            var extent = dims[id].getExtent();
            
            var select = null;
            
            if (axisConfig === undefined) {
                select = new SplitAxisSelect(id, extent, dims[id].getName(), 'layerDimItem');
            }
            else {
                select = new SplitAxisSelect(id, axisConfig.getAxisMapping(id), dims[id].getName(), 'layerDimItem');
            }
            
            div.appendChild(select.build());

        }
        
        this._form.appendChild(div);
        
        // It appears that IE8 dosen't fire the onchange event for the fieldset
        // element like firefox does so adding the change handlers to the form
        // elements individually.
        this._handlerLookup = Utils.addHandlerToFormElements(this._form, 'change', this._onSelectionChange, this);        
        
    },
    
    /**
     * 
     */
    _onSelectionChange: function (e) {
        var target = e.target || e.srcElement;
        
        var param = null;
        var value = null;
        
        var ssIndex = target.id.indexOf('_subselect_');
        if (ssIndex > -1) {
            param = target.id.substring(7, ssIndex);
            value = document.getElementById('select_' + param).value;
        } else {
            param = target.id.substr(7);
            value = target.value;
        }

        this.eventsManager.triggerEvent("LAYER_DIMENSION_CHANGED", 
                {param: param, value: value});
    },

    /**
     * Given a dimension and a value return the display text
     */
    getDimensionText: function (dim, value) {
        return value;
    },
        
    _getLayerProperty: function (olLayer, id) {
        var val = null;
        
        if (olLayer !== null) {
            val = olLayer.params[id.toUpperCase()];
        }
        
        return val;
    },

    getSelectedDimensions: function () {
    	var dims = {};
    	
    	var elements = Utils.getActiveFormElements(this._form);
    	
    	for (var i = 0; i < elements.length; i++) {
    		var element = elements[i];
    		
    		if (element.name !== null) {
    		    
    		    var elementName = element.name;
    		    if (elementName.substr(0, 7) === 'selected_') {
    		        elementName = elementName.substr(7);
    		    }
    		    // get rid of the 'selected_' from the start of the element name
    		    
    			dims[elementName] = element.value;
    		}
    	}
    	
    	return dims;
    }
};