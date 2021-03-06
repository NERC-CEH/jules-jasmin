var LINE_HEIGHT = 26.0; // This specifies the height of a line in the floating results div
var KEY_CODE_UP = 38;
var KEY_CODE_DOWN = 40;
var KEY_CODE_ENTER = 13;
var should_show_results = false; // This is used to keep track of whether or not the floating results div should be shown
                                 // since IE doesn't handle blur events involving scroll bars nicely.
var mouse_hover_active = true; // We sometimes need to disable mouse hover on the results list (so that you can scroll
                               // with the up/down keys without mouse hover events getting in the way

function getName(id) {
    var name = $("#name_" + id)
    return name.text();
};

function getDesc(id) {
    var desc = $("#desc_" + id)
    return desc.text();
};

/**
 * Search the output_variables for a string
 * @param searchText: The text to search for
 * @return: list of matching output variable IDs
 */
function search(searchText) {
    // Get a list of all available IDs
	var ids = [];
    var output_row_prefix = "output_row_";
    $("div[id^=" + output_row_prefix + "]").each(function(index) {
        var id = $(this).attr("id");
        id = id.split(output_row_prefix)[1];
        ids.push(id);
    });
	// Add any matching output variables to the results list
    var results = [];
	searchText = searchText.toLowerCase();
    for (var i=0; i < ids.length; i++)
    {
        id = ids[i];
        if (getName(id).toLowerCase().indexOf(searchText) != -1 || getDesc(id).toLowerCase().indexOf(searchText) != -1 ) {
            results.push(id);
        }
    }
    return results.sort();
}

/**
 * Display a list of results in the autocomplete drop-down
 * @param results: List of matching output variable IDs
 */
function displayResults(results) {
    var res = $("#results");
    res.empty();
    for (var i=0; i < results.length; i++)
    {
        var id = results[i];
        var html = "<li class='res-list result' title='" + getDesc(id) + "' value=" + id + ">" + getName(id) + " - " + "<i>" + getDesc(id) + "</i></li>";
        res.append(html);
    }
    res.width($("#input-bar").width() -2);
    $(".result").click(addOutput);
    $(".result").hover(resultHoverOn, resultHoverOff);
    n_lines = Math.min(results.length, 10)
    res.height(27 * n_lines + "px");
    res.show();
    $("#results").scrollTop(0);
}
/**
 * Set this result list item to 'hovered'
 */
resultHoverOn = function () {
    if (mouse_hover_active) {
        $(".result").removeClass("hovered");
        $(this).addClass("hovered");
    }
}

/**
 * Hover-off function for a result
 */
resultHoverOff = function () {
    if (mouse_hover_active) {
        $(this).removeClass("hovered");
    }
}

/**
 * Display a message in the autocomplete dropdown indicating that no matches could be found
 */
function displayNoMatches(searchText) {
    var res = $("#results");
    var html = "<li class='res-list'>No matches found for '" + searchText + "'</li>"
    res.empty();
    res.append(html);
    res.width($("#input-bar").width() -2);
    res.height("27px");
    res.show();
}

/**
 * Add an output variable to the selected outputs 
 */
addOutput = function() {
    var id = $(this).val();
    $("#ov_select_" + id).prop('checked', true);
    var output_row = $("#output_row_" + id);
    $('#output_rows').prepend($("#output_row_" + id));
    output_row.show();
    hideResults();
}

/**
 * Remove a selected output from the screen and deselect the form element
 */
removeOutput = function () {
    var id = $(this).attr("ov-id");
    $("#ov_select_" + id).prop('checked', false);
    $("#output_row_" + id).slideUp()
}

/**
 * Hide the autocomplete results list
 */
hideResults = function () {
    var res = $("#results");
    res.hide();
}

/** 
 * When the text in the autocomplete box is changed this function updates the autocomplete drop down
 */
autoComplete = function () {
    var searchText = $("#autoText").val();
    var results = search(searchText);
    if (results.length === 0) {
        displayNoMatches(searchText);
        return;
    }
    displayResults(results);
}

/** 
 * This processes a key press in the autocomplete text box. Up or down keys move the selected (hovered) list item as you would expect,
 * with a bit of extra code to make sure that it copes with wrap arounds to the top / bottom of the list and to sort out the 
 */
autoKeyPress = function (e) {
    	mouse_hover_active = false; // If we're using keys we don't want the mouse to trigger hover events on scroll.
    	var code = (e.keyCode ? e.keyCode : e.which);
    	// DOWN
    	if (code === KEY_CODE_DOWN) {
			// Select the first result if none currently selected
    		if ($(".result.hovered").length === 0) {
    			$("#results li").first().addClass("hovered");
    		} else {
                $(".result.hovered").first().removeClass("hovered").next().addClass("hovered");
    		    if (typeof($(".result.hovered").val()) != 'undefined') {
                    var position = $(".result.hovered").index();
                    // Check if we are at the bottom of the scrollbox
                    if (((position+1) * LINE_HEIGHT) > $("#results").scrollTop() + $("#results").height() ) {
                        $("#results").scrollTop(LINE_HEIGHT * (position+1) - $("#results").height());
                    }
    		    } else {
    		        $("#results").scrollTop(0);
    		        $(".result.hovered").removeClass("hovered");
    		        $(".result").first().addClass("hovered");
    		    }
    		}
    	// UP
    	} else if (code === KEY_CODE_UP) {
			// Select the last result if none currently selected (and scroll to it)
            if ($(".result.hovered").length === 0) {
    			$("#results li").last().addClass("hovered");
    			$("#results").scrollTop($("#results")[0].scrollHeight);
    		} else {
                var position = $(".result.hovered").index();
    		    // Check if we are at the top of the scrollbox and adjust the scroll
                if (((position-1) * LINE_HEIGHT) < $("#results").scrollTop() ) {
                    $("#results").scrollTop((position-1) * LINE_HEIGHT);
                }
				// Select the next item up
                $(".result.hovered").first().removeClass("hovered").prev().addClass("hovered");
                // Wrap round and scroll
				if (position === 0) {
                    $("#results").scrollTop($("#results")[0].scrollHeight);
    		        $(".result.hovered").removeClass("hovered");
    		        $(".result").last().addClass("hovered");
                }


    		}
        // ENTER
        } else if(code === KEY_CODE_ENTER) {
    		if($(".result.hovered").length > 0){
    			$(".result.hovered").first().click();
    			$("#autoText").blur()
    		}
    	} else {
    	        autoComplete();
    	}

    }

/** 
 * This function is called after page load to initialise all of the required handlers
 */
initHandlers = function () {
    $(".remove_output_var").click(removeOutput);
    var autoText = $("#autoText");
    autoText.keyup(autoKeyPress);
    autoText.focus(autoComplete);
    var inputBtn = $("#input-bar-btn");
    inputBtn.click(autoComplete);

    // We need to keep track of where a mouse click occurs so we know whether to blur or not.
    $("#results, #autoText, #input-bar-btn").mouseenter(function() {
        should_show_results = true;
    }).mouseleave(function() {
        should_show_results = false;
    });

    // If a mouse click occurs outside of the results box, button or drop-down, then hide the results.
    $('body').click(function() {
        if (!should_show_results) {
            hideResults();
        }
    });

    // If the user moves the mouse over the result function we reactivate mouse hover of results.
    $('#results').mousemove(function() {
        mouse_hover_active = true;
    });
}