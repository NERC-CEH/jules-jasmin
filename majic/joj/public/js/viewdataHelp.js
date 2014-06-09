/** 
 * Help display functions.
 *
 * @author R. Wilkinson
 */

ViewdataHelp = {};

/**
 * Toggles visibility of help text.
 * It is assumed that the button id is of the form <name>-btn and the corresponding help text component has id <name>-text.
 */
ViewdataHelp.toggleHelp = function(button, state) {
    var sectionId = button.id.replace(/-btn$/, '');
    ViewdataHelp.toggleHelpById(sectionId);
};

/**
 * Toggles visibility of help text.
 * It is assumed that the help text component has id <name>-text.
 * 
 */
ViewdataHelp.toggleHelpById = function(sectionId, layoutId) {
    var component = Ext.getCmp(sectionId + "-text");

    // Hide the text if toggling off.
    if (component.isVisible()) {
        component.setVisible(false);
        ViewdataHelp.updateLayout(component, layoutId);
        return;
    }

    // Find out whether the help text has already been loaded.
    var divs = component.el.dom.getElementsByTagName('div');
    var loaded = false;
    var textDivId = sectionId + "-text-div";
    for (var i = 0; i < divs.length; ++i) {
        if (divs[i].id == textDivId) {
            loaded = true;
            break;
        }
    }
    if (loaded) {
        component.setVisible(true);
        ViewdataHelp.updateLayout(component, layoutId);
    } else {
        Ext.Ajax.request({
            url: './get_help',
            success: ViewdataHelp.getHelpSuccess,
            failure: ViewdataHelp.getHelpFailure,
            params: {help: sectionId},
            scope: {component: component, textDivId: textDivId}
        });
    }
};

ViewdataHelp.updateLayout = function(component, layoutId) {
    var form = component.findParentByType('form');
    if (form) {
        form.doLayout();
    }
    if (layoutId) {
        var cmp = component.findParentBy(function(cnt, startCmp) {return cnt.el.id == layoutId});
        if (cmp) {
            cmp.doLayout();
        }
    }
};

ViewdataHelp.getHelpSuccess = function(response, opts) {
    var obj = Ext.decode(response.responseText);
    this.component.update('<div id="' + this.textDivId + '" class="vd-help-panel-body">' + obj.help + '</div>')
    this.component.setVisible(true);
    var form = this.component.findParentByType('form');
    if (form) {
        form.doLayout();
    }
    var cmp = this.component.findParentBy(function(cnt, startCmp) {return cnt.el.id == 'vd-layers-region'});
    if (cmp) {
        cmp.doLayout();
    }
};

ViewdataHelp.getHelpFailure = function(response, opts) {
    var obj = Ext.decode(response.responseText);
    this.component.update('<div id="' + this.textDivId + '" class="vd-help-panel-body">Help text unavailable.</div>')
    this.component.setVisible(true);
    var form = this.component.findParentByType('form');
    if (form) {
        form.doLayout();
    }
};
