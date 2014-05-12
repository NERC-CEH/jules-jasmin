/**
 * Created by Phil Jenkins (Tessella) on 11 Mar 2014.
 *
 * Functions for the "Create Analysis" page
 */

var EcomapsCreateAnalysis = (function() {

    var selectedColumns = new Object();

    var initHandlers = function(){
        $("select#coverage_dataset_ids").change(refreshTimeSelectors);

        // Error span swap
        $("span.help-inline").each(function(index, el){

            // Find the parent control group
            // Swap the message with the input
            $(el).insertAfter($(el).next());
            $(el).closest("div.control-group").addClass("error");
        });

        // Set up handler for changing point dataset value
        $("select#point_dataset_id").change(function(){

            updatePointDatasetColumns($(this).val());
        });

        //
        $("a#dataset-preview-open").click(function() {
            $("div#dataset-preview").html("<div class='modal-body'>Loading preview <img src='/layout/images/loading7.gif' /></div>");
            $("div#dataset-preview").load("/dataset/preview/" + $("select#point_dataset_id").val());
        });

        $("i[data-toggle='tooltip']").tooltip();

        // Populate the lists based on the currently-selected point dataset
        updatePointDatasetColumns($("select#point_dataset_id option:selected").val());

    };

    var refreshTimeSelectors = function(){

        var selections = $(this).val();

        if(selections) {
            for(var i=0; i < selections.length; i++){

                // Do we already have an entry
                var columnValue = selections[i];

                if(!selectedColumns[columnValue]){
                    selectedColumns[columnValue] = true;

                    var selectionParts = columnValue.split("_");
                    var dsId = selectionParts[0];
                    var col = selectionParts[1];

                    $.get("/dataset/timeselection/" + dsId + "?col=" + col, function(data){

                        $("div#time-point-container").append(data);
                    });
                }
            }
        }

        for(var column in selectedColumns) {
            if(selections.indexOf(column) < 0) {
                delete selectedColumns[column];
            }
        }

        $("div.time-selector").each(function(){
            if(!selectedColumns.hasOwnProperty($(this).data("columnid"))){
                $(this).remove();
            }
        });
    };

    var populateVariableList = function(listId, options, selectedValue, defaultValue) {

        listId = "#" + listId;

        $(listId).attr("disabled", false);
        $(listId).empty();

        if (selectedValue === ''){
            for(var i=0; i<options.length; i++) {
                $(listId).append($("<option></option>")
                    .val(options[i])
                    .text(options[i])
                    .attr("selected", options[i] === defaultValue ? 'selected' : undefined));

            }
        }
        else{
             for(var i=0; i<options.length; i++) {
                $(listId).append($("<option></option>")
                    .val(options[i])
                    .text(options[i])
                    .attr("selected", options[i] === selectedValue ? 'selected' : undefined));

            }
        }

    };

    /* updatePointDatasetColumns
    *
    *   Provides a facility for populating the model parameter dropdowns
    *   based on the point dataset chosen
    *
    */
    var updatePointDatasetColumns = function(dataset_id) {

        $("select.model-param").each(function(index){
            $(this).empty();
            $(this).append($("<option></option>").text("Loading..."));
            $(this).attr("disabled", true);
        });
        jQuery.support.cors = true;
        $.ajax({
            url : "/dataset/columns/" + dataset_id,
            success: function(data) {
                // Populate each list we know of

                // Time
                populateVariableList("unit_of_time", data, $("input#unit_of_time_value").val(), 'year');

                // Group by
                populateVariableList("random_group", data, $("input#random_group_value").val(), 'SERIES_NUM');

                // Model Var
                populateVariableList("model_variable", data, $("input#model_variable_value").val(), 'loi');
            },
            error: function(xhr, status, error) {
                 alert(status);
               },
            dataType: 'json'
        });
    };

    return {
        /*
         * init
         *
         * Initialisation function, sets up the module
         *
         */
        init: function(){
            initHandlers();
        }
    }
})();
$(function() {
        EcomapsCreateAnalysis.init();
    }
);
