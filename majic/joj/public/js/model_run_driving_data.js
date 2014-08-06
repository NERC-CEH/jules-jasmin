var id_attr = 'dsid';
var radio_button_id_prefix = '#driving_dataset_';
var click_selectors = 'tr.driving-data';

var enableDownloadButton = function() {
    var uploadInput = $('#downloadBtn');
    var userUploadRadio = $('input[user_upload="true"]');
    if (userUploadRadio.is(':checked')) {
        uploadInput.prop('disabled', true);
        uploadInput.addClass('disabled');
        uploadInput.attr("title", "You must select a Majic driving data from the list above before you can download");
    } else {
        uploadInput.prop('disabled', false);
        uploadInput.removeClass('disabled');
        uploadInput.removeAttr("title");
    }
}

/*
 * Prepare the Model run Driving data page (driving_data.html).
 */
$(document).ready(function() {
    EcomapsGeneral.initialise_custom_checkboxes(id_attr, radio_button_id_prefix, click_selectors);
    $('.driving-data').click(enableDownloadButton);
    enableDownloadButton();

    $('#uploadBtn, #downloadBtn').click(function() {
        if (!$(this).hasClass('disabled')) {
            $('.error-message').hide()
        }
    })
});