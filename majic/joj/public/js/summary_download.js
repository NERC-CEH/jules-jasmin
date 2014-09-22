var createUrl = function(model_run_id, output, period, year, format) {
    var base_url = "/dataset/download";
    var query_string_template = "?model_run_id={model_run_id}&output={output}&period={period}&year={year}&format={format}";
    var query_string = query_string_template.replace(/{model_run_id}/g, model_run_id)
                                            .replace(/{output}/g, output)
                                            .replace(/{period}/g, period)
                                            .replace(/{year}/g, year)
                                            .replace(/{format}/g, format);
    return base_url + query_string;
}

var updateHrefs = function() {
    $("a.dl-link").each(function() {
        var model_run_id = $(this).data("model_run_id");
        var output = $(this).data("output");
        var period = $(this).data("period");
        var yearBox = $('#year');
        var year = '';
        if (yearBox.length) {
            year = yearBox.val();
        }
        var format = $('span#dl-format').text();
        var url = createUrl(model_run_id, output, period, year, format);
        $(this).attr('href', url);
    });
}

var changeFormat = function() {
    var chosen_format = $(this).text();
    $('span#dl-format').text(chosen_format);
    $('span.link-format').text(chosen_format);
    updateHrefs();
}

var changeYear = function() {
    var year = $('input#year').val();
    var year_text = year + ")";
    $('span.link-single-year').text(year_text);
    updateHrefs();
}

$(document).ready(function() {
    updateHrefs();
    $("a.dl-format").click(changeFormat);
    $("input#year").keyup(changeYear);
});