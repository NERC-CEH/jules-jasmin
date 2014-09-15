

/* show the correct parameters list for the selected namelist*/
function update_namelist_showing()
{
    selected_namelist = $('#namelists').val();
    $(".parameters").hide();
    $("#namelist_" + selected_namelist).show();
}

function add_list_item(mask_template, count_input_id, controls_id) {
    count = $('#' + count_input_id).val();
    $("#" + controls_id).after(mask_template.replace(/%template%/g, count));
    $("#" + controls_id).parent().find(".fa-times-circle").first().click(delete_line);
    count = parseInt(count) + 1;
    $('#' + count_input_id).val(count);
}

/* Add a mask line*/
function add_mask()
{
    mask_template = ' \
        <div class="controls-row"> \
            <input id="region-%template%.id" name="region-%template%.id" placeholder="Category" type="hidden" value="" /> \
            <input id="region-%template%.category" name="region-%template%.category" placeholder="Category" type="text" value="" class="span3"/> \
            <input id="region-%template%.name" name="region-%template%.name" placeholder="Name" type="text" value="" class="span3"/> \
            <input id="region-%template%.path" name="region-%template%.path" placeholder="data/filepath/filename.nc" type="text" value="" class="span3"/> \
            <i class="fa fa-times-circle fa-2x ico red span1"></i> \
        </div>';

    add_list_item(mask_template, "mask_count", "mask_header");
}

/* function to delete a line from a list*/
function delete_line(event)
{
    $(event.currentTarget).parent().next('.error_block').remove();
    $(event.currentTarget).parent().remove();
}

/* function to add a variable to the driving data set*/
function add_variable()
{
    var_template = ' \
    <div class="controls-row"> \
            <input class="span2" id="drive_var_-%template%.vars" name="drive_var_-%template%.vars" placeholder="Variable" type="text" value="" /> \
            <input class="span2" id="drive_var_-%template%.names" name="drive_var_-%template%.names" placeholder="Variable name" type="text" value="" /> \
            <input class="span2" id="drive_var_-%template%.templates" name="drive_var_-%template%.templates" placeholder="Template name" type="text" value="" /> \
            <input class="span2" id="drive_var_-%template%.interps" name="drive_var_-%template%.interps" placeholder="Interpolation" type="text" value="" /> \
            <i class="fa fa-times-circle fa-2x ico red span1"></i> \
    </div>';
    add_list_item(var_template, "drive_nvars", "drive_vars_header");
}

/* function to add a parameter to the extra parameters */
function add_parameter()
{
    param_template = ' \
    <div class="controls-row"> \
        <span class="span4"> \
            %name% \
            <input type="hidden" value="%id%" name="param-%template%.id" id="param-%template%.id" /> \
        </span> \
        <input type="text" value="" placeholder="Fortran namelist value" name="param-%template%.value" id="param-%template%.value" class="span4" /> \
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

