"use strict";

/*jslint onevar: false*/


/**
 * @requires utils
 */

/**
 * @constructor
 */

/*global document:false, WMSC:false, Utils:false*/

var SplitSelect = function (containerId, name, data, labelText) {
    
    this._container = document.getElementById(containerId);
    this.name = name;
    this.data = data;
    
    if (labelText === undefined) {
        this.labelText = name;
    }
    else {
        this.labelText = labelText;
    }
        
};

SplitSelect.prototype = {
    
    build: function () {
        
        //if the data is an array just make a single select box
        if (this.data.constructor === Array) {
            
            WMSC.log("data =" + this.data);
            this._container.appendChild(Utils.buildLabel(this.labelText, { id: this.name + '_label', htmlFor: this.name}));
            this._container.appendChild(document.createTextNode("\n"));
            this._container.appendChild(Utils.buildSelect(this.name, this.name, this.data, this.data));
            
            
        } //otherwise need to split the selection box up
        else {
            this._buildSplitSelect();
        }
    },
    
    _buildSplitSelect: function () {

        this._container.appendChild(Utils.buildLabel(this.labelText, {id: this.name + '_label'}));
        this._container.appendChild(document.createTextNode("\n"));
        
        var items = this._getItemOrder();
        for (var i = 0; i < items.length; i++) {
            var n = items[i];
            var sel = Utils.buildSelect(this.name + "_" + n, this.name + "_" + n, this.data[n], this.data[n]);
            
            var handler = Utils.addHTMLEventListener(sel, 'change', this._buildTime, this);
            
            this._container.appendChild(sel);
            this._container.appendChild(document.createTextNode("\n"));
        }

        var value = this._buildTimeString();
        
        this._container.appendChild(Utils.buildHiddenInputElement(this.name, value, this.name));
        this._container.appendChild(document.createTextNode("\n"));            

    },
    
    _getItemOrder: function () {
        var indicies = [];
        var format = this.data._fmt;
        for (var item in this.data) {

            if (item === '_fmt') {  
                continue;  
            }
            
            indicies.push([item, format.indexOf(item)]);
        }
      
        var sortNumber = function (a, b) { 
            return a[1] - b[1]; 
        };

        indicies = indicies.sort(sortNumber);
      
        var items = [];
        for (var i = 0; i < indicies.length; i++) {
            items.push(indicies[i][0]);
        }
      
        return items;
    },
    
    _buildTime: function () {
        WMSC.log("Building time");
        var elt = document.getElementById(this.name);
        elt.value = this._buildTimeString();
    },

    _buildTimeString: function () {
        var s = this.data._fmt;
        var items = this._getItemOrder();
        for (var i = 0; i < items.length; i++) {
            var opt = items[i];
          
            var elt = document.getElementById(this.name + "_" + opt);
            var reg = new RegExp("%\\(" + opt + "\\)s", "gm");             
            s = s.replace(reg, elt.value);
        }
        return s;
    }
};