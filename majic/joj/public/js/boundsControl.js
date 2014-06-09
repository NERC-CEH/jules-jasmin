"use strict";

/*jslint onevar: false*/

/**
 * Control to display the map coordinate inputs + update these and respond to inputs
 * @class
 *
 * @requires OpenLayers/Events.js
 * @requires OpenLayers/Bounds.js
 *
 * @author C Byrom
 */

/*globals WMSC: false, document: false, Utils: false, alert: false, OpenLayers: false
          $: false,*/

WMSC.BoundsControl = OpenLayers.Class(
{
    EVENT_TYPES: ['clearSelection', 'TEXT_SELECTION_CHANGED'],
    
    GLOBAL_BOUNDS: new OpenLayers.Bounds(-180.0, -90.0, 180.0, 90.0),

    // The WMS domain and layer parameters of the current selection
    wmsParams: null,
    clearButtonID: 'WMSC_clear',
    setButtonID: 'WMSC_set_bounds',
    formID: 'coordsForm',

    controlMarkup: '<div id="WMSC_sel" class="WMSC_domain">' +
      '<table>' +
      '  <tr><td colspan="2"' +
          '          align="center">' +
          '    <input type="text" name="bboxN" size="4" value="90"/><br/>N' +
          '  </td></tr>' +
      '  <tr>' +
      '   <td><input type="text" name="bboxW" size="4" value="-180"/> W</td>' +
      '   <td>E <input type="text" name="bboxE" size="4" value="180"/></td>' +
      '  </tr>' +
      '  <tr><td colspan="2" align="center">S<br/>' +
          '    <input type="text" name="bboxS" size="4" value="-90"/>' +
          '  </td></tr>' +
      '</table>' +
      '<input id="WMSC_clear" type="button" value="Reset selection"/>' +
      '</div>',

    
    /**
     * Constructor to create dimensionControl object
     *
     * @param domainDivID - ID of div element to use for domain control
     * @param formID - ID of form which features the coordinate selection control
     * @controlMarkup - HTML defining the coordinate selection control; NB, if this
     *    is not set, a default markup is used
     */
    initialize: function (domainDivID, initialBounds, eventsManager, controlMarkup) 
    {
         
        this._input_names = ['bboxN', 'bboxW', 'bboxE', 'bboxS'];
        this._supressTextChangeEvent = false;
        this.domainDivID = domainDivID;

        if (typeof(controlMarkup) !== 'undefined') {
            this.controlMarkup = controlMarkup;
        }
        this.eventsManager = eventsManager;
        
        this.wmsParams = {};

        // store of the selected dimensions; not used currently, but useful if we're producing output data
        this._selectedDims = {};
        
        this._lastSelection = null;
        
        this._initDomainDiv();
        
        if (initialBounds !== null) {
            this.setSelection(initialBounds);
        }
        else {
            this.setSelection(this.GLOBAL_BOUNDS);
        }
        
        this.eventsManager.register('MAP_SELECTION_CHANGED', this, this._onMapSelectionChanged);
    },

    /**
     * Clean up object
     * - important for IE.
     */
    destroy: function () 
    {
    },

    /**
     * Listener to trigger a change selection event
     */
    _selectionListener: function () 
    {
        var selection = this.getSelection();
        WMSC.log("triggering TEXT_SELECTION_CHANGED, selection = " + selection);
        
        if (this._supressTextChangeEvent === false) {
            this.eventsManager.triggerEvent('TEXT_SELECTION_CHANGED', {selection: selection});
        }
        
        // the this._supressTextChangeEvent is used to prevent this being picked 
        // up by the map control right after it raise the MAP_SELECTION_CHANGED event 
    },
    
    /**
     * Set the div with the coord data up 
     * - including specifying event listeners and handlers
     */
    _initDomainDiv: function () 
    {
        var domainDiv = document.getElementById(this.domainDivID);
        if (this.controlMarkup !== null) {
            domainDiv.innerHTML = this.controlMarkup;
        }

        this.selectionForm = $(this.formID);
        var inputElements = this._getInputElements();

        // NB, not all controls may have a clear button
        var clearButton = $(this.clearButtonID);
        if (clearButton) {
            clearButton.onclick = this._clearSelection.bindAsEventListener(this);
        }

        // If there is a set button, use this otherwise define onchange listeners for the input fields.
        var setButton = $(this.setButtonID);
        var listener = this._selectionListener.bindAsEventListener(this);
        if (setButton) {
            setButton.onclick = listener;
        } else {
            for (var i = 0; i < inputElements.length; i++) {
                inputElements[i].onchange = listener;
            }
        }

        
    },
    
    _getInputElements: function () {
        var domainDiv = document.getElementById(this.domainDivID);
        
        var inputElements = [];
        
        if (domainDiv) {
            for (var i = 0; i < this._input_names.length; i++) {
                var foundElements = Utils.getContainedElementsByName(domainDiv, this._input_names[i]);

                if (foundElements.length === 0 || foundElements[0] === null || foundElements[0].tagName !== 'INPUT') {
                    throw "Required input element " + this._input_names[i] + " not found in BoundsControl.";
                }

                inputElements.push(foundElements[0]);
            }
        }
        
        return inputElements;  
    },
    
    
    /**
     * Reset displayed coords to full global bounds
     */
    _clearSelection: function () 
    {
        this.eventsManager.triggerEvent('clearSelection');
    },
    
    /*
     * Retrieve selected coord data
     */
    getSelection: function () 
    {
        var inputElements = this._getInputElements();        
        var left, top, right, bottom;
        for (var i = 0; i < inputElements.length; i++) {
            var elt = inputElements[i];
            if (elt.name === 'bboxW') {
                left = elt.value;
            }
            else if (elt.name === 'bboxS') {
                bottom = elt.value;
            }
            else if (elt.name === 'bboxE') {
                right = elt.value;
            }
            else if (elt.name === 'bboxN') {
                top = elt.value;
            }
        }
        
        return new OpenLayers.Bounds(left, bottom, right, top);
    },
        
    /**
     * Update displayed coordinate selection - mapping to the
     * bounding box displayed in the map layer
     * NB, data is validated, to flip negative area selections, before being set
     *
     * @param bbox - openlayers bounds object
     */
    setSelection: function (bbox) 
    {
        //alert("Set selection bbox="+ bbox + " noCascade = " + noCascade);
        var old_b = this.getSelection();

        // Validation.  negative tests required to catch NaN
        if (!(bbox.left >= -180.0 && bbox.left < 180.0)) {
            bbox.left = old_b.left;
        }
        if (!(bbox.right > -180.0 && bbox.right <= 180.0)) {
            bbox.right = old_b.right;
        }
        if (!(bbox.top > -90.0 && bbox.top <= 90.0)) {
            bbox.top = old_b.top;
        }
        if (!(bbox.bottom >= -90.0 && bbox.bottom < 90.0)) {
            bbox.bottom = old_b.bottom;
        }
        
        var t;
        if (bbox.left > bbox.right) 
        {
            t = bbox.left; 
            bbox.left = bbox.right; 
            bbox.right = t;
        }
    
        if (bbox.bottom > bbox.top) 
        {
            t = bbox.bottom; 
            bbox.bottom = bbox.top; 
            bbox.top = t;
        }
        
        var inputElements = this._getInputElements();
        
        for (var i = 0; i < inputElements.length; i++) {
            var elt = inputElements[i];
            if (elt.name === 'bboxW') {
                elt.value = bbox.left.toFixed(1);
            }
            else if (elt.name === 'bboxS') {
                elt.value = bbox.bottom.toFixed(1);
            }
            else if (elt.name === 'bboxE') {
                elt.value = bbox.right.toFixed(1);
            }
            else if (elt.name === 'bboxN') {
                elt.value = bbox.top.toFixed(1);
            }
        }
        
    },
    
    /**
     * When the selection on the map has changed update the bounds controls.
     * 
     * It is worth noting that the flag _supressTextChangeEvent is used to stop the 
     * text change event from fireing while re-setting the bounds.
     */
    _onMapSelectionChanged: function (e) {
        this._supressTextChangeEvent = true;
        this.setSelection(e.selection);
        this._supressTextChangeEvent = false;
    }
});

