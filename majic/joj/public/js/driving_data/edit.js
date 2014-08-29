

/* show the correct parameters list for the selected namelist*/
function update_namelist_showing()
{
    selected_namelist = $('#namelists').val();
    $(".parameters").hide();
    $("#namelist_" + selected_namelist).show();
}

function add_list_item(mask_template, count_input_id, controls_id) {
    count = $('#' + count_input_id).val();
    count = parseInt(count) + 1;
    $('#' + count_input_id).val(count);
    $("#" + controls_id).after(mask_template.replace(/%template%/g, count));
    $("#" + controls_id).parent().find(".fa-times-circle").first().click(delete_line);
}

/* Add a mask line*/
function add_mask()
{
    mask_template = '<div class="controls-row"> \
            <div class="span3"> \
                <input id="id_%template%" name="id_%template%" placeholder="Category" type="hidden" value="" /> \
                <input id="category_%template%" name="category_%template%" placeholder="Category" type="text" value="" /> \
            </div> \
            <div class="span3"> \
                <input id="name_%template%" name="name_%template%" placeholder="Name" type="text" value="" /> \
            </div> \
            <div class="span5"> \
                <input id="path_%template%" name="path_%template%" placeholder="data/filepath/filename.nc" type="text" value="" /> \
            </div> \
        </div>';
    add_list_item(mask_template, "mask_count", "mask_header");
}

/* function to delete a line from a list*/
function delete_line(event)
{
    $(event.currentTarget).parent().remove();
}

/* function to add a variable to the driving data set*/
function add_variable()
{
    var_template = ' \
    <div class="controls-row"> \
            <input class="span2" id="drive_vars_%template%" name="drive_vars_%template%" placeholder="Variable" type="text" value="" /> \
            <input class="span2" id="drive_var_names_%template%" name="drive_var_names_%template%" placeholder="Variable name" type="text" value="" /> \
            <input class="span2" id="drive_var_templates_%template%" name="drive_var_templates_%template%" placeholder="Template name" type="text" value="" /> \
            <input class="span2" id="drive_var_interps_%template%" name="drive_var_interps_%template%" placeholder="Interpolation" type="text" value="" /> \
            <input id="drive_var_is_deleted_%template%" name="drive_var_is_deleted_%template%" type="hidden" value="" /> \
            <i class="fa fa-times-circle fa-2x ico red span1" onclick="delete_line(this)"></i> \
    </div>';
    add_list_item(var_template, "drive_nvars", "drive_vars_header");
}

/* function to add a parameter to the extra parameters */
function add_parameter()
{
    param_template = ' \
    <div class="controls-row"> \
        <span class="span5"> \
            %name% \
            <input type="hidden" value="%id%" name="param_id_%template%" id="param_id_%template%" /> \
        </span> \
        <input type="text" value="" placeholder="Fortran namelist value" name="param_value_%template%" id="param_value_%template%" class="span5" /> \
        <i class="fa fa-times-circle fa-2x ico red span1"></i> \
    </div>';

    selected_namelist = $('#namelists').val();
    param_name = selected_namelist + "::" + $("#namelist_" + selected_namelist + " option:selected").text();
    param_id = $("#namelist_" + selected_namelist).val();

    template = param_template.replace(/%name%/g, param_name)
    template = template.replace(/%id%/g, param_id )
    add_list_item(template, "params_count", "parameters_header");
}

/* initialise name list and setup click and change functions*/
$(function ()
  {
    update_namelist_showing();
    $("#namelists").change(update_namelist_showing);
    $("#add_mask").click(add_mask);
    $("#add_variable").click(add_variable);
    $("#add_parameter").click(add_parameter);
    $(".fa-times-circle").click(delete_line);
  })

