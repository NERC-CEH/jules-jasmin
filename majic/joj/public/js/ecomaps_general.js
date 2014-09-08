/**
 * Created by Phil Jenkins (Tessella) on 2/27/14.
 *
 * General functions to call on every EcoMaps page
 */

var EcomapsGeneral = (function() {

    /*
     * Find all forms with the attribute data-confirm and add an on submit method
     *  which shows a confirm box with the text given in the attribute
     */
    var confirmSubmit = function () {
        $("form[data-confirm]").submit(
            function(event) {
                message = $(this).attr('data-confirm')
                answer = confirm(message);
                if (!answer) {
                    event.preventDefault();
                }
            });
        $("button[data-confirm], a[data-confirm]").click(
            function(event) {
                message = $(this).attr('data-confirm')
                answer = confirm(message);
                if (!answer) {
                    event.preventDefault();
                }
            });
    };

    var initialise_custom_checkboxes = function(id_attr, radio_button_id_prefix, click_selectors) {
        /*
         * Identify which tick box icons should be visible based on the underlying radio buttons
         */
        setCorrectChecks = function() {
            checks = $('.select-icon').each(function() {
                id = $(this).attr(id_attr);
                select = $(radio_button_id_prefix + id);
                if (select.is(':checked')) {
                    $(this).removeClass('grey');
                    $(this).addClass('green');
                    $(this).removeClass('fa-circle-o');
                    $(this).addClass('fa-check-circle-o');
                } else {
                    $(this).addClass('grey');
                    $(this).removeClass('green');
                    $(this).addClass('fa-circle-o');
                    $(this).removeClass('fa-check-circle-o');
                }
            });
        }

    setCorrectChecks();

    // Add click handlers to select icons
    $(click_selectors).click(function() {
        id = $(this).attr(id_attr);
        $('input[id^="' + radio_button_id_prefix + '"]').prop('checked', false);
        select = $(radio_button_id_prefix + id);
        select.prop('checked', true);
        setCorrectChecks();
    });

    }

    return {
        /*
         * init
         *
         * Initialisation function, sets up the module
         *
         */
        init: function(){
            confirmSubmit();
        },

        initialise_custom_checkboxes: initialise_custom_checkboxes
    }
})();
$(function() {
        EcomapsGeneral.init();
        $('.fa-info-circle').popover({container: 'body'})
    }
);