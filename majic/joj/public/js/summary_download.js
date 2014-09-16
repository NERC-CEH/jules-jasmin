var download = function(model_run_id, output, period, year) {
    var base_url = "/dataset/download";
    var query_string_template = "?model_run_id={model_run_id}&output={output}&period={period}&year={year}";
    var query_string = query_string_template.replace(/{model_run_id}/g, model_run_id)
                                            .replace(/{output}/g, output)
                                            .replace(/{period}/g, period)
                                            .replace(/{year}/g, year);
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

    //
}

$(document).ready(function() {
    $("a.dl-link").click(function() {
        var model_run_id = $(this).data("model_run_id");
        var output = $(this).data("output");
        var period = $(this).data("period");
        var year = $('#year').val();
        download(model_run_id, output, period, year);
    });
});