"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, OpenLayers: false, document: false, AjaxRetriever: false, Utils: false*/

var LegendContainer = OpenLayers.Class.create();

LegendContainer.prototype = {
		
	initialize: function (legendDivId, eventsManager) {
		this.legendDiv = document.getElementById(legendDivId);
		this._retriever = new AjaxRetriever();
		this.eventsManager = eventsManager;
		
		this.eventsManager.register("LAYER_PROPERTY_CHANGED", this, this.onLayerPropertyChanged);
		this.eventsManager.register("CURRENT_WMCLAYER_CHANGED", this, this.onLayerChanged);		
	},

    /**
     * handles the CURRENT_WMCLAYER_CHANGED event, replaces the legend
     * with one correponding to the new layer (if the new layer isn't null.
     */
    onLayerChanged: function (e) {
        this.setLegendForLayer(e.olLayer, e.wmcLayer);
    },
    
    /**
     * handles the LAYER_PROPERTY_CHANGED event. A property on the layer has 
     * changed, need to re-draw the legend
     */
    onLayerPropertyChanged: function (e) {
    	this.setLegendForLayer(e.layer, e.wmcLayer);
	},
	
	
	setLegendForLayer: function (olLayer, wmcLayer) {
	    
	    var legendLoaded = false;
	    
	    if (wmcLayer !== null && olLayer !== null) {
            
            var style = olLayer.params.STYLES;
            var url = wmcLayer.getLegendURL(style);
            
            WMSC.log("Legend url = " + url);
            
            if (url !== null) {
                
                // add the current openlayers layer parameters
                // to the GetLegend url
                url = Utils.addParamsToUrl(url, olLayer.params);
                                
                this.loadNewLegend(url);
                
                legendLoaded = true;
            }
        }
	    
	    if (legendLoaded === false) {
	        this.clearLegend();
	    }
	},
	
	
	/**
	 * Loads a new legend from the given url, this uses the legendRetriver 
	 * to get the new legend html using AJAX and then calls the .setLegend
	 * function. 
	 */
	loadNewLegend: function (url) {
	                
        WMSC.log("getting legend url = " + url);
        
	    var onSuccessFn = this.setLegend.bindAsEventListener(this);
	    
	    var params = {REQUEST: 'GetLegend', ENDPOINT: url};
        
        this._retriever.getResponse(params, onSuccessFn);
	},
	
	/**
	 * Takes the xhr response text and places it inside the legend div.
	 * The response text should be a valid <img> element.
	 */
	setLegend: function (xhr) {
		WMSC.log("setting legend at" + new Date());
    	this.legendDiv.innerHTML = '';
    	var legendHTML = xhr.responseText;
		if (legendHTML) {
			this.legendDiv.innerHTML = legendHTML;
		}
	},
	
	/**
	 * clears the content from the legendDiv
	 */
	clearLegend: function (xhr) {
		this.legendDiv.innerHTML = '';
	}
};