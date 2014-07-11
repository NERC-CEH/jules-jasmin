/*
 * Prepare the Model run Driving data page (driving_data.html).
 */
$(document).ready(function() {
    /*
     * Identify which tick box icons should be visible based on the underlying radio buttons
     */
    setCorrectChecks = function() {
        checks = $('.select-icon').each(function() {
            dsid = $(this).attr("dsid");
            select = $('#driving_dataset_' + dsid);
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
    $('.select-icon, tr.driving-data').click(function() {
        dsid = $(this).attr("dsid");
        $('input').prop('checked', false);
        select = $('#driving_dataset_' + dsid);
        select.prop('checked', true);
        setCorrectChecks();
    });
});