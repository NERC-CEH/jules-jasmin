/**
 *    Majic
 *    Copyright (C) 2014  CEH
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License along
 *   with this program; if not, write to the Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
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
    var layers = getSelectedLayers();
    if (layers.length == 0) {
        return false;
    }
    setMarker(position);
    createGraphSpace(position);
    getData(layers, position);

    // Enable buttons
    closeBtn = $("button#close-graph");
    resetBtn = $("button#reset-graph");
    closeBtn.prop('disabled', false);
    closeBtn.removeClass('disabled');
    resetBtn.prop('disabled', false);
    resetBtn.removeClass('disabled');

    return true;
}
/**
 * Update the graph
 */
var updateGraph = function() {
    if (typeof stored_position != 'undefined') {
        var position = stored_position;
        var graphs_added = createGraph(position);
        if (!(graphs_added)) {
            hideGraph();
            stored_position = position;
        }
    }
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
    markers.setZIndex(100000);
    var size = new OpenLayers.Size(21,25);
    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
    var icon = new OpenLayers.Icon('/js/img/marker-gold.png', size, offset);
    marker = new OpenLayers.Marker(position, icon);
    markers.addMarker(marker);
    // Center on the new position since we have moved the screen
    map.setCenter(position);
}

/**
 * Get a list of all currently selected data layers
 * @returns {Array} List of Layer IDs
 */
function getSelectedLayers()
{
    var dataset_ids = [];
    $(".dataset").each(function()
    {
        if ($(this).parent().hasClass("active")){
            // Check that the graph layer is visible:
            var layerId = $(this).attr("layer-id");
            var dataset_type = $(this).attr("dataset-type");
            if (dataset_type != DATASET_TYPE_LAND_COVER_FRAC && dataset_type != DATASET_TYPE_SOIL_PROP) {
                var layerCheckBox = $('input.layer-toggle[data-layerid="' + layerId + '"]')
                // Add the layer IF: we didn't find a layer control (e.g. it's single cell) or the layer control is checked
                if (layerCheckBox.length ==0 || layerCheckBox.is(':checked')) {
                    dataset_ids[dataset_ids.length] = layerId;
                }
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
    // Disable buttons
    closeBtn = $("button#close-graph");
    resetBtn = $("button#reset-graph");
    closeBtn.prop('disabled', true);
    closeBtn.addClass('disabled');
    resetBtn.prop('disabled', true);
    resetBtn.addClass('disabled');

    // Hide graph
    var graphDiv = $("#graph");
    graphDiv.hide();
    // Remove the map marker
    if (marker) {
        markers.removeMarker(marker);
    }
    stored_position = undefined;
    // Reset the map height
    $("#map").height($("#wrap").height() - 42);
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
function getData(layerIds, position)
{
    data = [];
    for (var i = 0; i < layerIds.length; i++ ) {
        var layerId = layerIds[i];
        var dsid = $(".dataset[layer-id='" + layerId + "']").attr("data-dsid");
        var layerControls = $(".layer-controls[data-layerid='" + layerId + "']")
        var time = ""
        var time_control = layerControls.find("select.dimension")
        if (time_control.length) {
            time = time_control.val()
        }
        var url = "/map/graph/" + dsid + "?lat=" + position.lat + "&lon=" + position.lon + "&time=" + time;
        $.getJSON(url, function (_data) {
            data[data.length] = _data;
            // If this is the last one then we can go ahead and plot them all
            if (data.length == layerIds.length){
                plotGraph(data);
                var graph_title_template = "Measurements at Lat: {lat}, Lon: {lon}";
                var title = graph_title_template.replace(/{lat}/g, data[0].lat).replace(/{lon}/g, data[0].lon);
                $('#graph-title').text(title);
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
        var ymax = data[i].ymax - (data[i].ymin - data[i].ymax) * 0.25;
        if (data[i].ymin < 0) {
            var ymin = data[i].ymin - (data[i].ymax - data[i].ymin) * 0.25;
        } else {
            var ymin = Math.max(data[i].ymin - (data[i].ymax - data[i].ymin) * 0.25, 0);
        }

        yaxesList[yaxesList.length] = {
            max: ymax,
            min: ymin,
            zoomRange: false,
            panRange: false,
            tickFormatter: function (v, axis) {
                return v.toPrecision(3);
            }
        };
    }
    graph_placeholder = $("#graph-placeholder");

    $.plot(graph_placeholder, dataList, {
        xaxis: {
            mode: "time",
            max: data.xmax,
            min: data.xmin,
            panRange: [data.xmin, data.xmax]
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
}