"use strict";

/**
 * Builds a get Ajax request and caches the result, if the same parameters are
 * requested again the cached result is returned. 
 * 
 * As well as an on success function on failure and on exception functions can 
 * also be set. If these functions aren't set simple logging functions are 
 * used instead.
 */

/*global Ajax:false, WMSC:false */

var AjaxRetriever = function () {
    this._contextLookup = {};
};

AjaxRetriever.prototype = 
{
    lookup: {},
    
    getResponse: function (params, onSuccessFunction, onFailureFunction, onExceptionFunction) {
        
        this._getResponse(params, onSuccessFunction, onFailureFunction, onExceptionFunction);
    },
    
    _getResponse: function (params, onSuccessFunction, onFailureFunction, onExceptionFunction) {
        
        var pString, onRetrieve, req;
        
        if (this._isCached(params)) {
            
            pString = this._getParamsString(params);
            onSuccessFunction(this._contextLookup[pString]);
            
        } else {
            
            onRetrieve = function (xhr) {
                
//                WMSC.log("xhr.responseXML.documentElement.childNodes.length = " 
//                        + xhr.responseXML.documentElement.childNodes.length);
                
                var resp = this._processResponse(xhr);
                this._addToLookup(params, resp);
                onSuccessFunction(resp);
            };

            if (onFailureFunction === undefined) {
                onFailureFunction = function (resp) {   
                    WMSC.log("Failure:" + resp); 
                };
            }
            
            if (onExceptionFunction === undefined) {
                onExceptionFunction = function (resp, e) {
                    WMSC.log("Exception:" + e); 
                };
            }
            
            // invoke the call asynchronously via AJAX
            req = new Ajax.Request('', 
                {parameters: params,
                 method: "get",
                 onSuccess: onRetrieve.bindAsEventListener(this),
                 onException : onExceptionFunction,
                 onFailure : onFailureFunction
                });
        }
    },
    
    
    _processResponse: function (xhr) {
        return xhr;
    },
    
    _addToLookup: function (params, resp) {
        var pString = this._getParamsString(params);
        this._contextLookup[pString] = resp;
    },
    
    _isCached: function (params) {
        var pString, s;
        
        pString = this._getParamsString(params);
        
        for (s in this._contextLookup) {
            if (s === pString) {
                return true;
            }
        }
        
        return false;
    },
    
    _getParamsString: function (params) {
        var s = "", k;
        
        for (k in params) {
            s = s + k + ":" + params[k] + ",";
        }
        
        return s;
    }        
};