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

       /**
         * Function to use on hover over a row
         */
        editHoverOn = function () {
            $(this).find('.edit').addClass('edit-hover');
            $(this).find('.page-group').addClass('page-group-hover');
        }

        /**
         * Function to use on hover off of a row
         */
        editHoverOff = function () {
            $(this).find('.edit').removeClass('edit-hover');
            $(this).find('.page-group').removeClass('page-group-hover');
        }

        /**
         * Add the hover on, hover off effects to the rows
         */
        $('.row').hover(editHoverOn, editHoverOff);
});
