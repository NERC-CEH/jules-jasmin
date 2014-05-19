"use strict";

/*jslint onevar: false*/

/**
 * @requires utils
 */

/**
 * @constructor
 */

/*global document:false, WMSC:false, Utils:false*/

var SplitAxisSelect = function (name, data, labelText, containerClass) {
    
    this.containerId = this.name + '_split_select';
    this.name = name;
    this.data = data;
    this.containerClass = containerClass;
    
    if (labelText === undefined) {
        this.labelText = name;
    }
    else {
        this.labelText = labelText;
    }
        
};

SplitAxisSelect.prototype = {

    build: function () {
    
        var container = document.createElement("div");
        if (this.containerClass !== undefined) {
            container.className = this.containerClass;
        }
    
        //if the data is an array just make a single select box
        if (this.data.constructor === Array) {
            
            container.appendChild(Utils.buildLabel(this.labelText, { id: this.name + '_label', htmlFor: this.name}));
            container.appendChild(document.createTextNode("\n"));
            container.appendChild(Utils.buildSelect('select_' + this.name, this.name, this.data, this.data));
            
        } //otherwise need to split the selection box up
        else {
            this._buildSplitSelect(container);
        }
        
        return container;
    },
    
    _buildSplitSelect: function (container) {
    
        container.appendChild(Utils.buildLabel(this.labelText, {id: this.name + '_label'}));
        container.appendChild(document.createTextNode("\n"));
        
        for (var i = 0; i < this.data.selectLists.length; i++) {
            var selectList = this.data.selectLists[i];
            var id = 'select_' + this.name + "_subselect_" + i;
            
            var div = document.createElement('div');
            div.className = "subselect_input";
            
            
            div.appendChild(Utils.buildLabel(selectList.label, {id: this.name + "_subselect_" + i + '_label'}));
            
            var sel = Utils.buildSelect(id, null, selectList.values, selectList.values);
            
            var handler = Utils.addHTMLEventListener(sel, 'change', this._buildTime, this);
            
            div.appendChild(sel);
            div.appendChild(document.createTextNode("\n"));
            container.appendChild(div);
        }
    
        
        var value = this.data.axisValues[0];
        
        container.appendChild(Utils.buildHiddenInputElement('select_' + this.name, value, 'select_' + this.name));
        container.appendChild(document.createTextNode("\n"));            
    
    },
    
        
    _buildTime: function () {
        var elt = document.getElementById('select_' + this.name);
        elt.value = this._buildTimeString();
    },

    _buildTimeString: function () {
        var timeValuesIndex = 0;
        
        for (var i = 0; i < this.data.selectLists.length; i++) {
        
            var id =  'select_' + this.name + "_subselect_" + i;
            var selElt = document.getElementById(id);
            
            timeValuesIndex += selElt.selectedIndex * this.data.selectLists[i].indexFactor;
        }
        
        return this.data.axisValues[timeValuesIndex];
    }
};