"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, document: false, Utils:false, OpenLayers:false 
          DisplayOptionsRetriever:false, escape:false*/

/**
 * @requires Openlayers.Event
 * @requires DisplayOptionRetriever
 */


/**
 * An object to manage the content of the layer display options form. When a 
 * layer is selected, if a display_options URL is set then the JSON from
 * the URL is retrieved and transformed into controls which set additional
 * styling parameters on the current layer.
 * 
 * Incoming events: 
 * 'LAYER_STYLE_CHANGED' - the style has been changed on the current layer so 
 *   the layer options need to be re-calculated to include any style specific 
 *   options 
 * 'CURRENT_WMCLAYER_CHANGED' - the current web map context layer has changed 
 *   so need to re-build the layer options (or not depending on if the 
 *   layer supports them).
 *   
 * Outgoing events:
 * 'LAYER_DISPLAY_CHANGED' - one of the display options has been changed.
 * 
 * @constructor
 */
var LayerDisplayOpts = function (layerDisplayOptionsFormId, hideDisplayOptions, eventsManager) {
    
    this._form = document.getElementById(layerDisplayOptionsFormId);
    this.eventsManager = eventsManager;
    this.displayOptsRetriever = new DisplayOptionsRetriever();
    this.hideDisplayOptions = hideDisplayOptions;
    this.currentWMCLayer = null;
    this.currentOLLayer = null;
    this._handlerLookup = null;
    
    this.eventsManager.register("LAYER_STYLE_CHANGED", this, this._onLayerStyleChanged);
    this.eventsManager.register('CURRENT_WMCLAYER_CHANGED', this, this._onCurrentLayerChanged);
};

