"use strict";

/*jslint onevar: false*/

/**
 * @requires Openlayers.Event
 * @requires DisplayOptionRetriever
 */

/*globals WMSC: false, document:false, OpenLayers: false,
         DisplayOptionsRetriever: false, Utils: false*/

/**
 * An object to manage the content of the layer information form, the form
 * mostly contains items of information but can also be used to select the 
 * style for the layer if different styles are described in the capabilities
 * response.
 * 
 * Incoming events: 
 * 'CURRENT_WMCLAYER_CHANGED' - the current web map context layer has changed 
 *   so need to re-build the layer information
 * 
 * @constructor
 */
var LayerInfo = function (layerInfoContainerId, eventsManager, furtherInfoLinks) {
    
    if (furtherInfoLinks === undefined) {
        this.furtherInfoLinks = [];
    }
    else {
        this.furtherInfoLinks = furtherInfoLinks;
    }
    
    this._container = document.getElementById(layerInfoContainerId);
    this.eventsManager = eventsManager;
    
    this.eventsManager.register('CURRENT_WMCLAYER_CHANGED', this, this._onCurrentLayerChanged);
};

LayerInfo.prototype = {
        
    EVENTS_RAISED: [],
    
     /**
      * handler for the current layer changed event
      */
    _onCurrentLayerChanged: function (e) {
        
        if (e.wmcLayer !== null && e.olLayer !== null) {
            this._buildInfo(e.wmcLayer, e.olLayer);
        }
        else {
            this._clearInfo();
        }
        
    },
    
    /**
     * Rebuilds all of the display option controls given by the layer
     */
    _buildInfo: function (wmcLayer, olLayer) {
        
        var div = document.createElement('div');
        
        div.appendChild(this._buildInfoItem('URL', olLayer.url));
        div.appendChild(this._buildInfoItem('Layer Name', this._getLayerProperty(olLayer, 'layers')));
        div.appendChild(this._buildInfoItem('Layer Abstract', wmcLayer.getAbstract()));
        
        var infoHTML = "";
        
        for (var i = 0; i < this.furtherInfoLinks.length; i++) {
            var link = this.furtherInfoLinks[i];
            
            if (link.match(olLayer.url)) {
                infoHTML = infoHTML + link.getHTML() + ", ";
            }
        }
        
        if (infoHTML.length > 0) {
            infoHTML = infoHTML.slice(0, infoHTML.length - 2); // get rid of the last ','
            div.appendChild(this._buildInfoItem('Further Info', infoHTML));
        }
        
        this._clearInfo();
        this._container.appendChild(div);
    },

    _clearInfo: function () {
        this._container.innerHTML = "";
    },
    
    _getLayerProperty: function (olLayer, id) {
        var val = null;
        
        if (olLayer !== null) {
            val = olLayer.params[id.toUpperCase()];
        }
        
        return val;
    },
    
    _buildInfoItem: function (name, value) {
        var span = document.createElement('span');
        span.innerHTML = value;
        
        return Utils.buildLabelInputDiv(name, span, 'layerInfoItem');
        
    }
    
};
