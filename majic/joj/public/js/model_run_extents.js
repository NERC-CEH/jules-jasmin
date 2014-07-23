// These are used for the custom radio buttons
var id_attr = 'site';
var radio_button_id_prefix = '#site_';
var click_selectors = '.site-select';

/*
 * This is called when the user has chosen to use multi-cell extents.
 * Show the multi-cell area of the page and hide the single cell area.
 */
var chooseMultiCell = function () {
    var singleCell = $('#single-cell, #upload-single-cell');
    var multiCell = $('#multi-cell')
    singleCell.find('input').prop('disabled', true);
    singleCell.hide();
    multiCell.find('input').prop('disabled', false);
    multiCell.show();
}

/*
 * This is called when the user has chosen to use single-cell extents.
 * Show the single-cell area of the page and hide the multi cell area.
 */
var chooseSingleCell = function () {
    var singleCell = $('#single-cell, #upload-single-cell');
    var multiCell = $('#multi-cell')
    singleCell.find('input').prop('disabled', false);
    singleCell.show();
    multiCell.find('input').prop('disabled', true);
    multiCell.hide();
}

/*
 * Update the page after one of the spatial extent radio boxes is ticked
 */
var updatePageFromSelect = function() {
    var selected = $('input[id^="site_"]:checked');
    if (selected.attr('id') === 'site_multi') {
        chooseMultiCell();
    } else {
        chooseSingleCell();
    }
}

/*
 * Update the checkbox for the 'average over cell' option (it's a custom icon
 * over the top of a standard check box).
 */
 var updateCheckBoxIcon = function() {
    var check = $('#average_over_cell');
    var icon = $('#check_av');
    if (check.is(':checked')) {
        icon.removeClass('grey');
        icon.addClass('green');
        icon.removeClass('fa-square-o');
        icon.addClass('fa-check-square-o');
    } else {
        icon.removeClass('green');
        icon.addClass('grey');
        icon.removeClass('fa-check-square-o');
        icon.addClass('fa-square-o');
    }
}

/*
 * Toggle the 'average driving data over cell' check box
 */
var toggleAverageCheckBox = function () {
    //toggle the box
    var check = $('#average_over_cell');
    if (check.is(':checked')) {
        check.prop('checked', false);
    } else {
        check.prop('checked', true);
    }
    // then update the icon
    updateCheckBoxIcon();
}

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

var chooseUploadDrivingData = function () {
    // Select the right option and deselect the other:
    var yes = $('#upload_yes i');
    yes.removeClass('grey');
    yes.addClass('green');
    yes.removeClass('fa-circle-o');
    yes.addClass('fa-check-circle-o');
    var no = $('#upload_no i');
    no.addClass('grey');
    no.removeClass('green');
    no.addClass('fa-circle-o');
    no.removeClass('fa-check-circle-o');

    // Show the relevant div
    $('#upload_driving_data').show();
}

var chooseNotUploadDrivingData = function () {
    // Select the right option and deselect the other:
    var no = $('#upload_no i');
    no.removeClass('grey');
    no.addClass('green');
    no.removeClass('fa-circle-o');
    no.addClass('fa-check-circle-o');
    var yes = $('#upload_yes i');
    yes.addClass('grey');
    yes.removeClass('green');
    yes.addClass('fa-circle-o');
    yes.removeClass('fa-check-circle-o');

    // Show the relevant div
    $('#upload_driving_data').hide();
}

/*
 * Prepare the Extents page (extents.html).
 */
$(document).ready(function() {
    EcomapsGeneral.initialise_custom_checkboxes(id_attr, radio_button_id_prefix, click_selectors);

    // Whenever one of the radio buttons (multi or single cell) is selected we want to update the page:
    $(click_selectors).click(updatePageFromSelect);
    updatePageFromSelect(); // Call this once to set up the page correctly

    // Set click handlers for the 'average driving data over cell' custom checkbox.
    $('#check_av').click(toggleAverageCheckBox);
    $('#average_over_cell').change(updateCheckBoxIcon);
    updateCheckBoxIcon(); // Call this once to make sure it's ticked if needed

    // Add click handler for the BNG to Lat/Lon button
    $('#convert-bng').click(bngToLatLon);

    $('#upload_no').click(chooseNotUploadDrivingData);
    $('#upload_yes').click(chooseUploadDrivingData);
    chooseNotUploadDrivingData();

    // Set Up tabs
    $('#driving-data-tabs').tab('show');
    $('#tab-upload').addClass('active');
});