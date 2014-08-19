var enable_disable_fractional_values = function() {
    var ice_box = $('#land_cover_ice');
    var frac_vals = $('#fractional_vals').find('input');
    if (ice_box.is(':checked')) {
        frac_vals.prop('disabled', true);
    } else {
        frac_vals.prop('disabled', false);
    }
}

$(document).ready(function() {
    $('#land_cover_ice').click(enable_disable_fractional_values);
    enable_disable_fractional_values();
})