/*
 * Prepare the Model run Submit page (submit.html).
 */

$(document).ready(function() {
     /**
      * Set the height of the 'edit' divs on the left to match the larger div containing the summmary text
      */
     $('div.page-group').each(function(index) {
            var id = $(this).attr("id");
            var edit_div = $('#edit-' + id);
            var height = $(this).parent().height();
            edit_div.height(height);
        });

    // Set the click handler for the rows
    $('.summary').click(function() {
        var url = $(this).find('a').attr('href');
        window.location = (url);
    });
});
