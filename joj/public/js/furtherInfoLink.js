"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, Utils: false, escape: false */

var FurtherInfoLink = function (conf) {
    var i, propName;
    
    for (i = 0; i < this.REQUIRED_PROPERTIES.length; i++) {
        
        propName = this.REQUIRED_PROPERTIES[i];
        
        if (conf[propName] === undefined) {
            var message = "Requierd property '" + propName + "' not found in conf" + Utils.getObjString(conf);
            WMSC.log(message);
            throw (message);
        }
        else {
            this[propName] = conf[propName];
        }
    }    

    for (i = 0; i < this.OPTIONAL_PROPERTIES.length; i++) {
        
        propName = this.OPTIONAL_PROPERTIES[i];
        
        if (conf[propName] !== undefined) {
            this[propName] = conf[propName];
        }
    }
    
};

FurtherInfoLink.prototype = {

    REQUIRED_PROPERTIES: ['endpoint', 'link'],
    OPTIONAL_PROPERTIES: ['name', 'image'],
   
   
    match: function (url) {
        return Utils.reMatch(this.endpoint, url);
    },
    
    getHTML: function () {
        var name = "info";
        
        if (Utils.hasAttr(this, 'name')) {
            name = this.name;
        }
        
        name = name.escapeHTML();

        if (Utils.hasAttr(this, 'image')) {
            name = name + '<image src="' + escape(this.image) + '" />';
        }        
        
        
        return '<a target="_blank" href="' + this.link + '">' + name + '</a>';
    }
        
};