/*
 * Convert the BNG coordinates to lat/lon using an AJAX call and set them on the page
 */
var bngToLatLon = function() {
    var bng_easting = $('#bng_e').val();
    var bng_northing = $('#bng_n').val();
    var url = "/model_run/bng_to_latlon?bng_easting=" + bng_easting + "&bng_northing=" + bng_northing;
    $.getJSON(url, function(data) {
        if (data.is_error) {
            displayBngError();
        } else {
            setLatLon(data.lat, data.lon);
        }
    }).fail(displayBngError);
}

/*
 * Set the latitude and longitude for the single site.
 */
var setLatLon = function(lat, lon) {
    $('input#lat').val(lat);
    $('input#lon').val(lon);
    $('#bng-error').hide();
}

/*
 * Display an error message in the BNG converter
 */
var displayBngError = function() {
    $('#bng-error').show();
}


$(document).ready(function() {
     // Add click handler for the BNG to Lat/Lon button
    $('#convert-bng').click(bngToLatLon);
});