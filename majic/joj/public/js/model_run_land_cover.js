// NOTE - any changes to this fragment MUST be copied through to the identical div in the land_cover.html template.
var fragment_string = '<div id="lc_action_{action_id}" class="lc-action-holder" action-id="{action_id}">\
                <span class="then">then</span>\
                <div class="lc-action">\
                    <i class="fa fa-arrows sort-icon"></i>&nbsp;&nbsp;\
                    Change <b>{region_name} ({cat_name})</b> to <b>{value_name}</b>\
                    <span class="pull-right"><i action-id="{action_id}" class="fa fa-times-circle remove-icon"></i></span>\
                    <input id="action_{action_id}_region" name="action_{action_id}_region" type="hidden" value="{region_id}"/>\
                    <input id="action_{action_id}_value" name="action_{action_id}_value" type="hidden" value="{value_id}"/>\
                    <input id="action_{action_id}_order" name="action_{action_id}_order" type="hidden" value="{order}"/>\
                </div>\
            </div>';

var get_action_id_to_add = function() {
    var action_ids = [];
    var actions = $('#actions-sortable').children()
    if (actions.length == 0) {
        return 1
    }
    actions.each(function() {
        var id = $(this).attr("action-id");
        action_ids.push(parseInt(id));
    })
    action_ids = action_ids.sort()
    return action_ids[action_ids.length -1] + 1
}

var add_action = function () {
    var action_id = get_action_id_to_add();
    var cat_id = $('#lc_cat').val()
    var cat_name  = $('#lc_cat option:selected').text()
    var region_id  = $('#lc_cat_' + cat_id + '_region').val()
    var region_name  = $('#lc_cat_' + cat_id + '_region option:selected').text()
    var value_id  = $('#lc_value').val()
    var value_name  = $('#lc_value option:selected').text()
    var order  = $('#actions-sortable').children().length + 1

    fragment = fragment_string.replace(/{action_id}/g, action_id).replace(/{region_name}/g, region_name)
                              .replace(/{region_id}/g, region_id).replace(/{cat_name}/g, cat_name)
                              .replace(/{value_name}/g, value_name).replace(/{value_id}/g, value_id)
                              .replace(/{order}/g, order)

    $('#actions-sortable').append(fragment);
    $('.remove-icon').click(remove_action); // Add click handlers for the new fragment
    show_or_hide_message();
}

var remove_action = function() {
    var action_id = $(this).attr("action-id");
    action = $("#lc_action_" + action_id);
    action.hide("slow", function(){
        action.remove();
        update_orders();
        show_or_hide_message();
    });
}

var update_orders = function(event, ui) {
    var action_ids = $('#actions-sortable').sortable('toArray');
    for (i=0; i < action_ids.length; ++i) {
        var action = $('#' + action_ids[i]);
        action.find('input[id*="order"]').val(i + 1);
    }
}

var change_categories = function() {
    var cat_id = $('#lc_cat option:selected').val()
    $('.lc_region').hide()
    $('#lc_cat_' + cat_id + '_region').show()
}

var show_or_hide_message= function() {
    message = $('#no-actions-message');
    if ($('#actions-sortable').children().length == 0) {
        message.show()
        //message.slideDown();
    } else {
        message.hide();
    }
}

$(document).ready(function() {
    $('#actions-sortable').sortable({activate: update_orders, update: update_orders});

    $('#lc_add').click(add_action);
    $('.remove-icon').click(remove_action);

    $('#lc_cat').change(change_categories);
    change_categories();
})