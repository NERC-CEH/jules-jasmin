"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, Ajax: false, JSON: false*/

var DisplayOptionsRetriever = function () {
    this._lookup = {};            
};

DisplayOptionsRetriever.prototype = {

    getDisplayOptions: function (url, onSuccessFunction, onFailureFunction, onExceptionFunction) {
            
        if (this.isCached(url)) {
            onSuccessFunction(this._lookup[url]);
            
        } else {
            
            var onRetrieve = function (resp) {
                var obj = null;
                
                try {
                    obj = JSON.parse(resp.responseText);
                }
                catch (e) {
                    var msg = "Error occurred parsing JSON.\n Description:" + e.stack + "\n";
                    WMSC.log(msg);
                }
                
                this.addToLookup(url, obj);
                
                onSuccessFunction(obj);
            };

            if (onFailureFunction === undefined) {
                onFailureFunction = function(resp) {   
                    WMSC.log("Failure:" + resp); 
                };
            }
            
            if (onExceptionFunction === undefined) {
                onExceptionFunction = function(resp, e) {
                    WMSC.log("Exception:" + e); 
                };
            }

            var params = {REQUEST: 'GetDisplayOptions', URL: url};

            // invoke the GetWebMapContext call asynchronously via AJAX
            var req = new Ajax.Request('', 
                {
                    parameters: params,
                    method: "get",
                    onSuccess: onRetrieve.bindAsEventListener(this),
                    onException: onExceptionFunction,
                    onFailure: onFailureFunction
                });
        }
    },
    
    addToLookup: function (url, obj) {
        this._lookup[url] = obj;
    },
    
    isCached: function (url) {
        
        for (var l in this._lookup) {
            if (l === url) {
                return true;
            }
        }
        
        return false;
    }
};