"use strict";

/*jslint onevar: false*/

/**
 * A bounding box
 *  
 * @param mapContainerId     - the container for the openlayers map
 * @param controlContainerId - the container for the bounds control.  
 * @param inputElementId     - the input element that the bbox value will be set in, 
 *     if set to null will be ignored
 * @param stringContainerId  - the container for the map selection string to display,
 *     the value to the user, if set to null will be ignored
 * @param boundsMarkup      - a html string that sets the markup for the text bounds,
 *                            selection. Must include 4 input elements with names 
 *                            'bboxN','bboxE','bboxS','bboxW'. 
 */
var BoundingBoxMapSelect= function (mapContainerId, controlContainerId, baseLayerData, inputElementId, stringContainerId, backgroundImage, boundsMarkup) {
    
    this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);          
    
    this.mapContainerId = mapContainerId;
    this.stringContainerId = stringContainerId;
    this.inputElementId = inputElementId;
    this.controlContainerId = controlContainerId;
    this.backgroundImage = backgroundImage;
    
    this._bbox = new OpenLayers.Bounds(-180.0, -90.0, 180.0, 90.0);
    
    if (this.inputElementId !== null) {
        
        var inputValue = document.getElementById(this.inputElementId).value;
        
        if (inputValue !== null && inputValue !== '') {
            // if the bbox input has a value attempt to use it to set the 
            // inital bounds on the map
            this._bbox = this._getBoundsFromString(inputValue);
        }
    }
    
    if (boundsMarkup) {
        this.boundsMarkup = boundsMarkup;
    }
    
    this._buildMap(baseLayerData);
    this._buildBoundsControl();
    this._updateBBoxString();
    
    this.events.register('TEXT_SELECTION_CHANGED', this, this._boundsTextChanged);
    this.events.register('clearSelection', this, this._resetMapSelection);
        
};

