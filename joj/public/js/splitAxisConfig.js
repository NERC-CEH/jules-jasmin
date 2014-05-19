"use strict";

/*jslint onevar: false*/

/*globals WMSC: false */

/**
 * Represents the values for a single select box that is used as part
 * of a split select control.
 * 
 * @param indexFactor - the factor the selected index of this select should
 *  be multiplied by when generating the index of the return value.
 * @param label - the label this select box should be displayed with.
 * @param values - A list of the values that should be visible in this select box.
 */
var SplitAxisSelectList = function (indexFactor, label, values) {
    
    this.indexFactor = indexFactor;
    this.label = label;
    this.values = values;
    
};

/**
 * Represents the contents of an Axis element in the  SplitAxisConfig XML file, 
 * this describes the values and selections for a single named axis.
 * 
 * @param axisValues - a list of all the possible axis values.
 * @param selectLists - a list of SplitAxisSelectList objects that represent
 *     each of the select boxes used to select a value form axisValues. 
 */
var SplitAxisMapping = function (axisValues, selectLists) {
    
    this.axisValues = axisValues;
    this.selectLists = selectLists;
    
    for (var i = 0; i < selectLists.length; i++) {
        if (this.selectLists[i].constructor !== SplitAxisSelectList) {
            throw ("Unknown value in select list (" + this.selectLists[i].constructor + ") expected SplitAxisSelectList.");
        }
    }
    
};

var SplitAxisConfig = function (mappingObj) {
    
    for (var n in mappingObj) {
        
        var mapping = mappingObj[n];
        
        if (mapping.constructor !== SplitAxisMapping) {
            throw ("Unknown value in mapping list (" + mapping.constructor + ") expected SplitAxisMapping.");
        }
    }
    
    this.mappingObj = mappingObj;
    
};

SplitAxisConfig.prototype = {
        
    getAxisNames: function () {
        var names = [];
        
        for (var n in this.mappingObj) {
            names.push(n);
        }
        return names;
    },
    
    getAxisMapping: function (name) {
        var found = false;
        
        var names = this.getAxisNames();
        for (var i = 0; i < names.length; i++) {
            if (name === names[i]) {
                found = true;
                break;
            }
        }
        
        if (! found) {
            WMSC.log("Axis name " + name + " not found in the mapping list.");
            return null;
        }
        
        return this.mappingObj[name];
    }
        
};

/**
 * An object that reads a SplitAxisConfig xml file and builds a SplitAxisConfig 
 * object.
 * 
 * @param node - the root node of a SplitAxisConfig xml file.
 */
var SplitAxisConfigBuilder = function (node) {
    this.node = node;
};

SplitAxisConfigBuilder.prototype = {
    
    /**
     * Build a SplitAxisConfig object using the current node.
     */
    buildConfig: function () {
    
        var axisElements = this._getAllAxisElements();
        
        var mappingObj = {};
        
        for (var i = 0; i < axisElements.length; i++) {
            var axisElement = axisElements[i];
            
            var axisValues = this._buildAxisValues(axisElement);
            var selectLists = this._buildSelectLists(axisElement);
            
            var axisName = axisElement.getAttribute('name').toLowerCase();
            mappingObj[axisName] = new SplitAxisMapping(axisValues, selectLists);
            
        }
        
        return new SplitAxisConfig(mappingObj);
    },
    
    
    
    /**
     * Builds a list of axis values form the 'AxisValues' element
     */
    _buildAxisValues: function (node) {

        var axisValuesNode = WMSC.traverseWMSDom(node, ['AxisValues']);
        
        var axisValues = [];
        
        for (var i = 0; i < axisValuesNode.childNodes.length; i++) {
            var child = axisValuesNode.childNodes[i];
            if (child.nodeName === 'AxisValue') {
                axisValues.push(WMSC.getTextContent(child));
            }
        }
        
        return axisValues;
    },
    
    _getAllAxisElements: function () {
        var i;
        
        var elements = [];
        for (i = 0; i < this.node.childNodes.length; i++) {
            var child = this.node.childNodes[i];
            if (child.nodeName.toUpperCase() === 'AXIS') {
                elements.push(child);
            }
        } 
        
        return elements;
    },
    
    /**
     * Builds a list of SplitAxisSelectList objects form the children of the
     * 'SelectLists' element.
     */
    _buildSelectLists: function (node) {
        var selectListsNode = WMSC.traverseWMSDom(node, ['SelectLists']);
        
        var selectLists = [];
        
        for (var i = 0; i < selectListsNode.childNodes.length; i++) {
            var child = selectListsNode.childNodes[i];
            if (child.nodeName === 'SelectList') {
                selectLists.push(this._buildSplitAxisSelect(child));
            }
        }
        
        return selectLists;
        
    },
    
    /**
     * Builds a single SplitAxisSelectList object form a 'SelectList' element.
     */
    _buildSplitAxisSelect: function (node) {
        var indexFactor = node.getAttribute('indexFactor');
        var label = node.getAttribute('label');
        
        var values = [];
        
        for (var i = 0; i < node.childNodes.length; i++) {
            var child = node.childNodes[i];
            if (child.nodeName === 'Option') {
                values.push(WMSC.getTextContent(child));
            }
        }        
        
        return new SplitAxisSelectList(indexFactor, label, values);
        
    }
    
};
