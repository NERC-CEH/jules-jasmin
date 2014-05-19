"use strict";

/*jslint onevar: false*/

/**
 * 
 */

/*global AjaxRetriever:false, WMSC:false, SplitAxisConfigBuilder:false */

var AxisConfigRetriever = function () {
    this._contextLookup = {};
};

AxisConfigRetriever.prototype = new AjaxRetriever();
AxisConfigRetriever.prototype.constructor = AxisConfigRetriever;

AxisConfigRetriever.prototype.getResponse = function (url, onSuccessFunction, onFailureFunction, onExceptionFunction) {
    var params = {REQUEST: 'GetAxisConfig', URL: url};
    this._getResponse(params, onSuccessFunction, onFailureFunction, onExceptionFunction);
};
        
AxisConfigRetriever.prototype._processResponse = function (xhr) {
    
    respXML = xhr.responseXML;

    var builder = new SplitAxisConfigBuilder(respXML.documentElement);
    return builder.buildConfig();
};
