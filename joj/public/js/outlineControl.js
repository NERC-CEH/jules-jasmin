"use strict";

/*jslint onevar: false*/

/*globals Utils: false, document: false, OpenLayers: false*/

var OutlineControl = function (outlineButtonId, eventsManager, options) {
    
    this.outlineButton = document.getElementById(outlineButtonId);
    
    this.eventsManager = eventsManager;
    
    for (var i = 0; i < this.OPTIONAL_ARGS.length; i++) {
        var optionName = this.OPTIONAL_ARGS[i];
        if (options[optionName] !== undefined) {
            this[optionName] = options[optionName];
        }
    }
    
    Utils.addHTMLEventListener(this.outlineButton, 'click', this.addNewOutline, this);
    
    this.eventsManager.register("LAYER_REMOVED", this, this.onLayerRemoved);
};

OutlineControl.prototype = {
        
    EVENT_TYPES: ['NEW_OUTLINE'],
    
    OPTIONAL_ARGS: ['url', 'params'],
    
    url: 'http://labs.metacarta.com/wms/vmap0',
    
    params: {'layers': 'coastline_01', 'format': 'image/png'},
    
    addNewOutline: function () {
        var outlineLayer = new OpenLayers.Layer.WMS(
                'Outline',
                this.url, 
                this.params,
                {isBaseLayer: false, buffer: 1});
    
        // must set these parameters or the map wil not draw
        outlineLayer.params.CRS = 'CRS:84';
        outlineLayer.params.FORMAT = 'image/png';
        if (typeof(outlineLayer.params.VERSION) == 'undefined') {
            outlineLayer.params.VERSION = '1.3.0';
        }
        outlineLayer.params.TRANSPARENT = 'true';
        
        // can't use the default id as there is already an element with that
        // id on the page.
        outlineLayer.id = "outline_layer"; 
        
        this.eventsManager.triggerEvent("NEW_OUTLINE", {layer: outlineLayer});
        this.outlineButton.disabled = true;
    },
    
    onLayerRemoved: function (e) {
        if (e.layer_id === 'outline_layer') {
            this.outlineButton.disabled = false;
        }
    }
};