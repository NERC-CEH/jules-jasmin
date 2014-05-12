"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, OpenLayers: false, document: false, Utils: false, 
          DisplayOptionsRetriever:false*/

var LayerFigureDownload = function (containerId, eventsManager) {
    
    this._container = document.getElementById(containerId);
    
    this._container.innerHTML = this.controlMarkup;
    
    this._form = document.getElementById('layer_figure_download_form');
    
    this.eventsManager = eventsManager;
    this.displayOptsRetriever = new DisplayOptionsRetriever();
    this.currentWMCLayer = null;
    this.currentOLLayer = null;
    
    this._hiddenInputContainer = null;
    this._selectHandler = null;
    this._getFigureHandler = null;
    this._getFigureButton = null;
    this._styleSelect = null;
    
    this._currentSelection =  new OpenLayers.Bounds(-180, -90, 180, 90);
    
    this.eventsManager.register('CURRENT_WMCLAYER_CHANGED', this, this._onCurrentLayerChanged);
    this.eventsManager.register('MAP_SELECTION_CHANGED', this, this._onMapSelectionChanged);
};

LayerFigureDownload.prototype = {
        
    EVENTS_RAISED: [],
    
    LABEL_TEXT: "Get Figure for Selected Layer",
    
    controlMarkup: '<form id="layer_figure_download_form">\n' +
                   '</form>\n',
    
     /**
      * handler for the current layer changed event
      */
    _onCurrentLayerChanged: function (e) {
        
        this._clearForm();
        
        if (e.wmcLayer !== null && e.olLayer !== null) {
            this._buildInfo(e.wmcLayer, e.olLayer, e.wmc);
        }
        
        this.currentOLLayer = e.olLayer;
        this.currentWMCLayer = e.wmcLayer;
    },
    
    /**
     * Rebuilds all of the display option controls given by the layer
     */
    _buildInfo: function (wmcLayer, olLayer, wmc) {
                
        if (wmc.supportsRequest('GetFigure')) {
            var label = Utils.buildLabel(this.LABEL_TEXT);
            this._form.appendChild(label);
            
            this._form.appendChild(this._buildGetFigureButton(wmc));
            this._form.appendChild(document.createTextNode("\n"));
        }

        this._hiddenInputContainer = document.createElement('div');
        this._form.appendChild(this._hiddenInputContainer);
         
    },

    _clearForm: function () {
        
        // remove the event handler before deleting the element
        if (this._styleSelect !== null && this._selectHandler !== null) {
            Utils.removeHTMLEventListener(this._styleSelect, 'change', this._selectHandler);
        }
        
        // remove the get figure event handler
        if (this._getFigureButton !== null && this._getFigureHandler !== null) {
            Utils.removeHTMLEventListener(this._getFigureButton, 'click', this._getFigureHandler);
        }
        
        this._form.innerHTML = "";
        
        this._styleSelect = null;
        this._selectHandler = null;
        this._getFigureButton = null;
        this._getFigureHandler = null;
        this._hiddenInputContainer = null;
    },
    
    _getLayerProperty: function (olLayer, id) {
        var val = null;
        
        if (olLayer !== null) {
            val = olLayer.params[id.toUpperCase()];
        }
        
        return val;
    },
    
    _buildGetFigureButton: function (wmc) {
        var i;
        var div = document.createElement('div');
        
        var req = wmc.getRequest('GetFigure');
        
        var formatDescriptions = [];
        var formatValues = [];
        var formatList = req.formats;
        
        for (i = 0; i < formatList.length; i++) {
        
            formatValues.push(formatList[i]);
            
            if (formatList[i] === 'image/svg+xml') {
                formatDescriptions.push('SVG');
            }
            else if (formatList[i].indexOf('image/') === 0) {
                formatDescriptions.push(formatList[i].slice(6, formatList[i].length).toUpperCase());
            }
            else if (formatList[i] === 'application/postscript') {
                formatDescriptions.push('PS');
            }
            else if (formatList[i] === 'application/pdf') {
                formatDescriptions.push('PDF');
            }            
            else {
                formatDescriptions.push(formatList[i]);
            }
        }
        
        var inputs = Utils.buildSelect(null, 'format', formatDescriptions, formatValues);
        
        div.appendChild(inputs);
        
        this._getFigureButton = document.createElement('input');
        this._getFigureButton.type = 'button';
        this._getFigureButton.value = "Get Figure";
        
        this._getFigureHandler = Utils.addHTMLEventListener(this._getFigureButton, 
                                     'click', this._onGetFigureClick, this);
        
        div.appendChild(this._getFigureButton);
        return div;
    },
    
    _onGetFigureClick: function (e) {
        WMSC.log("_onGetFigureClick running");
        this._addHiddenInputItems();
        
        this._form.action = this.currentOLLayer.url; 
        this._form.method = "get"; 
        this._form.target = "_blank";
        this._form.submit();
    },
    
    _addHiddenInputItems: function () {
        
        // clear any old hidden inputs
        this._hiddenInputContainer.innerHTML = "";
        
        for (var p in this.currentOLLayer.params) {
            if (p.toUpperCase() === 'REQUEST') {
                this._hiddenInputContainer.appendChild(Utils.buildHiddenInputElement('REQUEST', 'GetFigure'));
            }
            else if (p.toUpperCase() === 'FORMAT') {
                //ignore the format parameter
            }
            else {
                this._hiddenInputContainer.appendChild(Utils.buildHiddenInputElement(p, this.currentOLLayer.params[p]));
            }
        }
        
        var bboxString = this._currentSelection.left + "," + this._currentSelection.bottom + "," + this._currentSelection.right + "," + this._currentSelection.top;
        
        this._hiddenInputContainer.appendChild(Utils.buildHiddenInputElement('BBOX', bboxString));
        this._hiddenInputContainer.appendChild(Utils.buildHiddenInputElement('WIDTH', '1200'));
        this._hiddenInputContainer.appendChild(Utils.buildHiddenInputElement('HEIGHT', '900'));
    },
   
    addMapSelectionChangedHandlers: function (events) {
        events.register('MAP_SELECTION_CHANGED', this, this.onChangeSelection);
    },
    
    _onMapSelectionChanged: function (e) {
        this._currentSelection = e.selection;
    }
    
};
