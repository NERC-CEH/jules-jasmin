/*
 * Prepare the Model run Create page (create.html).
 */
$(document).ready(function() {
    /*
     * Identify which tick box icons should be visible based on the underlying radio buttons
     */
    setCorrectChecks = function() {
        checks = $('.select-icon').each(function() {
            configid = $(this).attr("configid");
            select = $('#science_configuration_' + configid);
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

    // Add click handlers to select icons and div
    $('.select-icon, .description-div').click(function() {
        configid = $(this).attr("configid");
        $('input').prop('checked', false);
        select = $('#science_configuration_' + configid);
        select.prop('checked', true);
        setCorrectChecks();
    });
});