/**
 * Created by Phil Jenkins (Tessella) on 2/25/14.
 *
 * Simplified map viewer suitable for the EcoMaps application
 *
 */

// Used to collapse or expand the model runs / datasets list
function expandCollapse() {
    $(this).parent().siblings('div').toggle();
    var icon = $(this).find('div.expand-icon');
    if (icon.text() == ' -')
    {
        icon.text(' +')
    } else {
        icon.text(' -')
    }
    return false;
}

/*
 * Select a tab and pane based on its id post-fix
 * name - post-fix of the name of the tab
 */
function selectTab(name) {
    $(".nav-tabs li").removeClass("active");
    $("#tab_" + name).addClass("active");
    $(".tab-pane").hide();
    $("#pane_" + name).show();
}

// Put the map variable here so we can use it for  graphing
var map = null;
var currentLayerIndex; // Need to access this when adding graphing layers

var EcomapsMap = (function() {

    // Module-level variables

    var layerDict = new Object();
    var defaultLayerOptions = {
        isBaseLayer: false,
        buffer: 0
    };

        // If the map page is called with a model run selected we need to expand
        // the selected model_run and then click it to show it on the map.
        function openSelectedRun()
        {
            var selected_id = $('#selected_id').text();
            if (selected_id) {
                var model_run_header = $("a.dataset-heading[data-model_run_id='" + selected_id + "']").filter('.model-run').first();
                model_run_header.click();
                var datasetHeaders = model_run_header.parent().siblings('div').find("a.dataset-heading");
                datasetHeaders.click();
                var outputDiv = datasetHeaders.filter('.output').parent().siblings('div');
                outputDiv.find('a.dataset').first().click();

                //find the pane of the first example of the selected model and select that tab
                var tab_name = datasetHeaders.parents('.tab-pane').first().prop('id')
                selectTab(tab_name.replace('pane_', ''));
            }
            else {
                var tab_name = $('.tab-pane').prop('id');
                selectTab(tab_name.replace('pane_', ''))
            }
        }

    currentLayerIndex = 1;

    /*
     * initHandlers
     *
     * Sets up any event handlers in this module
     *
     */
    var initHandlers = function(){
        // Each dataset link in the menu...
        $("a.dataset").click(loadUnloadDataset);

        var datasetHeadings = $("a.dataset-heading");
        datasetHeadings.click(expandCollapse);

        datasetHeadings.filter('.model-run').click(function() {
            var run_id = $(this).data("model_run_id");
            var dataset_type = $(this).parent().siblings('div').find('a.dataset').last().attr('dataset-type');
            if (dataset_type == DATASET_TYPE_COVERAGE || dataset_type == DATASET_TYPE_LAND_COVER_FRAC || dataset_type == DATASET_TYPE_SOIL_PROP) {
                loadBoundaries(run_id, function() {});
            } else if (dataset_type == DATASET_TYPE_SINGLE_CELL) {
                loadPositions(run_id, function() {});
            }
        });

        // Image export
        $("a#image-export").click(exportMapImage);

        // The layer element is dynamically-populated, so the event handlers
        // need to be declared on a static element instead, so using JQuery's 'on' functionality
        var layerContainer = $("div#options-panel");

        // Toggle the layer on or off
        layerContainer.on("click", "input.layer-toggle", function(){
           toggleLayerDisplay($(this).data("layerid"));
           updateGraph();
        });

        // Toggle legend display on/off
        layerContainer.on("click", "input.legend-toggle", function(){
            toggleLegendDisplay($(this).data("layerid"));
        });

        // Changing the style of the layer
        layerContainer.on("change", "select.style-list", function(){

            var layerId = $(this).data("layerid");
            layerDict[layerId].styleName = $(this).val();
            setLayerStyle(layerId);
        });

        // Pop up the panel containing more detailed analysis information
        layerContainer.on("click", "a.view-analysis", function(){

            // Load the HTML straight from the response
            $("div#analysis-detail").load( '/analysis/view/' + $(this).data("analysisid") + '?compact' );
        });

        layerContainer.on("click", "button.scale-update", function() {

            var value1 = $(this).siblings("input.scale-min")[0].value;
            var value2 = $(this).siblings("input.scale-max")[0].value;

            // Swap them over if they are the wrong way round
            var minValue = Math.min(value1, value2);
            var maxValue = Math.max(value1, value2);

            var layerId = $(this).data("layerid");
            var layerObj = layerDict[layerId];
            layerObj.scaleMin = minValue;
            layerObj.scaleMax = maxValue;
            setLayerStyle(layerId);
        });

        layerContainer.on("change keyup", "select.dimension", function(){
            // If the layer whose dimenson we're changing is am ancillary file (land cover, soil props etc)
            // we must call the changeAncilsLayer() method rather than changeDimension()
            var ds_type = $(this).attr("dataset_type")
            if (ds_type == DATASET_TYPE_LAND_COVER_FRAC || ds_type == DATASET_TYPE_SOIL_PROP) {
                var value = $(this).val();
                var layerId = $(this).closest("div.layer-controls").attr("data-layerid");
                var datasetId = $(".dataset[layer-id='" + layerId +  "']").attr("data-dsid");
                changeAncilsLayer(value, layerId, datasetId);
            } else {
                changeDimension(
                  $(this).data("dimension"),
                  $(this).val()
                );
                updateGraph();
            }
        });

        // Reset button
        $("button#reset-button").click(resetViewer);

        $("button#reset-graph").click(resetGraph);
        $("button#close-graph").click(hideGraph);
    };

    var createSortableList = function() {

        // Making the layers sortable - we'll
        // have an <ol> for each dataset selected
        $("ol.sortable").sortable({
            group: 'layers',
            itemSelector : "li.layer",
            nested: false,
            handle: 'i.icon-resize-vertical',
            onDragStart: function ($item, position, _super) {
                var layerContainer = $("div#layer-list");

                // Force the list container to maintain its rendered width
                layerContainer.css('width',layerContainer.css('width'));
                _super($item, position);
            },

            onDrop : function($item, container, _super) {
                // How many layers do we have v--- Subtract base layer
                var index = map.layers.length-1;
                $("ol.sortable li.layer").each(function(){

                    // Now reorder the map layers based on the order
                    // they come through this each() function
                    var layerId = $(this).data("layerid");
                    var layer = layerDict[layerId];
                    layer.index = index;
                    var mapLayer = map.getLayersByName(layer.data.name)[0];
                    map.setLayerIndex(mapLayer, index);

                    index--;
                });
                var markerLayers = map.getLayersByName("Markers");
                if (markerLayers.length > 0) {
                    map.setLayerIndex(markerLayers[0], 100000);
                }
                _super($item, container);
            }
        });
    };

    var boundsDict = {};
    var positionsDict = {}

    var waitForBoundaries = function(run_id, callback) {
        waitForResult(run_id, boundsDict, loadBoundaries, callback);
    }

    var waitForPositions = function(run_id, callback) {
        waitForResult(run_id, positionsDict, loadPositions, callback);
    }

    var waitForResult = function(key, dict, loadFunction, callback) {
        if (key in dict) {
            result = dict[key];
            if (result == 'loading') {
                setTimeout(function() {
                    if (dict[key] == 'loading') {
                        loadFunction(key, callback);
                    } else {
                        callback();
                    }
                }, 2500);
            } else {
                callback();
            }
        }
    }

    var loadBoundaries = function(run_id, callback) {
        boundsDict[run_id] = 'loading';
        $.getJSON('/dataset/multi_cell_location/' + run_id, function(data){
            var projection = new OpenLayers.Projection("EPSG:4326");
            var bounds = new OpenLayers.Bounds(data.lon_w, data.lat_s, data.lon_e, data.lat_n);
            bounds.transform(projection, map.getProjectionObject());
            boundsDict[run_id] = bounds;
            callback();
        });
    }

    var loadPositions = function(run_id, callback) {
        positionsDict[run_id] = 'loading';
        $.getJSON("/dataset/single_cell_location/" + run_id, function(result) {
            var position = new OpenLayers.LonLat(result.lon, result.lat);
            positionsDict[run_id] = position;
            callback();
        });
    }

    /*
     * loadUnloadDataset
     *
     * Loads or unloads an EcoMaps dataset into the map page
     *
     */
    var loadUnloadDataset = function() {
        var datasetId = $(this).data("dsid");
        var dataset_type = $(this).attr("dataset-type")
        var layerId = $(this).attr("layer-id");
        var datasetLink = $(this).closest("li");

        // Is this already selected?
        if (datasetLink.hasClass("active")) {
            unloadDataset(dataset_type, layerId, datasetLink);
        }
        else {
            loadDataset(dataset_type, layerId, datasetId, datasetLink);
        }
    };

    /*
     * unloadDataset
     *
     * Unloads an EcoMaps dataset from the map page
     *
     */
    var unloadDataset = function(dataset_type, layerId, datasetLink) {
        datasetLink.removeClass("active");

        if (dataset_type == DATASET_TYPE_COVERAGE || dataset_type == DATASET_TYPE_LAND_COVER_FRAC || dataset_type == DATASET_TYPE_SOIL_PROP) {
            removeLayerFromMap(layerId);
        }

        var panel = $('li.layer[data-layerid="' + layerId + '"]');
        panel.remove();
        var time_controls = $('div.layer-controls[data-layerid="' + layerId + '"]');
        time_controls.remove();

        // Dimensions
        if ($('div.layer-controls').length == 0) {
            $('#options-panel').hide();
        }
        // Layers
        if ($("ul.layer-controls").length == 0) {
            $("div#layer-panel").hide();
        }

        updateGraph();
    }

    /*
     * showPanelLoading
     *
     * Shows message indicating that the layers panel is loading
     */
    var showPanelLoading = function() {
        $('#layers-loading').show();
    }

    /*
     * hidePanelLoading
     *
     * Hides message indicating that the layers panel is loading
     */
    var hidePanelLoading = function() {
        $('#layers-loading').hide();
    }


    /*
     * loadDataset
     *
     * Loads an EcoMaps dataset to the map page
     *
     */
    var loadDataset = function(dataset_type, layerId, datasetId, datasetLink) {
        var run_id = datasetLink.find('a.dataset').data("model_run_id");
        if (dataset_type == DATASET_TYPE_COVERAGE || dataset_type == DATASET_TYPE_LAND_COVER_FRAC || dataset_type == DATASET_TYPE_SOIL_PROP) {
            centerOnMap(run_id);
            getMapDataAndShow(layerId, datasetId, '');
        }
        if (dataset_type == DATASET_TYPE_TRANSECT) {
            alert("Transects (datasets which are only 1 cell deep) are not supported for visualisation");
            return false;
        } else {
            // Plop the loading panel over the map
            datasetLink.addClass("active");
            showPanelLoading();
            setLoadingState(true);
            // Load the layers UI straight from the response
            $.get("/viewdata/layers?dsid=" + datasetId + "&layerid=" + layerId, function(result) {
                var ds_li = $("a.dataset[layer-id='" + layerId + "']").parent();
                var loadCancelled = !ds_li.hasClass('active');
                if (loadCancelled) {
                    setLoadingState(false);
                    hidePanelLoading();
                    return false;
                }

                $("div#layer-container").prepend(result);
                var dimensionItems = $("div#layer-list").find("li.dimension");

                if(dimensionItems.length > 0){
                    dimensionItems.detach().appendTo("ol#dimension-list");
                    $("div#dimension-panel").show();
                }
                if($("li.layer").length == 0) {
                    $("div#layer-panel").hide();
                } else {
                    $("div#layer-panel").show();
                }
                $("div#options-panel").show();
                createSortableList();
                if (dataset_type == DATASET_TYPE_COVERAGE) {
                    updateGraph();
                } else {
                    waitForPositions(run_id, function () {
                        createGraph(positionsDict[run_id]);
                    });
                }
                hidePanelLoading();
            }).fail(function() {
                setLoadingState(false);
                hidePanelLoading();
                datasetLink.removeClass("active");
            });
        }
        // All done
        setLoadingState(false);
    }


    var getMapDataAndShow = function(layerId, datasetId, variable) {
        // Make the request for the WMS layer data
        $.getJSON('/viewdata/get_layer_data?dsid=' + datasetId + "&variable=" + variable,
            function(data){
                var ds_li = $("a.dataset[layer-id='" + layerId + "']").parent();
                var loadCancelled = !ds_li.hasClass('active');
                if (loadCancelled) {setLoadingState(false);return false;}
                for(var i=0; i< data.length; i++){

                    // Give it a unique ID for our layer bag
                    var id = "" + layerId;

                    // We'll refer back to this when changing styles or visibility
                    layerDict[id] = {
                        index: currentLayerIndex,
                        data: data[i],
                        visible: true,
                        wmsObject: null,
                        legendURL: null,
                        scaleMin: data[i].data_range_from,
                        scaleMax: data[i].data_range_to,
                        styleName: data[i].styles[0].name,
                        isCategorical: data[i].is_categorical
                    };

                    // Now to add to the map, and set a default style
                    addLayerToMap(layerId);
                    setLayerStyle(layerId);
                }
            }
        ).fail(function() {
            alert("An error occurred loading the dataset, please try again.");
            setLoadingState(false);
        });
    }

    /*
     * centerOnMap
     *
     * If the loaded dataset is the only dataset on the map, center the map viewer
     * on the geographical extent of the dataset.
     */
    var centerOnMap = function (run_id) {
        if (Object.keys(layerDict).length == 0) {
            waitForBoundaries(run_id, function() {
                map.zoomToExtent(boundsDict[run_id]);
            });
        }
    }


    /*
     * initMap
     *
     * Sets up the OpenLayers map
     *
     */
    var initMap = function() {

        // Switch to true for Google base map
        var useGoogle = false;
        var wms = null;

        // Zoom in over the UK to begin with, set coords here
        var lat = 54;
        var lon = -2;
        var position = new OpenLayers.LonLat(lon, lat);

        if(useGoogle) {

            var WGS84 = new OpenLayers.Projection("EPSG:4326");
            var WGS84_google_mercator = new OpenLayers.Projection("EPSG:3857");

            OpenLayers.Projection.addTransform("EPSG:4326", "EPSG:3857", OpenLayers.Layer.SphericalMercator.projectForward);
            OpenLayers.Projection.addTransform("EPSG:3857", "EPSG:4326", OpenLayers.Layer.SphericalMercator.projectInverse);

            var options = {
                projection: WGS84_google_mercator,
                displayProjection: WGS84,
                units: "m",
                maxResolution: 156543.0339,
                maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
                                                 20037508.34, 20037508.34)
            };

            map = new OpenLayers.Map('map', options);
            //var apiKey = "AlLzJcuciFYnzQhJZlyE5OGjGWtvWp2MfQNYDPL6kE4JnltPwiQL4gNayJbqS7MX";

            // Google map
            wms = new OpenLayers.Layer.Google("Test", {
                //key: apiKey,
                type: google.maps.MapTypeId.TERRAIN,
                "sphericalMercator": true
            });

            position.transform(WGS84, new OpenLayers.Projection("EPSG:900913"));

        }
        else {
            OpenLayers.IMAGE_RELOAD_ATTEMPTS = 10;
            map = new OpenLayers.Map('map');
            wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                "/dataset/base", {layers: 'basic'});
        }

        // Add the custom loading panel here...
        map.addControl(new OpenLayers.Control.LoadingPanel());
        map.addControl(new OpenLayers.Control.ScaleLine());

        map.addLayer(wms);
        map.zoomToMaxExtent();

        // Perform the zoom to the UK
        map.setCenter(position, 6);

        var loadingPanel = $('div.olControlLoadingPanel');
        var zoom = $('div.olControlZoom');
        var lp_z = parseInt(loadingPanel.css('z-index'));
        zoom.css('z-index', lp_z + 100);

        // Add a click event handler in the graphing JS
        map.events.register("click", map, function(e) {
            var position = map.getLonLatFromPixel(e.xy);
            createGraph(position);
        });

        // Stretch the map down the page.
        // Hide the panel div first because otherwise it overflows if there are lots of datasets
        $("#panel-div").hide();
        $("#map").height($("#wrap").height() - 42);
        $("#panel-div").height($("#wrap").height() - 42);
        $("#panel-div").show();
    };

    /*
     * setLoadingState
     *
     * Puts a loading div over the map
     *
     *  @param isLoading: true to show the div, false to hide
     */
    var setLoadingState = function(isLoading) {

        if(isLoading) {

            $("div#map-loading").show();
        }
        else {
            $("div#map-loading").hide();
        }
    };

    /*
     * removeLayerFromMap
     *
     * Removes the layer with the specified ID from the map
     *
     *  @param layerId: ID of the layer to remove
     */
    var removeLayerFromMap = function(layerId) {

        // Look the layer up...
        var layerObj = layerDict[layerId];

        //..remove from the map...
        if (typeof layerObj != 'undefined') {
            map.removeLayer(layerObj.wmsObject);


            //..legend..
            removeLegend(layerId);

            //..and make sure we remove from the bag
            delete layerDict[layerId];
            currentLayerIndex--;
        }
    };

    /*
     * addLayerToMap
     *
     * Adds a layer in our internal bag to the map control
     *
     *  @param layerId: ID of the layer to add
     */
    var addLayerToMap = function(layerId) {

        // Extract the bits we need to make the WMS object that
        // OpenLayers expects
        var layerObj = layerDict[layerId];

        var data = layerObj.data;

        // Standard parameters
        var defaultLayerParams = {
            format: 'image/png',
            version: '1.3.0',
            CRS: 'CRS:84',
            transparent: 'TRUE',
            opacity: 80,
            belowmincolor: 'transparent',
            abovemaxcolor: 'extend'
        };

        // Pull out extra info for the layer constructor
        var mapUrl = data.getMapUrl;
        var wmsVersion = data.wmsVersion;
        var layerName = data.name;

        if (wmsVersion) {
            defaultLayerParams.version = wmsVersion;
        }

        // Now we're ready to create the layer object
        var layer = new OpenLayers.Layer.WMS(layerName,
            mapUrl, defaultLayerParams, defaultLayerOptions);

        // Add a legend graphic
        var defaultStyle = data.styles[0];
        layerObj.legendURL = defaultStyle.legendURL.onlineResource.split('?')[0];

        $("div#legend").show();

        // Add to map
        layer.params['layers'] = layerName;
        map.addLayer(layer);
        layerObj.wmsObject = layer;
        currentLayerIndex++;
    };

    /*
     * toggleLayerDisplay
     *
     *  Toggles a layer's visibility
     *
     *  @param layerId: ID of the layer to toggle
     */
    var toggleLayerDisplay = function(layerId) {

        // Get the layer ref from our storage
        var layerObj = layerDict[layerId];
        var index = layerObj.index;

        // Simply swap the visibility over
        layerObj.visible = !layerObj.visible;
        map.layers[index].setVisibility(layerObj.visible);

        if(layerObj.visible) {
            var currentLayerStyle = $("div#options-panel").find("select[data-layerid = '" + layerId + "']")[0];
            addLegend(layerId, $(currentLayerStyle).val());
            // Hide the legend if the legend check box is unticked
            if (!$(".legend-toggle[data-layerid=" + layerId + "]").prop("checked")) {
                toggleLegendDisplay(layerId);
            }
        }
        else {
            // Always remove the legend because we never want to see it without the data
            removeLegend(layerId);
        }
    };

    /*
     * toggleLegendDisplay
     *
     *  Toggles a layer's legend visibility
     *
     *  @param layerId: ID of the layer containing the legend to toggle
     */
    var toggleLegendDisplay = function(layerId) {

        $("img[data-layerid=" + layerId + "]").toggle();
    };

    /*
     * setLayerStyle
     *
     *  Sets the style of the specified layer
     *
     *  @param layerId: ID of the layer to update the style for
     */
    var setLayerStyle = function(layerId) {

        var layerObj = layerDict[layerId];
        var index = layerObj.index;

        // Change the style parameter on this layer
        map.layers[index].mergeNewParams({
           'styles' : layerObj.styleName,
           'colorscalerange': layerObj.scaleMin + "," + layerObj.scaleMax
        });

        removeLegend(layerId);
        addLegend(layerId);
    };

    /*
     * addLegend
     *
     *  Adds a legend graphic for the specified layer with
     *  the specified style
     *
     *  @param layerId: ID of the layer to add a legend for
     */
    var addLegend = function(layerId) {

        layerObj = layerDict[layerId];
        var styleName = layerObj.styleName;
        // First let's get the style name in a form we can use
        // The map layer will most likely have a style like
        // 'boxfill/rainbow' - but we just want the 'rainbow' bit
        if(styleName.indexOf('/') > -1){
            styleName = styleName.split('/')[1];
        }
        // Now we should get the URL for the legend graphic
        legendURL = layerObj.legendURL;
        legendURL += "?REQUEST=GetLegendGraphic" +
                        "&LAYER=" + layerObj.data['name'] +
                        "&PALETTE=" + styleName +
                        "&colorscalerange=" + layerObj.scaleMin + "," + layerObj.scaleMax;

        if(layerObj.isCategorical) {
            legendURL += "&NUMCOLORBANDS=" + (layerObj.scaleMax-layerObj.scaleMin);
        }

        $("div#legend").append("<img data-layerid='" + layerId + "' src='" + legendURL + "' />");
    };

    /*
     * removeLegend
     *
     *  Removes the legend graphic for the specified layer
     *
     *  @param layerId: ID of the layer
     *                  corresponding to the legend to remove
     */
    var removeLegend = function(layerId) {

        $("div#legend").find("img[data-layerid='" + layerId + "']").remove();
    };

    /*
     * changeDimension
     *
     *  Alters the dimension of all layers based on the value passed in
     *
     *  @param dimension: Name of the dimension to change (time usually)
     *  @param value: The dimension value to set
     */
    var changeDimension = function(dimension, value) {

        var layerObj;
        var dimensionObj = {};

        for(var l in layerDict) {
            if(layerDict.hasOwnProperty(l)){
                layerObj = layerDict[l];
                dimensionObj = {};
                dimensionObj[dimension] = value;
                map.layers[layerObj.index].mergeNewParams(dimensionObj);
            }
        }
    };

    var changeAncilsLayer = function(value, layerId, datasetId) {
        // Remove existing layer from map
        removeLayerFromMap(layerId);
        // Load new layer to map
        getMapDataAndShow(layerId, datasetId, value);
    }

    /*
     * exportMapImage
     *
     *  Exports the current map state to a canvas, which
     *  can be saved as an image (except in IE8, typical)
     *
     */
    var exportMapImage = function() {

        // Let's find the canvas on the page
        var canvas = $("canvas#map-canvas").get(0);
        canvas.width = 0;

        // Set the canvas to the right size for this map
        canvas.width = map.viewPortDiv.clientWidth;
        // adding a little more height for padding the legends
        canvas.height = map.viewPortDiv.clientHeight + 200;

        // OK let's set up the canvas...
        var context = canvas.getContext("2d");

        // Which layers are selected ?
        var visibleLayers = $("div.olLayerGrid").filter(function(){
            return $(this).css("display") != 'none';
        });

        // Now look for each tile image in the layer...
        visibleLayers.children("img").each(function(){

            //..and draw it in the canvas
            context.drawImage(this, this.offsetLeft, this.offsetTop);
        });

        // This'll help us space the legends out
        var legendCount =0;

        $("div#legend img").each(function(){

            // Draw the legends at the bottom left, spaced out by their width
            context.drawImage(this, $(this).width()*legendCount, 490);
            legendCount++;
        });

        context.font = "bold 20px sans-serif";
        context.fillText("Majic Image Export - " + $("#map-title").html(), 10,25);

        var layerCount = 1;

        // Now to write the layer names out
        for(var l in layerDict) {
            if(layerDict.hasOwnProperty(l)){
                layerObj = layerDict[l];

                if(layerObj.visible) {
                    context.font = "18px sans-serif";
                    context.fillText(layerObj.data.title, 20,45*layerCount);
                    layerCount++;
                }
            }
        }

        window.open(canvas.toDataURL("image/png"));
    };

    var resetViewer = function() {

        // Reset the layers on the map
        for(var l in layerDict) {
            if(layerDict.hasOwnProperty(l)){
                removeLayerFromMap(l);
            }
        }

        $("div#layer-container").html("");
        $("ol#dimension-list").html("");
        $("div#dimension-panel").hide();
        $("div#options-panel").hide();
        $(".nav-list").find("li.active").removeClass("active");

        hideGraph();
    };

    var checkMapServer = function() {
        $.getJSON('/map/is_thredds_up', function(data) {
            var thredds_up = data['thredds_up'];
            if (!thredds_up) {
                $("div#server-offline").show();
            }
        });
    };

    return {

        init: function() {
            setLoadingState(false);
            initHandlers();
            // Open currently selected modelrun (if there is one)
            openSelectedRun();
            initMap();
            checkMapServer();
        }
    }
})();
$(function() {
        EcomapsMap.init();
    }
);
