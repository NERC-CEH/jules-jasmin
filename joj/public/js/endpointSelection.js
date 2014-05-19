"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, document: false, Utils: false*/

var EndpointSelection = function (containerId, endpointList, eventsManager) {
    this._container = document.getElementById(containerId);
    this.endpointList = endpointList;
    this.eventsManager = eventsManager;
    
    this._container.innerHTML = this.controlMarkup;
    
    // build the components
    this._select = this._buildSelect(endpointList);
    this._input = document.getElementById('new_endpoint_1');
    this._addButton = document.getElementById('new_endpoint_button');
    
    this._selectMethodRadio = document.getElementById('endpoint_select_method_select');
    this._inputMethodRadio = document.getElementById('endpoint_select_method_input');
    
    Utils.addHTMLEventListener(this._selectMethodRadio, 'click', this._onMethodRadioClick, this);
    Utils.addHTMLEventListener(this._inputMethodRadio, 'click', this._onMethodRadioClick, this);
    Utils.addHTMLEventListener(this._addButton, 'click', this._onAddButtonClick, this);
    
    // add them to the container
    this._selectContainer = document.getElementById('new_endpoint_select_container');
    this._selectContainer.appendChild(this._select);
    
    this._inputContainer = document.getElementById('new_endpoint_input_container');
    this._inputContainer.style.display = 'none';
    
    this._selectMethodRadio.checked = true;
    
};

EndpointSelection.prototype = {
        
    EVENT_TYPES: ["NEW_ENDPOINT"],
    
    controlMarkup: '\n' +
        '<div>\n' +
        '    <label for="endpoint_select_method_select"> Select Preset </label>\n' +
        '   <input type="radio" name="endpoint_select_method" value="select" \n' +
        '                  id="endpoint_select_method_select" ></input>\n' +
        '   <label for="endpoint_select_method_input"> Enter URL </label>\n' +
        '   <input type="radio" name="endpoint_select_method" value="input" \n' +
        '                   id="endpoint_select_method_input" ></input>\n' +
        '</div>\n' +
        '<div>\n' +
        '    <span id="new_endpoint_select_container"></span> \n' +
        '    <span id="new_endpoint_input_container"> \n' +
        '      <input id="new_endpoint_1" size="40" type="text" ></input> \n' +
        '    </span> \n' +
        '  <input type="button" id="new_endpoint_button" value="Add" /> \n' +
        '</div>\n',
               
        
    _buildSelect: function (endpointList) {    
        var descriptions = [];
        var values = [];
        
        for (var i = 0; i < endpointList.length; i++) {
            descriptions.push(endpointList[i].name);
            values.push(endpointList[i].url);
        }
                            
        return Utils.buildSelect("new_endpoint_2", "new_endpoint_2", descriptions, values);
        
    },
    
    _onAddButtonClick: function (e) {
        WMSC.log("Add endpoint clicked.");
        
        var url = null;
        if (this._selectMethodRadio.checked) {
            url = this._select.value;
        }
        else {
            url = this._input.value;
        }
        
        this.eventsManager.triggerEvent("NEW_ENDPOINT", {url: url}
        );
        
    },
    
    _onMethodRadioClick: function (e) {
        if (this._selectMethodRadio.checked) {
            if (this._selectContainer.style.display === 'none') {
                this._selectContainer.style.display = '';
                this._inputContainer.style.display = 'none';
            }
        }
        else {
            if (this._inputContainer.style.display === 'none') {
                this._inputContainer.style.display = '';
                this._selectContainer.style.display = 'none';
            }
        }
    }
};
    
 