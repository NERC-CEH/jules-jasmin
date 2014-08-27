var enable_disable_fractional_values = function() {
    var ice_box = $('#land_cover_ice');
    var frac_vals = $('#fractional_vals').find('input');
    if (ice_box.is(':checked')) {
        frac_vals.prop('disabled', true);
    } else {
        frac_vals.prop('disabled', false);
    }
}

/*
 * Update the checkbox for the 'is ice' option (it's a custom icon
 * over the top of a standard check box).
 */
 var updateCheckBoxIcon = function() {
    var check = $('#land_cover_ice');
    var icon = $('#check_ice');
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
    enable_disable_fractional_values();
}

/*
 * Toggle the 'is_ice' check box
 */
var toggleAverageCheckBox = function () {
    //toggle the box
    var check = $('#land_cover_ice');
    if (check.is(':checked')) {
        check.prop('checked', false);
    } else {
        check.prop('checked', true);
    }
    // then update the icon
    updateCheckBoxIcon();
}

$(document).ready(function() {
    $('#land_cover_ice').change(enable_disable_fractional_values);
    enable_disable_fractional_values();

    // Set click handlers for the 'is ice' custom checkbox.
    $('#check_ice').click(toggleAverageCheckBox); //updateCheckBoxIcon???
    $('#land_cover_ice').change(updateCheckBoxIcon);
    updateCheckBoxIcon(); // Call this once to make sure it's ticked if needed

    // The error formatting resets these for some reason that I don't understand...
    $('.land_cover_value').height(20);
    $('.land_cover_value').width(100);

})