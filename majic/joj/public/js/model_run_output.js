function getName(id) {
    var name = $("#name_" + id)
    return name.text();
};

function getDesc(id) {
    var desc = $("#desc_" + id)
    return desc.text();
};

function search(searchText) {
    var ids = [];
    var output_var_prefix = "output_var_";
    $("tr[id^=" + output_var_prefix + "]").each(function(index) {
        var id = $(this).attr("id");
        id = id.split(output_var_prefix)[1];
        ids.push(id);
    });
    var results = [];
    for (var i=0; i < ids.length; i++)
    {
        id = ids[i];
        if (getName(id).indexOf(searchText) != -1 || getDesc(id).indexOf(searchText) != -1 ) {
            results.push(id);
        }
    }
    return results;
}


function displayResults(results) {

    var res = $("#results");
    res.empty();
    for (var i=0; i < results.length; i++)
    {
        var id = results[i];
        var html = "<li class='res-list result' title='" + getDesc(id) + "' value=" + id + "><b>" + getName(id) + "</b>" + " - " + getDesc(id) + "</li>";
        res.append(html);
    }
    res.width($("#input-bar").width() -2);
    $(".result").mousedown(addOutput);
    $(".result").hover(resultHoverOn, resultHoverOff);
    n_lines = Math.min(results.length, 10)
    res.height(27 * n_lines + "px");
    res.show();
    $("#results").scrollTop(0);
}

resultHoverOn = function () {
    $(".result").removeClass("hovered");
    $(this).addClass("hovered");
}

resultHoverOff = function () {
    $(this).removeClass("hovered");
}

function displayNoMatches(searchText) {
    var res = $("#results");
    var html = "<li class='res-list'>No matches found for '" + searchText + "'</li>"
    res.empty();
    res.append(html);
    res.width($("#input-bar").width() -2);
    res.height("27px");
    res.show();
}

addOutput = function() {
    var id = $(this).val();
    $("#ov_select_" + id).prop('checked', true);
    $("#output_row_" + id).show();
    hideResults();
}

removeOutput = function () {
    var id = $(this).attr("ov-id");
    $("#ov_select_" + id).prop('checked', false);
    $("#output_row_" + id).slideUp()
}

hideResults = function () {
    var res = $("#results");
    res.hide();
}

autoComplete = function () {
    searchText = $("#autoText").val();
    results = search(searchText);
    if (results.length == 0) {
        displayNoMatches(searchText);
        return;
    }
    displayResults(results);
}

autoKeyPress = function (e) {
    	var code = (e.keyCode ? e.keyCode : e.which);

    	// DOWN
    	if (code == 40) {
    		if ($(".result.hovered").length == 0) {
    			$("#results li").first().addClass("hovered");
    		} else {
                $(".result.hovered").first().removeClass("hovered").next().addClass("hovered");
    		    if (typeof($(".result.hovered").val()) != 'undefined') {
                    var position = $(".result.hovered").index();
                    // Check if we are at the bottom of the scrollbox
                    if (((position+1) * 26.5) > $("#results").scrollTop() + $("#results").height() ) {
                        $("#results").scrollTop(26.5 * (position+1) - $("#results").height());
                    }
    		    } else {
    		        $("#results").scrollTop(0);
    		        $(".result.hovered").removeClass("hovered");
    		        $(".result").first().addClass("hovered");
    		    }

    		}
    	// UP
    	} else if(code == 38) {
            if ($(".result.hovered").length == 0) {
    			$("#results li").last().addClass("hovered");
    			$("#results").scrollTop($("#results")[0].scrollHeight);
    		} else {
                var position = $(".result.hovered").index();
    		    // Check if we are at the top of the scrollbox
                if (((position-1) * 26.5) < $("#results").scrollTop() ) {
                    $("#results").scrollTop((position-1) * 26.5);
                }
                $(".result.hovered").first().removeClass("hovered").prev().addClass("hovered");
                if (position == 0) {
                    $("#results").scrollTop($("#results").height());
    		        $(".result.hovered").removeClass("hovered");
    		        $(".result").last().addClass("hovered");
                }


    		}
        // ENTER
        } else if(code == 13) {
    		if($(".result.hovered").length > 0){
    			$(".result.hovered").first().mousedown();
    		}
    	} else {
    	        autoComplete();
    	}

    }

initHandlers = function () {
    $(".remove_output_var").click(removeOutput);
    var autoText = $("#autoText");
    autoText.keyup(autoKeyPress);
    autoText.blur(hideResults);
    autoText.focus(autoComplete);
    var inputBtn = $("#input-bar-btn");
    inputBtn.click(autoComplete);
    inputBtn.blur(hideResults);
}




