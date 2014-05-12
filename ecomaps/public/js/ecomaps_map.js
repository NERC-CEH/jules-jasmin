/**
 * Created by Phil Jenkins (Tessella) on 2/25/14.
 *
 * Simplified map viewer suitable for the EcoMaps application
 *
 */

var EcomapsMap = (function() {

    // Module-level variables
    var map = null;
    var layerDict = new Object();
    var defaultLayerOptions = {
        isBaseLayer: false,
        buffer: 0
    };

    var currentLayerIndex = 1;

    /*
     * initHandlers
     *
     * Sets up any event handlers in this module
     *
     */
    var initHandlers = function(){

        // Each dataset link in the menu...
        $("a.dataset").click(loadDataset);

        // Image export
        $("a#image-export").click(exportMapImage);

        // The layer element is dynamically-populated, so the event handlers
        // need to be declared on a static element instead, so using JQuery's 'on' functionality
        var layerContainer = $("div#options-panel");

        // Toggle the layer on or off
        layerContainer.on("click", "input.layer-toggle", function(){
           toggleLayerDisplay($(this).data("layerid"));
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

            var minValue = $(this).siblings("input.scale-min")[0].value;
            var maxValue = $(this).siblings("input.scale-max")[0].value;

            var layerId = $(this).data("layerid");
            var layerObj = layerDict[layerId];
            layerObj.scaleMin = minValue;
            layerObj.scaleMax = maxValue;
            setLayerStyle(layerId);
        });

        layerContainer.on("change keyup", "select.dimension", function(){

            changeDimension(
              $(this).data("dimension"),
              $(this).val()
            );
        });

        // Reset button
        $("button#reset-button").click(resetViewer);
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
                _super($item, container);
            }
        });
    };

    /*
     * loadDataset
     *
     * Loads a EcoMaps dataset into the map control
     *
     */
    var loadDataset = function() {

        // Highlight the selected dataset
        //$("li.active").removeClass("active");
        if ($(this).closest("li").hasClass("active")) {

        }
        else {

            $(this).closest("li").addClass("active");
            // Plop the loading panel over the map
            setLoadingState(true);

            // Let's get some layers!
            var datasetId = $(this).data("dsid");

            // Load the layers UI straight from the response
            $.get('/viewdata/layers/' + datasetId, function(result) {

                $("div#layer-container").prepend(result);
                var dimensionItems = $("div#layer-list").find("li.dimension");

                if(dimensionItems.length > 0){
                    dimensionItems.detach().appendTo("ol#dimension-list");
                    $("div#dimension-panel").show();
                }
                $("div#options-panel").show();
                createSortableList();
            });

            // Make the request for the WMS layer data
            $.getJSON('/viewdata/get_layer_data?dsid=' + datasetId,
                function(data){

                    for(var i=0; i< data.length; i++){

                        // Give it a unique ID for our layer bag
                        var layerId = "" + datasetId + data[i].name;

                        // We'll refer back to this when changing styles or visibility
                        layerDict[layerId] = {
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

                    // All done
                    setLoadingState(false);
                }
            ) .fail(function() {
                    alert("An error occurred loading the dataset, please try again.");
                    setLoadingState(false);
                });
        }
    };

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

            map = new OpenLayers.Map('map');
            wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
                "/dataset/base", {layers: 'basic'});
        }

        // Add the custom loading panel here...
        map.addControl(new OpenLayers.Control.LoadingPanel());
        map.addControl(new OpenLayers.Control.ScaleLine())

        map.addLayer(wms);
        map.zoomToMaxExtent();

        // Perform the zoom to the UK
        map.setCenter(position, 6);

        // Stretch the map down the page
        $("#map").height($("#wrap").height());
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
        map.removeLayer(layerObj.wmsObject);

        //..legend..
        removeLegend(layerId);

        //..and make sure we remove from the bag
        delete layerDict[layerId];
        currentLayerIndex--;
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
        }
        else {
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
        context.fillText("EcoMaps Image Export - " + $("#map-title").html(), 10,25);

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
        $("li.active").removeClass("active");
    };

    return {

        init: function() {
            setLoadingState(false);
            initHandlers();
            initMap();
        }
    }
})();
$(function() {
        EcomapsMap.init();
    }
);
