"use strict";

/*jslint onevar: false*/

/** 
 *  Control to provide an OpenLayers map with default layers loaded and basic 
 *  functionality to display legend data, output figure plots and interface with
 *  dimension and layer controls.
 *  @class 
 *
 * @requires OpenLayers/Layer.js
 * @requires OpenLayers/Bounds.js
 *
 *  @author C Byrom
 */

/*global document:false, WMSC:false, Utils:false, OpenLayers:false,
  DDCVisMap:false, SubSelectionMouseToolbar:false, $:false, Ajax:false */

WMSC.VisApp = OpenLayers.Class(
{
    EVENT_TYPES: ['MAP_SELECTION_CHANGED'],
    
    /**
     * Constructor to set up object
     * @constructor
     * 
     * @param div - ID of div section to use for map control
     * @param numZoomLevels - number of zoom levels to allow in map
     * @param mapWidth - width of displayed map
     * @param showCoast - true - display coastline, otherwise not
     * @param initialBounds - OpenLayers.Bounds object containing initial bounds
     * @param eventsManager - OpenLayers.Events object - application event manager
     * @param bgImagePath - path of background image
     * @param options - configuration options - object with option properties: mouseToolbarPosition (type OpenLayers.Pixel),
     *        panZoomPosition (type OpenLayers.Pixel), tileSize (type Number), featureInfoTool (type Boolean)
     */
    initialize: function (div, numZoomLevels, mapWidth, showCoast, 
                          initialBounds, eventsManager, bgImagePath, options)
    {
        this.figureCounter = 1;
        this.showCoast = showCoast;

        this.eventsManager = eventsManager;   
        this.bgImagePath = bgImagePath;
        
        var mouseToolbarPosition = new OpenLayers.Pixel(mapWidth - 40, -290);
        var mouseToolbarOrientation = 'vertical';
        var panZoomPosition = new OpenLayers.Pixel(4, 4);
        var tileSize = 320
        var featureInfoTool = false;
        var loadErrors = null;
        if (options)
        {
            if (options['mouseToolbarPosition'])
            {
                mouseToolbarPosition = options['mouseToolbarPosition'];
            }
            if (options['mouseToolbarOrientation'])
            {
                mouseToolbarOrientation = options['mouseToolbarOrientation'];
            }
            if (options['panZoomPosition'])
            {
                panZoomPosition = options['panZoomPosition'];
            }
            if (options['tileSize'])
            {
                tileSize = options['tileSize'];
            }
            if (options['featureInfoTool'])
            {
                featureInfoTool = options['featureInfoTool'];
            }
            if (options['loadErrors'])
            {
                loadErrors = options['loadErrors'];
            }
        }

        // NB, can't override both numZoomLevels and minResolution with
        // the current OpenLayers code.  Instead calculate resolutions
        // directly.
        var maxResolution = 360.0 / mapWidth;
        var resolutions = [];
        for (var i = 0; i < numZoomLevels; i++) 
        {
            resolutions.push(maxResolution / Math.pow(1.4, i));
        }

        // set up the map control
        this.map = new DDCVisMap(div, 
            { 
                resolutions: resolutions,
                controls: [],
                tileSize: new OpenLayers.Size(tileSize, tileSize)
            }
        );
        
        
        this.boxesLayer = new OpenLayers.Layer.Boxes("Sub-selection");

        this.subselControl = new SubSelectionMouseToolbar(
            this.boxesLayer,
            {'featureInfoTool': featureInfoTool,
             'position': mouseToolbarPosition, 'orientation': mouseToolbarOrientation /* not used currently */}
        );
        this.subselControl.setFeatureInfoHandler(this, this.featureInfoHandler);
        
        this.map.addControl(new OpenLayers.Control.LoadingPanel());
        if (loadErrors) {
            this.map.addControl(loadErrors);
        }
        this.map.addControl(this.subselControl);
        this.map.addControl(new OpenLayers.Control.PanZoomBar({'position': panZoomPosition, 'zoomWorldIcon': true}));
        this.map.addControl(new OpenLayers.Control.MousePosition());

        this.map.events.register('moveend', this.subselControl, this.subselControl.checkSubselVisibility);
        this.map.events.register('zoomend', this.subselControl, this.subselControl.checkSubselVisibility);
        
        this.baseLayer =  new OpenLayers.Layer.Image(
                "None",
                this.bgImagePath,
                new OpenLayers.Bounds(-180, -90, 180, 90),
                new OpenLayers.Size(8, 8),
                {isBaseLayer: true,
                 resolutions: resolutions}
            );
                
        this.map.addLayer(this.baseLayer);
        this.map.setLayerIndex(this.baseLayer, 0);
        
        this.map.addLayer(this.boxesLayer);
        this.map.setLayerIndex(this.boxesLayer, 1);
        
        
//        // Setup the map - initially with the basic openlayers map + coastline + boxes
//        this.updateVisLayer();

        this.maxExtent = initialBounds;
        this.map.zoomToExtent(this.maxExtent);    
        
        this.map.zoom = 0;
        
        // force the resolution to be set, this is needed so that layers added
        // retain the correct bounds.
        this.map.resolution = this.map.getResolutionForZoom(this.map.zoom);
         
        WMSC.log("this.map resolution= " + this.map.getResolution() + 
                               " zoom=" + this.map.zoom + 
                               " maxExtent(b,l,t,r)=" + this.map.maxExtent.bottom + "," + this.map.maxExtent.left + "," + this.map.maxExtent.top + "," + this.map.maxExtent.right + 
                               " center(lat,lon)=" + this.map.getCenter().lat + "," + this.map.getCenter().lon + 
                               " size=" + this.map.getSize().w + "," + this.map.getSize().h + 
                               " bounds(b,l,t,r)=" + this.map.calculateBounds().bottom + "," + this.map.calculateBounds().left + "," + this.map.calculateBounds().top + "," + this.map.calculateBounds().right);
        
        // Enter selection mode
        this.subselControl.switchModeTo('zoombox');
        
        this._divId = div;
        
        this.eventsManager.register('TEXT_SELECTION_CHANGED', this, this.updateSelectionBox);
        this.eventsManager.register('clearSelection', this, this.resetMapCoords);
        this.eventsManager.register("LAYER_ORDER_CHANGED", this, this.onLayerOrderChanged);
        this.eventsManager.register("SET_FEATURE_INFO_CONFIG", this, this.onSetFeatureInfoConfig);
        this.eventsManager.register("LAYER_DIMENSION_CHANGED", this, this.onLayerDimensionChanged);
        this.eventsManager.register("REDRAW_LAYERS", this, this.onRedrawLayers);
        this.map.events.register('moveend', this, this.updateBoundsControl);
        this.map.events.register('zoomend', this, this.updateBoundsBoundsControl);        
    },
    
    _logLocation: function () {
        WMSC.log("map div location = " + Utils.findPos(document.getElementById(this._divId)));
        WMSC.log("dims location= " + Utils.findPos(document.getElementById('dims')));
    },
    
    updateBoundsBoundsControl: function (events) {
        WMSC.log("map zoomed -- this.map resolution = " + this.map.resolution + " zoom=" + this.map.zoom + " maxExtent: b=" + this.map.maxExtent.bottom + " l=" + this.map.maxExtent.left + " t=" + this.map.maxExtent.top + " r=" + this.map.maxExtent.right);
    },

    /**
     * Handles a layer order changed event - causes the layers to be redrawn in the new order.
     * @param e  event {e.layers}
     */
    onLayerOrderChanged: function (e) {
        this.drawLayers(e.layers);
    },

    /**
     * Forces a redraw of all the layers.
     */
    onRedrawLayers: function () {
        for (var i = 0; i < this.map.layers.length; i++) {
            // OpenLayers 2.11 and earlier:
            var layer = this.map.layers[i];
            if (layer.mergeNewParams) {
                WMSC.log("Adding salt parameter for " + this.map.layers[i].name);
                this.map.layers[i].mergeNewParams({"_olSalt": Math.random()});
            }
            // OpenLayers 2.12:
            // this.map.layers[i].redraw(true);
        }
    },

    /**
     * Sets the configuration for the feature info tool when a new layer has been selected.
     * @param e  event {olLayer, layerData, dimensions}
     */
    onSetFeatureInfoConfig: function (e) {
        if (e.layerData) {
            this.subselControl.setQueryLayer(e.olLayer, e.layerData.getMapUrl, e.layerData.getFeatureInfoUrl);
            for (var name in e.dimensions) {
                this.subselControl.setQueryDimension(name, e.dimensions[name]);
            }
        }
    },

    /**
     * Sets a dimension value for the feature info tool when its value has changed.
     * @param e  event {param, value}
     */
    onLayerDimensionChanged: function (e) {
        this.subselControl.setQueryDimension(e.param, e.value);
    },

    // Cleaning up is important for IE.
    destroy: function () 
    {
        
        if (this.dimControl) {
            this.dimControl.destroy();
        }

        if (this.layerControl) {
            this.layerControl.destroy();
        }
        
        this.subselControl.destroy();
    },

    /**
     * Set up coast layer using the specified layer name
     */
    _initCoast: function (layerName) 
    {
        // check if coast layer is loaded or if a different coast layer has been specified; reload, if so
        if (!this.coastLayer || this.coastLayer.params.LAYERS !== layerName) 
        {
            this.coastLayer = new OpenLayers.Layer.WMS("Coastline",
                       "http://labs.metacarta.com/wms/vmap0",
                       {layers: layerName, format: 'image/gif',
                        transparent: 'true'});
        }
        this.map.addLayer(this.coastLayer);
    },

    /**
     * Determine whether any layers have been added to the layerlist; if so, add these one by one
     * to the map
     * NB, the layers are initially removed to ensure they are not duplicated
     */
    updateVisLayer: function () 
    {
        
        // firstly, remove any existing layers
        var j = this.map.getNumLayers(); 
        var i = 0;
        for (i = 0; i < j; i++)
        {
            this.map.removeLayer(this.map.layers[0]);
        }
        
        // Setup an initial baselayer - NB, without this, the transparent layers will not display
        if (!this.visLayer)
        {
            this.visLayer = new OpenLayers.Layer.WMS(
                 "OpenLayers WMS",
                 "http://labs.metacarta.com/wms/vmap0",
                 {layers: 'basic', format: 'image/png'}
            );
            
            // add extra parameters, if specified by layer control
            this._mergeDimParams(this.visLayer);
        }
        
        this.map.addLayer(this.visLayer);
        
        // retrieve the elements of the layer list and add these to the map
        var layerList = document.getElementById("layerlist");

        if (layerList !== null) {
            //Changed by domlowe: reversed the order these layers are added to the map. Dragging and dropping the
            // layer you want to be on top to the bottom of the list was counter intuitive.
            //old code:
            //for (var i = 0; layerList && i < layerList.childNodes.length; i++)
            //now in revese order:
            for (i = layerList.childNodes.length - 1; layerList && i >= 0; i--)
            {
                var child = layerList.childNodes[i];
                
                // ignore any hidden list values
                if (child.className === "hiddenList") {
                    continue;
                }
                
                if (child.nodeName === "LI")
                {
                    // extract the required info and load the map
                    // NB, these values are set in the layerControl._updateLeafLayer() method
                    // NB, for transparancy to be fully supported, the format must be gif
                    // - png is only partially supported and jpg not at all
                    var endpoint = child.getAttribute("wmcURL");
                    var title = child.getAttribute("title");
                    var layerName = child.getAttribute("layerName");

                    var mapLayer = new OpenLayers.Layer.WMS(
                                title,
                                endpoint,
                                 {format: 'image/gif',
                                  version: '1.3.0', 
                                  CRS: 'CRS:84',
                                  layers: layerName,
                                  styles: '',
                                  transparent: 'true'
                                 });
                    
                    // add extra parameters, if specified by layer control
                    this._mergeDimParams(mapLayer);
                    this.map.addLayer(mapLayer);
                }
            }
        }
            
        // add the coast outline, if required
        if (this.showCoast) {
            this._initCoast('coastline_01');
        }

        // add layer to represent the subselection box on the layer        
        this.map.addLayer(this.boxesLayer);
        
        // if there is legend data available, display this under the map
        this.loadLegend();
    },
    
    /**
     * If a dimension control has been specified, check if this has any
     * additional params to use when setting up the map layer; add
     * these, if so
     */
    _mergeDimParams: function (mapLayer)
    {
        if (this.dimControl && this.dimControl.wmsParams)
        {
            mapLayer.mergeNewParams(this.dimControl.wmsParams);
        }
        mapLayer.setZIndex(300);
    },    

    /**
     * Reset the map to display the full global bounds - and update
     * the coordinate selections to reflect this
     */
    resetMapCoords: function () 
    {
        WMSC.log("resetMapCoords");
        this.subselControl.deactivateSubsel();
        this.map.zoomToExtent(this.maxExtent);
        this.updateBoundsControl();
    },

    /**
     * Check if a legend element is available; if so, check
     * if the topmost layer isn't a default one; if so, attempt
     * to load and display legend data for this layer
     */
    loadLegend: function () 
    {
        var legend = $('legend');
        if (!legend) {
            return;
        }
            
        var setLegend = function (xhr) 
        {
            $('legend').innerHTML = '';
            var legendHTML = xhr.responseText;
            if (legendHTML) {
                $('legend').innerHTML = legendHTML;
            }
        };

        var failure = function (xhr) 
        {
            //alert('Error: could not load legend data for the last selected layer.');
        };

        // set the legend to be the topmost layer that has been picked
        // NB, there are initially three layers - for the subselection box, coastline and base map
        // - so ignore legend if only three layers
        var layerNo = this.map.layers.length;
        if (layerNo < 4)
        {
            legend.innerHTML = '';
            return;
        }
            
        var topLayer = this.map.layers[layerNo - 3];
        
        if (topLayer.url === null) 
        {
            legend.innerHTML = '';
        }
        else 
        {
            var url = topLayer.getFullRequestString({
                REQUEST: 'GetLegend'//, FORMAT: 'text/html'
            });

            var params = {REQUEST: 'GetLegend', ENDPOINT: url};
            
            var req = new Ajax.Request('',
                {
                    parameters : params,
                    method : "get",
                    onSuccess : setLegend.bindAsEventListener(this),
                    onFailure : failure.bindAsEventListener(this)
                });
        }
    },

    
    /**
     * If an area has been selected on the map to zoom, update
     * the dimension selection control to reflect this change
     */
    updateBoundsControl: function () 
    {
        var b = this.subselControl.getActiveBounds();

        WMSC.log("triggering MAP_SELECTION_CHANGED, selection = " + b);
        this.eventsManager.triggerEvent('MAP_SELECTION_CHANGED', {selection: b});
    },

    /**
     * Update the selection box displayed on the map
     * - taking the values from the input coord control
     */
    updateSelectionBox: function (e) 
    {
        WMSC.log("started update selection box");
        
        var old_b = this.subselControl.getActiveBounds();
        var new_b = e.selection;
        
        // Validation.  negative tests required to catch NaN
        if (!(new_b.left >= -180.0 && new_b.left <= 180.0)) 
        {
            new_b.left = old_b.left;
        }
        if (!(new_b.right >= -180.0 && new_b.right <= 180.0)) 
        {
            new_b.right = old_b.right;
        }
        if (!(new_b.top >= -90.0 && new_b.top <= 90.0)) 
        {
            new_b.top = old_b.top;
        }
        if (!(new_b.bottom >= -90.0 && new_b.bottom <= 90.0)) 
        {
            new_b.bottom = old_b.bottom;
        }
        
        var t;
        
        if (new_b.left > new_b.right) 
        {
            t = new_b.left; 
            new_b.left = new_b.right; 
            new_b.right = t;
        }
        if (new_b.bottom > new_b.top) 
        {
            t = new_b.bottom; 
            new_b.bottom = new_b.top; 
            new_b.top = t;
        }
        
        // this command triggers the moveend map event.
        this.subselControl.setSubSel(new_b);
        WMSC.log("finished update selection box");
    },


    /**
     * Handles a layer order changed event - causes the layers to be redrawn in the new order.
     * @param layers  array of layers in order to be drawn
     */
    drawLayers: function (layers) {
        
        var i;
        
        //remove the old layers
        if (this.map.layers.length > 0) {
            
            var removeLayers = [];
            for (i = 0; i < this.map.layers.length; i++) {
                if (this.map.layers[i] !== this.baseLayer &&
                    this.map.layers[i] !== this.boxesLayer) {
                    removeLayers.push(this.map.layers[i]);
                }
            }
            
            for (i = 0; i < removeLayers.length; i++) {
                var layer = removeLayers[i];
                WMSC.log("Removing layer id=" + layer.id + " name=" + layer.name);
                this.map.removeLayer(layer);
            }
        }
        
        var lastLayerIndex = 1;
        if (layers.length > 0) {
            
            for (i = layers.length - 1; i >= 0; i--) {
                var l = layers[i];
                
                this.map.addLayer(l);
                this.map.setLayerIndex(l, lastLayerIndex);
                lastLayerIndex ++;
                WMSC.log("Added layer name=" + l.name + " index=" + this.map.getLayerIndex(l));
            }
        }

        //add the layer for the boxes to be drawn
        this.map.setLayerIndex(this.boxesLayer, lastLayerIndex);
        
    },
 
    /**
     * Handles a getfeatureinfo event from the WMSGetFeatureInfo tool.
     * Triggers a new FEATURE_INFO event available to the application.
     * @param e event to propagate {pixelPosition, info}
     */
    featureInfoHandler: function (e) {
        // Unwrap and decode the HTML response passed as XML element.
        var encodedInfo = e.text.replace(/^<FeatureInfo>/, '').replace(/<\/FeatureInfo>$/, '');
        var info = this.decodeXml(encodedInfo);
        
        this.eventsManager.triggerEvent('FEATURE_INFO',
                                        {pixelPosition: [e.xy.x, e.xy.y],
                                         info: info});
    },

    decodeXml: function (string) {
        var escaped_one_to_xml_special_map = {
            '&amp;': '&',
            '&quot;': '"',
            '&lt;': '<',
            '&gt;': '>'
        };

        return string.replace(/(&quot;|&lt;|&gt;|&amp;)/g,
                              function(str, item) {
                                  return escaped_one_to_xml_special_map[item];
                              });
    }
});