BoundingBoxMapSelect.prototype = {

    EVENT_TYPES: ['MAP_SELECTION_CHANGED', 'TEXT_SELECTION_CHANGED', 'clearSelection'],        

    boundsMarkup : '<div id="bbox_sel_bounds_container" class="WMSC_domain">\n' +
    '<div class="input_item"> \n<label for="bboxN">North :</label>\n' + 
    '<input type="text" name="bboxN" id="bboxN" size="4" value="90"> </input>\n </div>\n' +
    '<div class="input_item"> <label for="bboxW">West  : </label>\n' + 
    '<input type="text" name="bboxW" size="4" value="-180" />\n </div>\n' +
    '<div class="input_item"> <label for="bboxS">South : </label>\n' + 
    '<input type="text" name="bboxS" size="4" value="180"> </input>\n </div>\n' +
    '<div class="input_item"> <label for="bboxE">East  : </label>\n' + 
    '<input type="text" name="bboxE" size="4" value="-90"> </input>\n </div>\n ' +
    '<input id="WMSC_clear" type="button" value="Reset selection"/>' +
    '</div>\n',
    
    _buildMap: function (baseLayerData) {
        // couldn't get the sub-selection to work with the default controls
        this.map = new OpenLayers.Map(this.mapContainerId, {controls:[]});
    
        this.map.addControl(new OpenLayers.Control.PanZoomBar());
        this.map.addControl(new OpenLayers.Control.MousePosition());
    
        // use a transparent baselayer if there are none specified
        if (baseLayerData === null) {
            var baseLayer =  new OpenLayers.Layer.Image(
                    "None",
                    this.backgroundImage,
                    new OpenLayers.Bounds(-180, -90, 180, 90),
                    new OpenLayers.Size(8, 8),
                    { isBaseLayer: true, maxResolution:"auto", numZoomLevels:5}
                );
            
            this.map.addLayer(baseLayer);
        }
        else {
            
            // if the baseLayerData doesn't look like an array assume there is only
            // one layer specified.
            if (baseLayerData.constructor !== Array) {
                baseLayerData = [baseLayerData];
            }
            
            for (i = 0; i < baseLayerData.length; i++) {
                layerData = baseLayerData[i];
                
                //this is the 'real' baselayer, the others are just for decoration
                if (i === 0) {
                    layerData.params.transparent = 'false';
                    
                    var layer = new OpenLayers.Layer.WMS(
                            "BaseLayer_" + i,
                            layerData.url,
                            layerData.params,
                            { isBaseLayer: true, maxResolution:"auto", numZoomLevels:5}
                    );
                    var baseLayer = layer;
                }
                else {
                    var layer = new OpenLayers.Layer.WMS(
                            "BaseLayer_" + i,
                            layerData.url,
                            layerData.params,
                            {maxResolution:"auto", numZoomLevels:5}
                    );
                }

                this.map.addLayer(layer);
                                          
            }
            
        }
        
        this.map.zoomToMaxExtent();
        
        var boxesLayer = new OpenLayers.Layer.Boxes("Sub-selection");
        
        this.subselControl = new SubSelectionMouseToolbar(
                new OpenLayers.Pixel(this.map.size.w - 40, 10), 
                'vertical', 
                boxesLayer);
        
        this.map.addControl(this.subselControl);
        
        this.map.addLayer(boxesLayer);
    
        this.map.setLayerIndex(baseLayer, 0);
        this.map.setLayerIndex(boxesLayer, 1);
        
        this.subselControl.switchModeTo('zoombox');
        
        // move to the default bounds
        this.map.zoomToExtent(this._bbox);
        
        // if the extent doesn't fit the old bounds exactly then they must
        // have been selected using the subsel control.
        var extent = this.map.getExtent();
        var roundedExtent = new OpenLayers.Bounds(extent.left.toFixed(1), extent.bottom.toFixed(1), extent.right.toFixed(1), extent.top.toFixed(1));
        
        if (! roundedExtent.equals(this._bbox)) {
            this.subselControl.setSubSel(this._bbox);
        }
        
        this.map.events.register('moveend', this, this._mapMoved);
    },
    
    /**
     * Build the bounds control using the markup in this.boundsMarkup
     */
    _buildBoundsControl: function () {
        this.boundsControl = new WMSC.BoundsControl(this.controlContainerId, this._bbox, this.events, this.boundsMarkup);
    },
    
    /**
     * Get the bbox string from the bounds control inputs
     */
    _getBBoxString: function () {
        return this._bbox.left.toFixed(1) + "," + this._bbox.bottom.toFixed(1) + "," + this._bbox.right.toFixed(1) + "," + this._bbox.top.toFixed(1);
    },
    
    /**
     * Update the string container or the input element with the new bounds string,
     * does nothing if both of these are undefined.
     */
    _updateBBoxString: function () {
        
        var bboxString = this._getBBoxString();
        
        if (this.stringContainerId) {
            var container = document.getElementById(this.stringContainerId);
            container.innerHTML = bboxString;
        }
        
        if (this.inputElementId) {
            var inputElt = document.getElementById(this.inputElementId);
            inputElt.value = bboxString;
        }
    },
    
    /**
     * The map has moved, need to trigger the MAP_SELECTION_CHANGED event with the new
     * bounds. The MAP_SELECTION_CHANGED is listened for by the boundsControl which
     * should update to reflect the new active bouds.
     */
    _mapMoved: function () {
        this._bbox = this.subselControl.getActiveBounds();
        this.events.triggerEvent('MAP_SELECTION_CHANGED', {selection: this._bbox });
        this._updateBBoxString();
        
        var center = this.map.getCenter();
        var zoom = this.map.getZoom();
        WMSC.log("Center = " + center + " zoom = " + zoom);
    },
    
    /**
     * The selected bounds in the bounds control have changed, need to update
     * the map.
     */
    _boundsTextChanged: function (e) {
        this._bbox = e.selection;
        this.subselControl.setSubSel(this._bbox);
        this._updateBBoxString();
    },
    
    /**
     * The reset button has been pressed, zoom the map to the max extent
     */
    _resetMapSelection: function () {
        this.subselControl.deactivateSubsel();
        // this will trigger the MAP_SELECTION_CHANGED event
        this.map.zoomToExtent(this.map.maxExtent);
        this._bbox = this.map.maxExtent;
        this._updateBBoxString();
    },
    
    /**
     * Takes a comma spearated bounds string (w,s,e,n) and returns an OpenLayers.Bounds object.
     */
    _getBoundsFromString: function (boundsString) {
        var splitResult = boundsString.split(',');
        var west = splitResult[0];
        var south = splitResult[1];
        var east = splitResult[2];
        var north = splitResult[3];
        return new OpenLayers.Bounds(west, south, east, north);
    },
    
    dispose: function () {
        this.events.destroy();
    }
};