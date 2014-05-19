/**
 * Created by Phil Jenkins (Tessella) on 2/12/14.
 *
 * This module provides progress reporting on an analysis run being performed
 */

;var ECOMAPS = {};

(function($) {

    var analysis_id = 0;
    var previousMessage = "";
    var dotCounter = 0;

    /**
     *  makeProgressRequest
     *
     *  Requests an update from the server on an analysis progress
     *
     *  @param id - ID of the analysis to check up on
     */
    var makeProgressRequest = function(id) {

        analysis_id = id;

        $.get("/analysis/progress/" + analysis_id,
            progressUpdateComplete,
            "json")
    };

    /**
     *  setProgressMessage
     *
     *  Updates our UI with the response from the server
     *
     * @param message - Message to set in the UI
     */
    var setProgressMessage = function(message) {

        previousMessage = message;

        $("ul#progress > li > i.icon-tasks").attr('class', 'icon-ok');
        $("ul#progress > li").attr('class', 'done');

        var newProgressItem = getInProgressItem(message);

        $("ul#progress").append(newProgressItem);
        newProgressItem.show("normal");
    };

    var getInProgressItem = function(message){
        return $("<li><i class='icon-tasks'></i>" + message + "</li>");
    };

    /**
     * progressUpdateComplete
     *
     * Callback function to handle a response to our progress request
     *
     * @param data - The JSON response from the server
     */
    var progressUpdateComplete = function(data) {

        // Are we done yet?
        if(!data.complete) {

            // Just update on progress
            if(data.message !== previousMessage) {

                setProgressMessage(data.message);
            }
            else {
                // If we've not moved to a new message, just indicate that something is happening
                if(dotCounter < 10) {
                    $("ul#progress li").last().append(".");
                    dotCounter++;
                }
                else {
                    $("ul#progress li").last().html(getInProgressItem(data.message).html());
                    dotCounter = 0;
                }
            }

            // Let's wait a few seconds to see what's happening
            window.setTimeout(function(){

                makeProgressRequest(analysis_id);

            }, 5000);
        }
        else {

            // All done!
            setProgressMessage(data.message + " - redirecting to results");

            window.setTimeout(function() {

                window.location.href = '/analysis/view/' + analysis_id;

            }, 5000);
        }
    };


    ECOMAPS.ANALYSIS = {
        /**
         *    Gets the progress message for the specified analysis
         *
         *    @param id - ID of the analysis to get progress for
         */
        getProgress: function(id)
        {
            makeProgressRequest(id);
        }
    }
})(jQuery);