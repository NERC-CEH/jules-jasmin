/**
 * Created by Phil Jenkins (Tessella) on 2/27/14.
 *
 * General functions to call on every EcoMaps page
 */

var EcomapsGeneral = (function() {

    /*
    * testMapServer
    *
    * Checks that the map server defined on the server side can be roused.
    * Will change the status message depending on the result
    *
    */
    var testMapServer = function() {

        // Set up the bits we need
        var statusMessage = $("#status-message");
        var dots = "";

        // In order to make the message stay still, we can pad out with spaces
        var spaces = cur_spaces = "&nbsp;&nbsp;&nbsp;";

        // Reset the message
        statusMessage.html("Testing" + dots + spaces).attr("class", "label");

        var loaderId = window.setInterval(function() {

            // Spin the dot effect while we wait...

            if(dots.length === 3) {
                dots = "";
                cur_spaces = spaces;
            }
            else {

                dots += ".";

                // 6 = the length of &nbsp;
                cur_spaces = spaces.substring(0, spaces.length-(6*dots.length));
            }

            statusMessage.html("Testing" + dots + cur_spaces);

        }, 500);

        $.get('/map/test/', function(serverOK){

            var cls, message = "";

            // Should be a straight true or false response
            if(serverOK) {
                message = "OK";
                cls= 'success';
                $("#server-offline").hide();
            }
            else {
                message = "Offline";
                cls = 'important';
                $("#server-offline").show("fast");
            }

            // Stop the spinning
            window.clearInterval(loaderId);
            statusMessage.html(message).attr('class', 'label label-' + cls);
        });
    };

    /*
     * Find all forms with the attribute data-confirm and add an on submit method
     *  which shows a confirm box with the text given in the attribute
     */
    var confirmSubmit = function () {
        $("[data-confirm]").submit(
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
            testMapServer();

            window.setInterval(testMapServer, 30000);
        },

        initialise_custom_checkboxes: initialise_custom_checkboxes
    }
})();
$(function() {
        EcomapsGeneral.init();
    }
);