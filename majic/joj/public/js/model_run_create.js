var id_attr = 'configid';
var radio_button_id_prefix = '#science_configuration_';
var click_selectors = '.select-div, .description-div';

/*
 * Prepare the Model run Create page (create.html).
 */
$(document).ready(function() {
    EcomapsGeneral.initialise_custom_checkboxes(id_attr, radio_button_id_prefix, click_selectors);
});