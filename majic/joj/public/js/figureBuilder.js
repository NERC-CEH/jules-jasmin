"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, document: false, Utils: false, alert: false*/

var FigureBuilder = function (containerId, makeFigureActionURL, initialBounds, eventsManager) {
    
    this._container = document.getElementById(containerId);
    
    this._container.innerHTML = this.controlMarkup;
    
	this._form = document.getElementById('figureForm');
	this._form.action = makeFigureActionURL;
	this._button = document.getElementById('make_figure_btn');
	
	this._currentLayers = null;
	
	this._hiddenControlsDiv = this.buildHiddenControlsDiv();
	
	this._handler = Utils.addHTMLEventListener(this._button, 'click', this.createFigure, this);
	
	this._currentSelection = initialBounds;
	
	this.eventsManager = eventsManager;
	eventsManager.register("LAYER_ORDER_CHANGED", this, this.onLayerOrderChanged);
	eventsManager.register('MAP_SELECTION_CHANGED', this, this.onChangeSelection);
};

FigureBuilder.prototype = {

    controlMarkup: '\n' +
'<form id="figureForm" method="get">\n' +
'    <div>\n' +
'        <select name="figFormat">\n' +
'          <option value="image/png" selected="1"> PNG </option>\n' +
'          <option value="image/jpeg"> JPEG </option>\n' +
'          <option value="image/gif"> GIF </option>\n' +
'          <option value="application/postscript"> EPS </option>\n' +
'          <option value="image/svg+xml"> SVG </option>\n' +
'        </select>\n' +
'        <input type="button" value="Make Figure" id="make_figure_btn"/>\n' +
'    </div>\n' +
'</form>',
        
	/**
	 * When the layer order changes update the current layers
	 */
	onLayerOrderChanged: function (e) {
    	this._currentLayers = e.layers;
	},
	
	onChangeSelection: function (e) {
		this._currentSelection = e.selection;
		WMSC.log("this._currentSelection = " + this._currentSelection);
	},
	
	//add the div to contain the hidden elements
	buildHiddenControlsDiv: function () {
		var div = document.createElement('div');
		div.style.display = 'none';
		this._form.appendChild(div);
		return div;
	},
	
	createFigure: function () {
		this._hiddenControlsDiv.innerHTML = "";
		if (this._currentLayers === null || this._currentLayers.length === 0) {
			alert("No layer found.");
		}
		else {
			
			for (var i = 0; i < this._currentLayers.length; i++) {
				var layer = this._currentLayers[i];
				this._hiddenControlsDiv.appendChild(this._buildLayerInputs(i + 1, layer));
			}
			
			var bboxString = this._currentSelection.left + "," + this._currentSelection.bottom + "," + this._currentSelection.right + "," + this._currentSelection.top;
			
			this._hiddenControlsDiv.appendChild(this._buildInputElement('BBOX', bboxString));
			this._hiddenControlsDiv.appendChild(this._buildInputElement('WIDTH', '1200'));
			this._hiddenControlsDiv.appendChild(this._buildInputElement('HEIGHT', '900'));
			
			
			// for now hiding the invalid target attribute on the form
			// could possibly replace this with some javascript
			this._form.setAttribute("target", "_blank");

			this._form.submit();
		}
		
	},
	
	_buildLayerInputs: function (ind, layer) {
		var div = document.createElement('div');
		div.appendChild(this._buildInputElement(ind + '_ENDPOINT', layer.url));
		for (var p in layer.params) {
			div.appendChild(this._buildInputElement(ind + '_' + p, layer.params[p]));
		}
		return div;
	},
	
	_buildInputElement: function (name, value) {
		var input = document.createElement('input');
		input.type = "hidden";
		input.name = name;
		input.value = value;
		return input;
	},
	
	destroy: function () {
		if (this._handler !== null) {
			Utils.removeHTMLEventListener(this._button, 'click', this._handler);
		}
	}

};