var link_templ = "<p class='qlink'><a href={url}>{text}</a></p>";

var add_link = function() {
    var id = $(this).attr("id");
    var url = '#' + id;
    var text = $(this).find(".q").text();
    var fragment = link_templ.replace(/{url}/g, url).replace(/{text}/g, text);
    $('#links').append(fragment);
}

$(document).ready(function() {
    $(".qa").each(add_link);
});

