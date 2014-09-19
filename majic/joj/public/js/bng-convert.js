/*
 * Convert the BNG coordinates to lat/lon using an AJAX call and set them on the page
 */

var _this;

var bngToLatLon = function() {
    var bng_easting = $(this).siblings('#bng_e').val();
    var bng_northing = $(this).siblings('#bng_n').val();
    var url = "/model_run/bng_to_latlon?bng_easting=" + bng_easting + "&bng_northing=" + bng_northing;
    _this = $(this);
    $.getJSON(url, function(data) {
        if (data.is_error) {
            displayBngError();
        } else {
            setLatLon(data.lat, data.lon);
        }
    }).fail(function() {
        displayBngError();
        });
    }

/*
 * Set the latitude and longitude for the single site.
 */
var setLatLon = function(lat, lon) {
    _this.closest('form').find('input#lat').val(lat);
    _this.closest('form').find('input#lon').val(lon);
    _this.closest('form').find('.bng-error').hide();
}

/*
 * Display an error message in the BNG converter
 */
var displayBngError = function() {
    _this.siblings('.bng-error').show();
}


$(document).ready(function() {
     // Add click handler for the BNG to Lat/Lon button
    $('.convert-bng').click(bngToLatLon);
});