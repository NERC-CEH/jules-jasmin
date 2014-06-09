"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, Utils: false */

var Endpoint = function (conf) {
    
    for (var i = 0; i < this.REQUIRED_PROPERTIES.length; i++) {
        
        var propName = this.REQUIRED_PROPERTIES[i];
        
        if (conf[propName] === undefined) {
            var message = "Requierd property '" + propName + "' not found in conf" + Utils.getObjString(conf);
            WMSC.log(message);
            throw (message);
        }
        else {
            this[propName] = conf[propName];
        }
    }    
    
};

Endpoint.prototype = {

    REQUIRED_PROPERTIES: ['url', 'name', 'service']
        
};