var download = function(model_run_id, output, period, year, format) {
    var base_url = "/dataset/download";
    var query_string_template = "?model_run_id={model_run_id}&output={output}&period={period}&year={year}&format={format}";
    var query_string = query_string_template.replace(/{model_run_id}/g, model_run_id)
                                            .replace(/{output}/g, output)
                                            .replace(/{period}/g, period)
                                            .replace(/{year}/g, year)
                                            .replace(/{format}/g, format);
    var url = base_url + query_string;
    // First check to see if the file exists:
    $.ajax({
        url:url,
        type:'HEAD',
        error: function()
        {
            alert("Error downloading file - is this a valid year?");
        },
        success: function()
        {
            window.open(url, '_self');
        }
    });
}

var changeFormat = function() {
    var chosen_format = $(this).text();
    $('span#dl-format').text(chosen_format);
    $('span.link-format').text(chosen_format);
}

var changeYear = function() {
    var year = $('input#year').val();
    var year_text = year + ")";
    $('span.link-single-year').text(year_text);
}

$(document).ready(function() {
    $("a.dl-link").click(function() {
        var model_run_id = $(this).data("model_run_id");
        var output = $(this).data("output");
        var period = $(this).data("period");
        var year = $('#year').val();
        var format = $('span#dl-format').text();
        download(model_run_id, output, period, year, format);
    });

    $("a.dl-format").click(changeFormat);
    $("input#year").keyup(changeYear);
});