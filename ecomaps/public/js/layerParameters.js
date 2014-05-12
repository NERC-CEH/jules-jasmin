"use strict";

/*jslint onevar: false*/

/**
 * @requires Openlayer.Event
 * @requires DisplayOptionsRetriever
 * @requires utils
 * 
 */

/*globals WMSC: false, OpenLayers: false, LayerDisplayOpts: false,
          LayerInfo: false, LayerDimensions: false, document: false*/

/**
 * The LayerParameters manages the content of style properties, display options
 * and the dimensions forms and updates them so that they remain consisntent 
 * with the currently selected layer.
 * 
 * It also has the ability to show/hide all of the forms via the properties div.
 * @constructor
 */
var LayerParameters = function (propertiesDivId, selectionFormId, wmcRetriever, 
                                hideDisplayOptions, eventsManager, furhterInfoLinks) {
    
    this.eventsManager = eventsManager;
    
    this.propertiesDiv = document.getElementById(propertiesDivId);

    this.currentOLLayer = null;
    this.currentWMCLayer = null;
    this.wmcRetriever = wmcRetriever;
    
    this.layerInfo = new LayerInfo('layer_info', this.eventsManager, furhterInfoLinks);
    this.layerDims = new LayerDimensions('WMSC_dimForm', this.eventsManager);
    this.layerDisplay = new LayerDisplayOpts(selectionFormId, hideDisplayOptions, this.eventsManager);
       
    // monitor all the parameter changes
    this.eventsManager.register('LAYER_DISPLAY_CHANGED', this, this.onParamChange);
    this.eventsManager.register('LAYER_DIMENSION_CHANGED', this, this.onParamChange);
    
    
    this.eventsManager.register("SELECTED_LAYER_CHANGED", this, this.onSelectedLayerChanged);
    
    WMSC.log("layer parameters created");
};

LayerParameters.prototype = {
        
    EVENTS_RAISED: ['LAYER_PROPERTY_CHANGED', 'CURRENT_WMCLAYER_CHANGED', 'LAYER_STYLE_CHANGED'].concat(
            LayerInfo.prototype.EVENTS_RAISED,
            LayerDimensions.prototype.EVENTS_RAISED,
            LayerDisplayOpts.prototype.EVENTS_RAISED),
        
    onParamChange: function (e) {

        if (this.currentOLLayer !== null) {
            this.currentOLLayer.params[e.param.toUpperCase()] = e.value;
            this.currentOLLayer.redraw();
        }

        this.eventsManager.triggerEvent("LAYER_PROPERTY_CHANGED", 
                {layer: this.currentOLLayer, wmcLayer: this.currentWMCLayer});        
        
        if (e.param.toUpperCase() === 'STYLES') {
            this.eventsManager.triggerEvent("LAYER_STYLE_CHANGED", 
                    {style: e.value});
        }
        
    },    
    
    /**
     * Handles the SELECTED_LAYER_CHANGED event, when the layer is changed the current
     * controls are removed and new ones corresponding to the new layer are created.
     * 
     * This also updates the this.currentLayer property.
     */
    onSelectedLayerChanged: function (e) {
                
        this.currentOLLayer = e.layer;
        this.currentWMCLayer = null;
        
        if (e.layer === null) {
            var eventArgs = {wmc: null, olLayer: null, wmcLayer: null};
            this.globalEventsManager.triggerEvent('CURRENT_WMCLAYER_CHANGED', eventArgs);
            this.internalEvents.triggerEvent('CURRENT_WMCLAYER_CHANGED', eventArgs);            
            
        } else {
            this.updateControls();
        }

    },

    /**
     * Hides the properties div
     */
    hideControls: function () {
        this.propertiesDiv.style.display = 'none';
    },

    /**
     * Shows the properties div and re-builds all of the controls in it
     */
    showControls: function () {
        this.propertiesDiv.style.display = 'block';
    },
    
    updateControls: function () {
        var successFn = this.buildControls.bindAsEventListener(this);   
        this.wmcRetriever.getWMC(this.currentOLLayer.url, successFn);
    },
    
    /**
     * Builds all the controls in the properties div using a WebMapCapabilities
     * object.
     */
    buildControls: function (wmc) {
        
        //find the dimensions for the layer
        var wmcLayer = this.searchSubLayers(wmc.getSubLayers());
        
        if (wmcLayer === null) {
            WMSC.log("WARNING: layer " + this.currentOLLayer.params.LAYERS + " not found in capabilities document.");
        }
        
        this.currentWMCLayer = wmcLayer;
        
        var eventArgs = {
            wmc: wmc,
            olLayer: this.currentOLLayer,
            wmcLayer: this.currentWMCLayer
        };
        
        this.eventsManager.triggerEvent('CURRENT_WMCLAYER_CHANGED', eventArgs);
    },
    
    /**
     * Searches a list of WMC.Layer objects to find the one that corresponds
     * to the current layer. 
     * 
     * @returns The WMC.Layer object corresponding to the currently selected layer
     */
    searchSubLayers: function (subLayers) {
        var wmcLayer = null;
        
        for (var i = 0; i < subLayers.length; i++) {
            var layer = subLayers[i];
            
            if (layer.getName() === this.currentOLLayer.params.LAYERS) {
                wmcLayer = layer;
                break;
            }
            
            // the desired layer may be a child of this layer so search any sublayers
            if (layer.getSubLayers().length > 0) {
                wmcLayer = this.searchSubLayers(layer.getSubLayers());
                
                if (wmcLayer !== null) {
                    break;
                }
            }
            
                
            
        }
        
        return wmcLayer;
    },
    

    destroy: function () {
        this.internalEvents.destroy();
        this._removeAllItems();
    }
};