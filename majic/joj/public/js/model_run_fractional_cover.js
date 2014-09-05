var disable_fractional_values_if_ice = function() {
    var ice_input = $('#land_cover_ice');
    if (ice_input.length > 0) {
        var frac_vals = $('#fractional_vals').find('input');
        frac_vals.prop('disabled', true);
    }
}

$(document).ready(function() {
    disable_fractional_values_if_ice();

    // The error formatting resets these for some reason that I don't understand...
    $('.land_cover_value').height(20);
    $('.land_cover_value').width(100);

})