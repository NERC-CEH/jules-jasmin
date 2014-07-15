var id_attr = 'dsid';
var radio_button_id_prefix = '#driving_dataset_';
var click_selectors = 'tr.driving-data';

/*
 * Prepare the Model run Driving data page (driving_data.html).
 */
$(document).ready(function() {
    EcomapsGeneral.initialise_custom_checkboxes(id_attr, radio_button_id_prefix, click_selectors);
});