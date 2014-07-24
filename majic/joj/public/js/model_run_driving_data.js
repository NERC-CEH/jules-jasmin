var id_attr = 'dsid';
var radio_button_id_prefix = '#driving_dataset_';
var click_selectors = 'tr.driving-data';

var enableUploadInput = function() {
    var uploadInput = $('#upload-input').find('input');
    var userUploadRadio = $('input[user_upload="true"]');
    if (userUploadRadio.is(':checked')) {
        uploadInput.prop('disabled', false);
    } else {
        uploadInput.prop('disabled', true);
    }
}

/*
 * Prepare the Model run Driving data page (driving_data.html).
 */
$(document).ready(function() {
    EcomapsGeneral.initialise_custom_checkboxes(id_attr, radio_button_id_prefix, click_selectors);
    $('.driving-data').click(enableUploadInput);
    enableUploadInput();
});