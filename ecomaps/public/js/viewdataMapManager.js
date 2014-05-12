/** 
 * Manages the map control, encapsulating interaction with Open Layers.
 * @class
 *
 * @requires OpenLayers/Events.js
 * 
 * @author R. Wilkinson
 */

/**
 * Constructor to initialise map controls.
 * @constructor
 *
 * @param eventsManager - event manager
*/
function ViewdataMapManager(eventsManager, mapPlaceholderId, loadErrors) {
    this.eventsManager = eventsManager;
    this.mapPlaceholderId = mapPlaceholderId;
    this.loadErrors = loadErrors;
    this.numZoomLevels = 10;
    this.layerIds = [];
    this.layerVisibilities = [];
    this.openLayersLayers = {};
    this.openLayersIdIndex = 0;
    this.resolutions = [];
    this.OUTLINE_LAYER_ID = 'll:outline';
    this.WMS_LAYER_OPTIONS = {isBaseLayer: false, buffer: 0};
    // Parameters to be excluded in makeLayerParameters - use to prevent OpenLayers cache avoidance
    // parameter being included in export files:
    this.EXCLUDED_LAYER_PARAMS = {'_OLSALT': true};

    /**
     * Creates the map window and controls.
     * @param initialStatus - initial status data for the map
     * @param mapElement - DOM element that is the map placeholder to be replaced by the map
     */
    this.createControls = function(initialStatus, initialBounds) {

        var bgImagePath = '../layout/images/clear.gif';

        this.defaultOptionsList = initialStatus.DefaultLayerParms;

        // Find the parent of the map placeholder element; it will be replaced by the real map. Remove the placeholder.
        var mapElement = document.getElementById(this.mapPlaceholderId);
        if (!this.parent) {
            var parentId = mapElement.parentNode.id;
            this.parent = mapElement.parentNode;
        }
        this.parent.removeChild(mapElement);

        // Create the map control.
        var mouseToolbarPosition =  new OpenLayers.Pixel(45, 4);
        var mouseToolbarPosition =  new OpenLayers.Pixel(63, 4);
        var panZoomPosition =  new OpenLayers.Pixel(4, 25);
        this.initialBounds = initialBounds;
        var displayWidth = this.getDisplayWidth(initialBounds, this.elWidth, this.elHeight);
        var mapOptions = initialStatus.MapOptions;
        if (mapOptions.numberZoomLevels) {
            this.numZoomLevels = mapOptions.numberZoomLevels;
        }

        this.visApp = new WMSC.VisApp(this.parent.id, this.numZoomLevels, displayWidth, true, initialBounds,
                                      this.eventsManager, bgImagePath,
                                      {mouseToolbarPosition: mouseToolbarPosition, mouseToolbarOrientation: 'horizontal',
                                       panZoomPosition: panZoomPosition, featureInfoTool: true,
                                       tileSize: mapOptions.tilesize, loadErrors: this.loadErrors});

        // Register handlers for layer changes.
        this.eventsManager.register('DRAW_LAYERS', this, this.onDrawLayers);
        this.eventsManager.register('LAYER_ADDED', this, this.onLayerAdded);
        this.eventsManager.register('LAYER_REMOVED', this, this.onLayerRemoved);
        this.eventsManager.register('LAYER_SELECTED', this, this.onLayerSelected);
        this.eventsManager.register('LAYER_LIST_REORDERED', this, this.onLayerListReordered);
        this.eventsManager.register('LAYER_DIMENSION_CHANGED', this, this.onLayerParameterChanged);
        this.eventsManager.register('LAYER_DISPLAY_CHANGED', this, this.onLayerParameterChanged);
    };

    this.addOutlineLayer = function(initialStatus) {
        // Create the default outline layer.
        var outlineSettings = initialStatus.OutlineSettings
        var outlineUrl = 'http://labs.metacarta.com/wms/vmap0';
        var outlineParams = {'layers': 'coastline_01', 'format': 'image/png'};
        if (outlineSettings['url'] !== undefined) {
            outlineUrl = outlineSettings['url'];
        }
        if (outlineSettings['params'] !== undefined) {
            outlineParams = outlineSettings['params'];
        }
        var newOutlineLayer = new OpenLayers.Layer.WMS(
            'Outline',
            outlineUrl,
            outlineParams,
            {isBaseLayer: false, buffer: 1});
        
        // Must set these parameters or the map will not draw.
        newOutlineLayer.params.CRS = 'CRS:84';
        newOutlineLayer.params.FORMAT = 'image/png';
        if (newOutlineLayer.params['VERSION'] == undefined){
            newOutlineLayer.params.VERSION = '1.3.0';
        }        
        newOutlineLayer.params.TRANSPARENT = 'TRUE';

        // Can't use the default id as there is already an element with that id on the page.
        newOutlineLayer.id = "outline_layer"; 

        this.openLayersLayers[this.OUTLINE_LAYER_ID] = newOutlineLayer;

        // Store the properties of the layer. 'layerData' is a placeholder that won't be used
        // because the OpenLayers layer is created above and never recreated (because of the
        // 'preconfigured' property).
        viewdataLayerData.setProperty(this.OUTLINE_LAYER_ID, 'layerData',
        {
            id: this.OUTLINE_LAYER_ID,
            title: "Outline",
            name: "default_outline",
            abstract: "Default outline layer",
            getCapabilitiesUrl: "",
            getMapUrl: outlineUrl,
            wmsVersion: newOutlineLayer.params.VERSION,
            styles: [],
            dimensions: []
        });
        viewdataLayerData.setProperty(this.OUTLINE_LAYER_ID, 'preconfigured', true);
        viewdataLayerData.setProperty(this.OUTLINE_LAYER_ID, 'stickyAtTop', true);
    };

    /**
     * Handler for draw layers event.
     * Raises an event to draw the layers in their current order.
     * @param e - event
     */
    this.onDrawLayers = function(e) {
        eventsManager.triggerEvent("LAYER_ORDER_CHANGED", {layers: this.getOpenLayerLayersInOrder()});
    };

    /**
     * Handler for new layer event. Creates an OpenLayers layer using the parameters in the layer
     * data.
     * @param e - event {id, layerData}
     */
    this.onLayerAdded = function(e) {
        if (viewdataLayerData.getProperty(e.id, 'preconfigured')) {
            // Layer is preconfigured so don't need to create it.
            return;
        }

        var getMapUrl = e.layerData['getMapUrl'];
        var layerName = e.layerData['name']
        var wmsVersion = e.layerData['wmsVersion']

        var globalDefaultParams = {
            format: 'image/png',
            version: '1.3.0',
            CRS: 'CRS:84',
            transparent: 'TRUE'
        };
        if (wmsVersion) {
            globalDefaultParams.version = wmsVersion;
        }

        this.defaultSetter = new LayerDefaultSetter(globalDefaultParams, this.defaultOptionsList);
        var defaultParams = this.defaultSetter.getDefaults(getMapUrl, layerName);

        var layer = new OpenLayers.Layer.WMS("#" + this.openLayersIdIndex + " " + layerName, 
                                             getMapUrl, defaultParams, this.WMS_LAYER_OPTIONS);

        layer.params['LAYERS'] = layerName;
        layer.id = getMapUrl + "_" + layer.name + "_" + this.openLayersIdIndex;

        this.openLayersLayers[e.id] = layer;

        this.openLayersIdIndex += 1;
    };

    /**
     * Handler for layer removed event.
     * @param layerId - id of removed layer
     */
    this.onLayerRemoved = function(layerId) {
        if (!viewdataLayerData.getProperty(layerId, 'preconfigured')) {
            delete this.openLayersLayers[layerId];
        }
    };

    /**
     * Handler for layer selected event. Triggers a specified event holding layer data.
     * @param e - event data {id, layerData, eventToPropagate}
     */
    this.onLayerSelected = function(e) {
        if (e.id == null) {
            eventsManager.triggerEvent(e.eventToPropagate, {id: null,
                                                            layerData: e.layerData,
                                                            olLayer: null});
        } else {
            this.selectedLayerData = e.layerData;
            this.selectedOpenLayersLayer = this.openLayersLayers[e.id];

            if(this.selectedOpenLayersLayer){
                eventsManager.triggerEvent(e.eventToPropagate, {id: e.id,
                                                                layerData: e.layerData,
                                                                olLayer: this.selectedOpenLayersLayer});
            }
        }
    };

    /**
     * Handler for layers reordered event.
     * @param layerIds - node IDs and visibilities of layers
     */
    this.onLayerListReordered = function(layerIds) {
        this.layerIds = [];
        this.layerVisibilities = [];
        for (var i = 0; i < layerIds.length; ++i) {
            this.layerIds.push(layerIds[i].id);
            this.layerVisibilities.push(layerIds[i].display);
        }
        eventsManager.triggerEvent("LAYER_ORDER_CHANGED", {layers: this.getOpenLayerLayersInOrder()});
    };

    /**
     * Handler for change event for some change of layer parameter.
     * Sets the parameter value for the selected layer and redraws it.
     * @param e - event data {param, value}
     */
    this.onLayerParameterChanged = function(e) {
        if (this.selectedOpenLayersLayer !== null) {
            this.selectedOpenLayersLayer.params[e.param.toUpperCase()] = e.value;
            this.selectedOpenLayersLayer.redraw();
        }

        this.eventsManager.triggerEvent("LAYER_PROPERTY_CHANGED",
                {layer: this.selectedOpenLayersLayer, layerData: this.selectedLayerData});

        if (e.param.toUpperCase() === 'STYLES') {
            this.eventsManager.triggerEvent("LAYER_STYLE_CHANGED",
                    {style: e.value});
        }
    };

    /**
     * Forms an array of OpenLayers layers in the order of the layers in the layer list.
     * @return array of OpenLayers Layer
     */
    this.getOpenLayerLayersInOrder = function() {
        var olLayers = [];
        for (var i = 0; i < this.layerIds.length; ++i) {

            if(this.openLayersLayers[this.layerIds[i]]) {
                this.openLayersLayers[this.layerIds[i]].visibility = this.layerVisibilities[i];
                olLayers.push(this.openLayersLayers[this.layerIds[i]]);
            }
        }
        return olLayers;
    };

    /**
     * Forms an array of objects containing the parameters for the layers in the order of the layers in the layer list.
     * @return array of objects {name, value}
     */
    this.makeLayerParameters = function(oneLayerOnly) {
        var retValues = [];
        var layerNumber = 1;
        var numNonOutlineLayers = 0;
        for (var i = 0; i < this.layerIds.length; ++i) {
            if (this.layerVisibilities[i]) {
                var layer = this.openLayersLayers[this.layerIds[i]];

                if(layer != null){
                    var layerData = viewdataLayerData.getProperty(this.layerIds[i], 'layerData');
                    var paramName = layerNumber + '_ENDPOINT';
                    retValues.push({name: paramName, value: layer.url});
                    for (var p in layer.params) {
                        if (!this.EXCLUDED_LAYER_PARAMS[p]) {
                            paramName = layerNumber + '_' + p;
                            retValues.push({name: paramName, value: layer.params[p]});
                        }
                    }
                    paramName = layerNumber + '_LAYER_ID';
                    retValues.push({name: paramName, value: this.layerIds[i]});
                }

                ++layerNumber;

                // Check whether to stop because only one non-outline layer is to be included.
                if (this.layerIds[i] != this.OUTLINE_LAYER_ID) {
                    numNonOutlineLayers += 1;
                }
                if (oneLayerOnly && numNonOutlineLayers > 0) {
                    break;
                }
            }
        }
        return retValues;
    };

    /**
     * Forms an array of objects containing the parameters for the layers in the order of the layers in the layer list.
     * @param layerId - layer id
     * @return array of objects {name, value}
     */
    this.makeParametersForLayer = function(layerId) {
        var retValues = [];
        var layer = this.openLayersLayers[layerId];
        var layerData = viewdataLayerData.getProperty(layerId, 'layerData');
        retValues.push({name: 'ENDPOINT', value: layer.url});
        for (var paramName in layer.params) {
            if (!this.EXCLUDED_LAYER_PARAMS[paramName]) {
                retValues.push({name: paramName, value: layer.params[paramName]});
            }
        }
        retValues.push({name: 'LAYER_ID', value: layerId});
        return retValues;
    };

    /**
     * Finds the layer number as used in makeLayerParameters for the layer of a specified ID.
     * @param id - layer ID
     * @return number of corresponding layer starting with 1 as the top layer, or 0 if ID not found
     */
    this.getLayerNumberById = function(id) {
        var layerNumber = 1;
        for (var i = 0; i < this.layerIds.length; ++i) {
            if (this.layerVisibilities[i]) {
                if (this.layerIds[i] === id) {
                    return layerNumber;
                }
                ++layerNumber;
            }
        }
        return 0;
    }

    /**
     * Handler for afterlayout ExtJS event for the map component.
     * @param cmp - map containing component
     */
    this.onAfterLayout = function(cmp) {
        if (!this.parent) {
            var mapElement = document.getElementById(this.mapPlaceholderId);
            this.parent = mapElement.parentNode;
        }
        WMSC.log("resize: " + this.parent.clientWidth + "," + this.parent.clientHeight);

        this.elHeight = this.parent.clientHeight;
        this.elWidth = this.parent.clientWidth;

        if (this.visApp) {
            var zoom = this.visApp.map.getZoom();
            var center = this.visApp.map.getCenter();
            var activeBounds = this.visApp.subselControl.getActiveBounds();

            var options = this.getMapOptions(this.initialBounds, this.numZoomLevels, this.elWidth, this.elHeight);
            this.visApp.map.setOptions(options);
            var resolutions = options.resolutions;
            for (var i = 0; i < this.visApp.map.layers.length; i++) {
                this.visApp.map.layers[i].resolutions = resolutions;
            }

            // Recenter if necessary to move the selection within view.
            center = this.getCenterToEnsureSelectionWithinView(center, zoom, resolutions, activeBounds,
                                                               this.elWidth, this.elHeight);

            this.visApp.map.updateSize();
            this.visApp.map.setCenter(center, zoom);

            this.visApp.drawLayers(this.getOpenLayerLayersInOrder());
        }
    };

    /**
     * Calculates a center that is either the current value or one modified if necessary to move the current selection into view.
     * @param center - OpenLayers.LonLat containing current center of map
     * @param zoom - current zoom level
     * @param resolutions - array of resolutions for each zoom level
     * @param selection - object containing current selection bounds
     * @param elWidth - width of element containing the map
     * @param elHeight - height of element containing the map
     * @return OpenLayers.LonLat containing new center
     */
    this.getCenterToEnsureSelectionWithinView = function(center, zoom, resolutions, selection, elWidth, elHeight) {
        var res = resolutions[zoom];
        var coordWidth = elWidth * res;
        var coordHeight = elHeight * res;
        var newCenter = new OpenLayers.LonLat(center.lon, center.lat);

        var coordTop = center.lat + coordHeight / 2.0;
        var coordBottom = center.lat - coordHeight / 2.0;
        var coordLeft = center.lon - coordWidth / 2.0;
        var coordRight = center.lon + coordWidth / 2.0;

        if (selection.left < coordLeft) {
            newCenter.lon -= coordLeft - selection.left;
        } else if (selection.right > coordRight) {
            newCenter.lon += selection.right - coordRight;
        }

        if (selection.bottom < coordBottom) {
            newCenter.lat -= coordBottom - selection.bottom;
        } else if (selection.top > coordTop) {
            newCenter.lat += selection.top - coordTop;
        }

        return newCenter;
    };

    /**
     * Calculates the options to pass to an Open Layers map.
     * @param initialBounds - boundary of unzoomed map in map coordinates
     * @param numZoomLevels - number of zoom levels
     * @param elWidth - width of element containing the map
     * @param elHeight - height of element containing the map
     * @return object containing the options
     */
    this.getMapOptions = function(initialBounds, numZoomLevels, elWidth, elHeight) {
        var mapWidth = initialBounds.getWidth();
        var mapHeight = initialBounds.getHeight();
        if ((mapWidth / mapHeight) > (elWidth / elHeight)) {
            var maxResolution = mapWidth / elWidth;
        } else {
            var maxResolution = mapHeight / elHeight;
        }
        var resolutions = [];
        for (var i = 0; i < numZoomLevels; i++) {
            resolutions.push(maxResolution / Math.pow(2.0, i / 2.0));
        }

        return {
            maxResolution: maxResolution,
            resolutions: resolutions,
            numZoomLevels: numZoomLevels
        }
    };

    /**
     * Calculates the options to pass to an Open Layers map.
     * @param initialBounds - boundary of unzoomed map in map coordinates
     * @param elWidth - width of element containing the map
     * @param elHeight - height of element containing the map
     * @return width of the map as it should be displayed
     */
    this.getDisplayWidth = function(initialBounds, elWidth, elHeight) {
        var mapWidth = initialBounds.getWidth();
        var mapHeight = initialBounds.getHeight();
        if ((mapWidth / mapHeight) > (elWidth / elHeight)) {
            var displayWidth = elWidth;
        } else {
            var displayWidth = elHeight * mapWidth / mapHeight;
        }
        return displayWidth;
    };
}