LayerDisplayOpts.prototype = {
    EVENTS_RAISED: ['LAYER_DISPLAY_CHANGED'],

    _onSelectionChange: function (e) {
        var target = e.target || e.srcElement;

        var param = target.id.substr(7);        
        var value = target.value;
        
        if (target.type === "checkbox") {
        	value = (target.checked) ? 'True' : 'False';
        }
        
        WMSC.log("value = " + value);
        value = escape(value);
        WMSC.log("escaped value = " + value);
        
        this.eventsManager.triggerEvent('LAYER_DISPLAY_CHANGED', 
            {
                param: param, 
                value: value
            }
        );
    },

    /**
     * Handler for the layer style changed event, re-creates the display options
     * for the new style.
     */
    _onLayerStyleChanged: function (style) {
        this._buildDisplayControls();
    },
    
     /**
      * handler for the current layer changed event
      */
    _onCurrentLayerChanged: function (e) {
        this._clearForm();
        
        this.currentWMCLayer = e.wmcLayer;
        this.currentOLLayer = e.olLayer;
        
        if (e.wmcLayer !== null && e.olLayer !== null) {
            this._buildDisplayControls();
        }
        
    },
    
    /**
     * Rebuilds all of the display option controls given by the layer
     */
    _buildDisplayControls: function () {

        //add the display options (if set)
        var dispURL = this.currentWMCLayer.getDisplayOptionsURL();
        
        if (dispURL !== null) {
            var successFn = this._buildDisplayOptions.bindAsEventListener(this);
            
            this.displayOptsRetriever.getDisplayOptions(dispURL, successFn);
        }
        else {
            this._buildDisplayOptions(null);
        }
        
    },

    _clearForm: function () {
        
        if (this._handlerLookup !== null) {
            
            Utils.removeEventHandlersFromLookup(this._handlerLookup, 'change');
        	this._handlerLookup = null;
        }
        
        this._form.innerHTML = "";
    },    
    
    /**
     * Given a display options object builds a list of display options inputs for
     * the currently selected layer.
     */
    _buildDisplayOptions: function (displayOptions) {
        
    	this._clearForm();
    	
    	var endpoint = this.currentOLLayer.url;
    	var hideOptions = [];
    	
    	if (this.hideDisplayOptions !== null) {
    	    for (var i = 0; i < this.hideDisplayOptions.length; i++) {
    	        
    	        if (Utils.reMatch(this.hideDisplayOptions[i].endpoint, endpoint)) {
    	            for (var j = 0; j < this.hideDisplayOptions[i].options.length; j++) {
    	                hideOptions.push(this.hideDisplayOptions[i].options[j]);
    	            }
    	        }
    	        
    	    }
    	}
    	    	
        var div = document.createElement('div');

        // generic display options
        var layerStyles = this.currentWMCLayer.getStyles();
        var currentStyle = this._getCurrentLayerProperty('styles');
        
        div.appendChild(this._buildGenericDisplayOptions(layerStyles, currentStyle, hideOptions));
        
        // are there any additional display options for this endpoint
        if (displayOptions !== null) {
            // display options common to all layers for this endpoint (should appear first)
            if (displayOptions.common !== undefined) {
            	div.appendChild(this._buildDisplayOptionsList(displayOptions.common, hideOptions));
            }
            
            // display options for this particular style
            
            if (currentStyle !== null) {
                if (displayOptions[currentStyle] !== undefined) {
                    div.appendChild(this._buildDisplayOptionsList(displayOptions[currentStyle], hideOptions));
                }
            }
        }
            
        // this is needed as this function is called via AJAX an might be called
        // run at the same time as another 
        this._form.innerHTML = "";
        
        this._form.appendChild(div);
        
        // It appears that IE8 dosen't fire the onchange event for the fieldset
        // element like firefox does so adding the change handlers to the form
        // elements individually.
        this._handlerLookup = Utils.addHandlerToFormElements(this._form, 'change', this._onSelectionChange, this);
    },
    
    _buildGenericDisplayOptions: function (layerStyles, currentStyle, hideOptions) {
        var div = document.createElement('div');
        
        if (layerStyles.length > 0) {
            div.appendChild(this._buildStyleSelect(layerStyles, currentStyle));
        }
        
        if (! Utils.isValueInList('transparent', hideOptions)) {
            div.appendChild(this._buildDisplayOptionBool({name: 'transparent', title: 'Transparent Background', defaultValue: 'true'}));
        }
        
        if (! Utils.isValueInList('bgcolor', hideOptions)) {
            div.appendChild(this._buildDisplayOptionValue({name: 'bgcolor', title: 'Background Colour', defaultValue: null}));
        }
        
        return div;
    },
    
    /**
     * Given a list of display options builds the corresponding html inputs.
     * 
     * @returns a div object containing all the inputs objects
     */
    _buildDisplayOptionsList: function (optionsList, hideOptions) {
        var div = document.createElement('div');

        for (var i = 0; i < optionsList.length; i++) {
            var opt = optionsList[i];
            
            if (Utils.isValueInList(opt.name, hideOptions)) {
                continue;
            }

            if (opt.type === 'select') {
                div.appendChild(this._buildDisplayOptionSelect(opt));
            } 
            else if (opt.type === 'value') {
                div.appendChild(this._buildDisplayOptionValue(opt));
            }
            else if (opt.type === 'bool') {
            	div.appendChild(this._buildDisplayOptionBool(opt));
            }
        }
        
        return div;
    },
    
    _buildDisplayOptionSelect: function (opt) {
        var title = this._getDisplayOptionTitle(opt);
        
        var defaultVal =  this._getDefaultValue(opt);
        var select = Utils.buildSelectBox(opt.name, opt.options, opt.options, defaultVal);
        
        var div = Utils.buildLabelInputDiv(title, select, 'displayOptionItem');
        return div;
    },
        
    _buildDisplayOptionValue: function (opt) {
        
        var title = this._getDisplayOptionTitle(opt);
        
        var input = document.createElement('input');
        input.id = 'select_' + opt.name;
        input.name = 'select_' + opt.name;
        input.type = 'text';
        input.value = this._getDefaultValue(opt);
        
        Utils.addHTMLEventListener(input, 'keypress', Utils.disableEnterKey, this);
        
        var div = Utils.buildLabelInputDiv(title, input, 'displayOptionItem');
        return div;
    },
    
    _buildDisplayOptionBool: function (opt) {
        
        var title = this._getDisplayOptionTitle(opt);
        
        var input = document.createElement('input');
        input.id = 'select_' + opt.name;
        input.name = 'select_' + opt.name;
        input.type = 'checkbox';
        input.onClick = "";
        
        var defaultVal = this._getDefaultValue(opt);
        
        if (String(defaultVal).toUpperCase() === "TRUE") {
        	input.checked = true;
        }
                    
        var div = Utils.buildLabelInputDiv(title, input, 'displayOptionItem');
        return div;
    },
    
    _getDefaultValue: function (opt) {
        var val = this._getCurrentLayerProperty(opt.name);
        
        if (val === null || val === undefined) {
        	if (opt.defaultVal === undefined || opt.defaultVal === null) {
        		val = '';
        	}
        	else {
        		val = opt.defaultVal;
        	}
        }
        
        return val;
    },
    
    _getCurrentLayerProperty: function (id) {
        var val = null;
        
        if (this.currentOLLayer !== null) {
            val = this.currentOLLayer.params[id.toUpperCase()];
            
            if (val === "" && id.toUpperCase() === 'STYLES') {
                
                //assume that the first sytle is the default one
                var styles = this.currentWMCLayer.getStyles();
                
                if (styles.length > 0) {
                    val = styles[0].name;
                }
                
            }
        }
        
        return val;
    },
    
    _getDisplayOptionTitle: function (opt) {
        var title = opt.title;
        
        if (title === undefined) {
            title = opt.name;
        }
        
        return title;
    },
    
    _buildStyleSelect: function (styles, currentStyle) {
        
        var values = [];
        var descriptions = [];
        
        for (var i = 0; i < styles.length; i++) {
            values.push(styles[i].name);
            descriptions.push(styles[i].title);
        }
        
        this._styleSelect = Utils.buildSelectBox('styles', descriptions, values, currentStyle);
        
        return Utils.buildLabelInputDiv('Style', this._styleSelect, 'layerInfoItem');
    }
        
};