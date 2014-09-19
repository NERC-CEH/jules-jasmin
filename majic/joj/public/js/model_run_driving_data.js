var id_attr = 'dsid';
var radio_button_id_prefix = '#driving_dataset_';
var click_selectors = 'tr.driving-data';

var openUploadPanel = function() {
    var userUploadRadio = $('input[user_upload="true"]');
    if (userUploadRadio.is(':checked')) {
        if ($('#form-driving-data').find('p.alert-warning').length) {
            $('#collapse1').collapse('show');
        }
    } else {
        $('#collapse1').collapse('hide');
    }
}

var showUploadPanel = function() {
    if ($('#form-driving-data').find('p.alert-warning').length) {
        $('#collapse1').collapse('show');
    }
}

var hideUploadPanel = function() {
    $('#collapse1').collapse('hide');
}

var setUploadPanelClicks = function() {
    var ddInputs = $('input.driving-data-input');
    var nonUploadInputs = ddInputs.not('[user_upload="true"]');
    var uploadInput = ddInputs.filter('input[user_upload="true"]');
    nonUploadInputs.each(function() {
        var row = $(this).closest('tr');
        row.click(hideUploadPanel);
    })
    uploadInput.closest('tr').click(showUploadPanel);
}

/*
 * Prepare the Model run Driving data page (driving_data.html).
 */
$(document).ready(function() {
    EcomapsGeneral.initialise_custom_checkboxes(id_attr, radio_button_id_prefix, click_selectors);
    $('#collapse1').collapse({'toggle': false})
    setUploadPanelClicks();
    openUploadPanel();
});