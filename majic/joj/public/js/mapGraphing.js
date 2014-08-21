/**
 * # header
 */

//Keep the data variable here so we can re-use it on map reset.
var data;
// Store the marker and marker layer here so we can move it rather than add more
var marker, markers;
var stored_position;

/**
 * Creates and displays an appropriate time series graph in response to a click on the OpenLayers map
 * @param position The OpenLayers LatLong object representing the position that was clicked
 * @returns {boolean}
 */
function createGraph(position)
{
    stored_position = position;
    // Get all the datasets to show
    var datasets = getSelectedLayers();
    if (datasets.length == 0) {
        return false;
    }
    setMarker(position);
    createGraphSpace(position);
    getData(datasets, position);
    return true;
}

var updateGraph = function() {
    var graphDiv = $("#graph");
    //if (graphDiv.is(':visible')) {
        if (typeof stored_position != 'undefined') {
            var position = stored_position;
            var graphs_added = createGraph(position);
            if (!(graphs_added)) {
                hideGraph();
                stored_position = position;
            }
        }
    //}
}

/**
 * Set a marker on the map at the position clicked.
 * @param position The OpenLayers LatLong object representing the position that was clicked
 */
function setMarker(position)
{
    if (!markers) {
        // Add a new layer if we need to
        markers = new OpenLayers.Layer.Markers( "Markers" );
        map.addLayer(markers);
        currentLayerIndex++;
    }
    if (marker) {
        // Clear the marker before adding a new one
        markers.removeMarker(marker);
    }
    var size = new OpenLayers.Size(21,25);
    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
    var icon = new OpenLayers.Icon('/layout/images/marker.png', size, offset);
    marker = new OpenLayers.Marker(position, icon);
    markers.addMarker(marker);
}

/**
 * Get a list of all currently selected data layers
 * @returns {Array} List of dataset IDs
 */
function getSelectedLayers()
{
    var dataset_ids = [];
    $(".dataset").each(function()
    {
        if ($(this).parent().hasClass("active")){
            // Check that the graph layer is visible:
            var layerId = $(this).attr("layer-id");
            var layerCheckBox = $('input.layer-toggle[data-layerid="' + layerId + '"]')
            if (layerCheckBox.is(':checked')) {
                dataset_ids[dataset_ids.length] = ($(this).attr("data-dsid"));
            }
        }
    });
    return dataset_ids;

}

/**
 * Create the graph space on the page
 * @param position OpenLayers LatLong object representing the position that was clicked
 */
function createGraphSpace(position)
{
    var graphDiv = $("#graph");
    if (graphDiv.css('display') == 'none')
    {
        var mapDiv = $("#map");
        // Set graph and map to correct height
        var space = mapDiv.height();
        graphDiv.height(space / 2.5);
        mapDiv.height(space - graphDiv.height());

        // Then make graph visible
        graphDiv.show();
        graphDiv.width(mapDiv.width());
        // Center on the new position since we have moved the screen
        map.setCenter(position);

    }
    graphDiv.addClass("graph-loading");
}

/**
 * Hide the graphing area
 */
function hideGraph()
{
    // Hide graph
    var graphDiv = $("#graph");
    graphDiv.hide();
    // Remove the map marker
    if (marker) {
        markers.removeMarker(marker);
    }
    stored_position = undefined;
    // Reset the map height
    $("#map").height($("#wrap").height() - 100);
}

/**
 * Reset the graph to the original zoom and position
 */
function resetGraph()
{
    plotGraph(data);
}

/**
 * Get the data from the OpenDap Client and call the plotting function
 * @param datasets The list of dataset IDs to retrieve graphing data for
 * @param position OpenLayers LatLong object representing the position that was clicked
 */
function getData(datasets, position)
{
    data = [];
    for (var i = 0; i < datasets.length; i++ ) {
        var dsid = datasets[i];
        var url = "/map/graph/" + dsid + "?lat=" + position.lat + "&lon=" + position.lon;
        $.getJSON(url, function (_data) {
            data[data.length] = _data;
            // If this is the last one then we can go ahead and plot them all
            if (data.length == datasets.length){
                plotGraph(data);
            }
        }).fail(function() {
            alert("An error occurred loading the dataset, please try again.");
            hideGraph();
        });
    }
}

/**
 * Plot the selected data on a graph
 * @param data Graph data in JSON format
 */
function plotGraph(data)
{
    var graph = $("#graph");
    graph.removeClass("graph-loading");
    // We need to iterate over all the data and do the following:
    var dataList = [];
    var yaxesList = [];
    for (var i = 0; i < data.length; i++) {
        dataList[dataList.length] = {
            label : data[i].label,
            data: data[i].data,
            yaxis : i+1
        };
        // Set the range a little bit taller than the graph
        ymax = data[i].ymax - (data[i].ymin - data[i].ymax) * 0.25;
        if (data.ymin < 0) {
            ymin = data[i].ymin - (data[i].ymax - data[i].ymin) * 0.25;
        } else {
            ymin = Math.max(data[i].ymin - (data[i].ymax - data[i].ymin) * 0.25, 0);
        }

        yaxesList[yaxesList.length] = {
            max: ymax,
            min: ymin
        };
    }

    $.plot(graph, dataList, {
        xaxis: {
            mode: "time",
            max: data.xmax,
            min: data.xmin
        },
        yaxes: yaxesList,
        zoom: {
            interactive: true
        },
        pan: {
            interactive: true
        },
        legend: {position: "nw"}
    });
    // Add a close button and reset button
    var closeButtonHtml = '<div class="alert alert-info" style="position:absolute;right:' + 30 + 'px;top:' + 14 +'px">' +
        '<a href="#" onclick="hideGraph()" id="graph-close-img"><i class="icon-remove"></i> Close</a></div>';
    graph.append(closeButtonHtml);

    var resetButtonHtml = '<div class="alert alert-info" style="position:absolute;right:' + 140 + 'px;top:' + 14 +'px">' +
        '<a href="#" onclick="resetGraph()" id="graph-close-img"><i class="icon-screenshot"></i> Reset</a></div>';
    graph.append(resetButtonHtml);
}