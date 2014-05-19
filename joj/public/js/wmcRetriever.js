"use strict";

/*jslint onevar: false*/

/*global OpenLayers:false, WMSC:false, Ajax:false */

var WMCRetriever = OpenLayers.Class.create();

WMCRetriever.prototype = {
	contextLookup: {},
	
    initialize: function (initialEndpoint) {
		
		//if the inital endpoint is set then request the 
		// context ready for use.
		if (initialEndpoint !== undefined) {
			this.getWMC(initialEndpoint);
		}
		
    },		
    
    getWMC: function (endpoint, onSuccessFunction, onFailureFunction) {
    	if (this.isWMCCached(endpoint)) {
    		onSuccessFunction(this.contextLookup[endpoint]);
    		
    	} else {
    		
	    	var onRetrieveWMC = function (xhr) {
	    		
//	    	    WMSC.log("xhr.responseXML.documentElement.childNodes.length = " 
//	    	            + xhr.responseXML.documentElement.childNodes.length);
	    	    
		    	//var wmc = new WMSC.WebMapContext(xhr.responseXML.documentElement);
		    	var wmc = new WMSC.Capabilities(xhr.responseXML.documentElement);
		    	this.addWMCToLookup(endpoint, wmc);
		    	
		    	onSuccessFunction(wmc);
			};

			//var params = {REQUEST: 'GetWebMapContext', ENDPOINT: endpoint};
			var params = {REQUEST: 'GetWebMapCapabilities', ENDPOINT: endpoint};

			if (onFailureFunction === undefined) {
			    onFailureFunction = function (resp) {   
			        WMSC.log("Failure:" + resp); 
			    };
			}
			
			// invoke the GetWebMapContext call asynchronously via AJAX
			var req = new Ajax.Request('', 
				{
			        parameters: params,
			        method: "get",
			        onSuccess: onRetrieveWMC.bindAsEventListener(this),
			        onException : function (resp, e) {   
			            WMSC.log("Exception:" + e); 
			        },
			        onFailure : onFailureFunction
				}
			);
    	}
    },
    
    addWMCToLookup: function (endpoint, wmc) {
    	this.contextLookup[endpoint] = wmc;
    },
    
    isWMCCached: function (endpoint) {
        var ep;
        
    	for (ep in this.contextLookup) {
    		if (ep === endpoint) {
    			return true;
    		}
    	}
    	return false;
    }
};