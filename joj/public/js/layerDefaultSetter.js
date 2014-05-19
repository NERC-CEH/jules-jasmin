"use strict";

/*jslint onevar: false*/

/**
 * @requires utils
 * 
 */

/*globals Utils: false*/

/**
 * @constructor
 */

var LayerDefaultSetter = function (globalDefaults, defaultOptionsList) {
    this.globalDefaults = globalDefaults;
    this.defaultOptionsList = defaultOptionsList;
};

LayerDefaultSetter.prototype = {
    
    
    getDefaults: function (endpoint, layer) {
        
        var defaults = {};
        
        this._setValues(defaults, this.globalDefaults);

        if (this.defaultOptionsList !== null && this.defaultOptionsList !== "") {
            this._addDefaultsFromOptionsList(defaults, endpoint, layer);
        }
        
        return defaults;
        
    },
    
    _addDefaultsFromOptionsList: function (defaults, testEndpoint, testLayer) {
        
        for (var i = 0; i < this.defaultOptionsList.length; i++) {
            var endpointRegex = this.defaultOptionsList[i].endpoint;
            
            if (Utils.reMatch(endpointRegex, testEndpoint)) {
                
                for (var j = 0; j < this.defaultOptionsList[i].layers.length; j++) {
                    var layerRegex = this.defaultOptionsList[i].layers[j];
                    
                    if (Utils.reMatch(layerRegex, testLayer)) {
                        this._setValues(defaults, this.defaultOptionsList[i].values);
                    }
                }                
            }
        }
    },
    
    _setValues: function (defaults, obj) {
        
        for (var k in obj) {
            defaults[k] = obj[k];
        }
    }
    
};