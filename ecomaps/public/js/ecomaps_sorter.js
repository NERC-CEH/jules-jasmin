/**
 * Created by Phil Jenkins on 3/4/14.
 */


var EcomapsSorter = (function() {

    var highlightSortedColumn = function(tableId, direction) {

    // Get table by ID
    var table = $("#" + tableId);

    var selectedColumn = table.data("sorting_column");

    // Loop over th elements
    $(table).find("th").each(function(){
        var columnName = $(this).data("column");

        if (selectedColumn == columnName){
            $(this).append(" ")

            // Add icon corresponding to direction of sorting
            if (typeof direction != "undefined" && direction == "asc"){
                $(this).append("<i class='icon-chevron-up'></i>");
            }
            else{
                $(this).append("<i class='icon-chevron-down'></i>");
            }
        };
    })

    };

    var getOrderDirection = function(tableId, previousSortingColumn, selectedColumnName){

        // Get table by ID
        var table = $("#" + tableId);

        var orderDirection = table.data("order_direction");


        // If the column name matches the one that was previously sorted on - reverse the direction of sorting
        if (typeof previousSortingColumn != "undefined" && previousSortingColumn == selectedColumnName){
            if (orderDirection == "asc"){
                var direction = "desc";
            }
            else{
                var direction = "asc";
            }
        }
        else{
            var direction = "asc";
        }

        return direction;

    };

    var constructAddressStringForSorting = function(tableHeader){
        // Function builds the address to redirect to depending on the column header that has been clicked.

        var table = $(tableHeader).closest("table");

        var tableId = $(table).get(0).id;

        var selectedColumnName = $(tableHeader).data("column");

        var previousSortingColumn = table.data("sorting_column");

        var direction = getOrderDirection(tableId ,selectedColumnName,previousSortingColumn);

        if (tableId == "public_analyses_table"){
            var isPublic = "true";
        }
        else{
            var isPublic = "false";
        }

        if(typeof table.data("filter") === 'undefined'){
            var filter = "";
        }
        else{
            var filter = table.data("filter");
        }

        var address = "/analysis/sort_and_filter/?column=" + selectedColumnName + "&order=" + direction + "&is_public=" + isPublic + "&filter_variable=" + filter;

        return{
            tableId : tableId,
            direction: direction,
            address : address
        }
    }

    var buildAddressStringForFiltering = function(selectId, tableId, isPublic){

            // Remove the whitespace around the filter value when it's extracted
            var filter = $("select#" + selectId).val().replace(/ /g,'');

            var table = $("#" + tableId);
            var column = table.data("sorting_column");
            var order = table.data("order_direction");

            var address = "/analysis/sort_and_filter/?column=" + column + "&order=" + order + "&is_public=" + isPublic + "&filter_variable=" + filter;

            return{
                direction: order,
                address: address
            }
    };

    var initSortables = function() {

        $("div#private-container").on("click", "th", function(){

            var result = constructAddressStringForSorting($(this));

            $("div#private-container").load(result.address, function() {
                highlightSortedColumn(result.tableId,result.direction);
            });
        });

        $("div#public-container").on("click", "th", function(){

            var result = constructAddressStringForSorting($(this));

            $("div#public-container").load(result.address, function() {
                highlightSortedColumn(result.tableId,result.direction);
            });

        });

        $("#filter_private_button").click(function() {

            tableId = "private_analyses_table"

            var result = buildAddressStringForFiltering("private_filter_value", tableId, "false")

            $("div#private-container").load(result.address, function() {
                 highlightSortedColumn(tableId,result.direction);
            });
        });

        $("#filter_public_button").click(function() {

           tableId = "public_analyses_table"

            var result = buildAddressStringForFiltering("public_filter_value", tableId, "true")

            $("div#public-container").load(result.address, function() {
                highlightSortedColumn(tableId,result.direction);
            });
        });

         $("#undo_filter_private_button").click(function() {

            var address = "sort_and_filter/?column=analyses.name&order=asc&is_public=false"

            $("div#private-container").load(address, function() {

            });
        });

        $("#undo_filter_public_button").click(function() {

            var address = "sort_and_filter/?column=analyses.name&order=asc&is_public=true"

            $("div#public-container").load(address, function() {

            });
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
            initSortables();

            // Default view
            $("div#private-container").html("<div class='modal-body'>Loading data <img src='/layout/images/loading7.gif' /></div>");
            $("div#private-container").load("sort_and_filter/?column=analyses.name&order=asc&is_public=false");
            $("div#public-container").load("sort_and_filter/?column=analyses.name&order=asc&is_public=true");
        }
    }
})();
$(function() {
        EcomapsSorter.init();
    }
);