var id_attr = 'site';
var radio_button_id_prefix = '#site_';
var click_selectors = '.select-div, .description-div';

/*
 * Prepare the Extents page (extents.html).
 */
$(document).ready(function() {
    EcomapsGeneral.initialise_custom_checkboxes(id_attr, radio_button_id_prefix, click_selectors);

    var page_load = true;

    var chooseMultiCell = function () {
        var singleCell = $('#single-cell');
        var multiCell = $('#multi-cell')
        singleCell.find('input').prop('disabled', true);
        if (page_load) {
            singleCell.hide();
        } else {
            singleCell.slideUp()
        }
        multiCell.find('input').prop('disabled', false);
        multiCell.show();
        page_load = false;
    }

    var chooseSingleCell = function () {
        var singleCell = $('#single-cell');
        var multiCell = $('#multi-cell')
        singleCell.find('input').prop('disabled', false);
        singleCell.show();
        multiCell.find('input').prop('disabled', true);
        if (page_load) {
            multiCell.hide();
        } else {
            multiCell.slideUp()
        }
        page_load = false;
    }

    var updatePageFromSelect = function() {
        var selected = $('input[id^="site_"]:checked');
        if (selected.attr('id') === 'site_multi') {
            chooseMultiCell();
        } else {
            chooseSingleCell();
        }
    }

    // Add handlers for click events:
    $(click_selectors).click(updatePageFromSelect);
    // Call this once to set up the page correctly
    updatePageFromSelect();

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

    $('#check_av').click(toggleAverageCheckBox);
    $('#average_over_cell').change(updateCheckBoxIcon);
    updateCheckBoxIcon();
});