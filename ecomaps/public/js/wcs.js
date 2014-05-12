"use strict";

/*jslint onevar: false sub:true*/

/*global WMSC:false, window:false, layerParameters:false, document:false, 
         alert:false, Utils:false, AjaxRetriever:false, */

var WCSDownloadControl = function (downloadDivId, initailBounds, eventsManager) {
    
    this.downloadButton = this.createDownloadButton();
    this.eventsManager = eventsManager;
    this.downloadDiv = document.getElementById(downloadDivId);
    this.currentBounds = initailBounds;
    this.currentLayer = null;
    this._retriever = new AjaxRetriever();
    
    
    Utils.addHTMLEventListener(this.downloadButton, 'click', this.setupWCSrequest, this);
    
    this.downloadDiv.appendChild(this.downloadButton);    
    
    this.eventsManager.register('MAP_SELECTION_CHANGED', this, this._onMapSelectionChanged);
    this.eventsManager.register('SELECTED_LAYER_CHANGED', this, this._onSelectedLayerChanged);
};

WCSDownloadControl.prototype = {
        
    //Create a WCS download button
    createDownloadButton: function () {
        var button = document.createElement('input');
        button.type = 'submit';
        button.id = 'wcsdownload';
        button.value = 'Download Data';
        return button;
    },
    
    _onMapSelectionChanged: function (e) {
        this.currentBounds = e.selection;  
    },
    
    _onSelectedLayerChanged: function (e) {
        this.currentLayer = e.layer;
        
        if (this.currentLayer === null) {
            this.downloadButton.disabled = true;
            
        } else {
            
            this.downloadButton.disabled = false;
            
            WMSC.log("WCS endpoint is now " + this._getWCSEndpoint());
            
//            var wcsGetCapabilities = Utils.replaceParamsInUrl(this._getWCSEndpoint(), 
//                                       {Request:'GetCapabilities', Service:'WCS'});
//            
//            WMSC.log("wcsGetCapabilities = " + wcsGetCapabilities);
//            
//            var onSuccess = function(xhr, wcsEndpoint) {
//                // check the endpoint hasn't changed
//                if (this._getWCSEndpoint() === wcsEndpoint) {
//                    this.downloadButton.enabled = true;
//                }
//            };
//            
//            var onFail = function(resp, wcsEndpoint) {
//                if (this._getWCSEndpoint() === wcsEndpoint) {
//                    this.downloadButton.enabled = false;
//                }
//            };
//            
//            var onExcept= function (resp, e) {
//                WMSC.log("Exception:" + e); 
//            };
//            
//            var params = {REQUEST: 'GetLegend', ENDPOINT: url};
//            
//            var req = new Ajax.Request('', 
//                    {method: "get",
//                     params: params,
//                     onSuccess: onSuccess.bindAsEventListener(this, this._getWCSEndpoint()),
//                     onException : onExcept,
//                     onFailure : onFail.bindAsEventListener(this, this._getWCSEndpoint())
//                    });
        }
        
        return 1;
    },
    
    // call WCS with current map parameters (bbox, layer, crs, dimensions etc)
    setupWCSrequest: function () {
        
        if (this.currentLayer === null) {
            alert("No layer currently selected.");
            return;
        }
        
        //gets the information from the gui needed to make a WCS request. e.g. selected bounding box and other dimensions
        //this implemenation assumes wcs endpoint mirrors wcs endpoint - could get this from webmapcontext dataurl instead??
        //note, in future this could be expanded to use OWSLib and provide a WCS client interface	
        // get the topmost layer
        // NB, there are initially three layers - for the subselection box, coastline and base map
        
        var wcsEndpoint = this._getWCSEndpoint();
        
        var coords = document.getElementById('coordsForm');
           
        var bboxStr = this.currentBounds.left + ',' + this.currentBounds.bottom + ',' + this.currentBounds.right + ',' + this.currentBounds.top;
        
        var dims = layerParameters.layerDims.getSelectedDimensions();
        
        this.makeWCSrequest(wcsEndpoint, this.currentLayer.params.LAYERS, bboxStr, dims);
    },
    
    
    makeWCSrequest: function (wcsEndpoint, coverageid, bbox, dims) {
        // makes the request to the WCS server
        
        var params = {'request': 'GetCoverage', 'service': 'WCS', 'version': '1.0.0', 'crs': 'EPSG:4326', 'format': 'cf-netcdf'};  //to store the wcs parameters
        
        //add coverage, bbox and dimension parameters
        params['coverage'] = coverageid;
        
        params['bbox'] = bbox;
        
        for (var dim_id in dims) {
            params[dim_id] = dims[dim_id];
        }	
        
        //build url string
        var wcsurl = wcsEndpoint;
        
        for (var param in params) {
            wcsurl = wcsurl + param + '=' + params[param] + '&';
        }
        
        WMSC.log('Making wcs request to ' + wcsurl);
        window.open(wcsurl, 'download'); 
        return false;
    },
    
    _getWCSEndpoint: function () {
        var wmsurl = this.currentLayer.getFullRequestString();
        var urlparts = wmsurl.split('?');
        var wcsEndpoint = urlparts[0].replace('wms', 'wcs') + '?';
        return wcsEndpoint;
    }
};





