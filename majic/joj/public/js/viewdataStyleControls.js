/** 
 * Creates and manages the style controls.
 * @class
 *
 * @requires OpenLayers/Events.js
 * 
 * @author R. Wilkinson
 */

/**
 * Constructor to initialise style controls.
 * @constructor
 *
 * @param eventsManager - event manager
 * @param initialStatus - configuration values passed when starting application
*/
function ViewdataStyleControls(eventsManager, initialStatus) {
    this.eventsManager = eventsManager;
    this.selectedLayerId = null;
    this.defaultOptionsList = initialStatus.DefaultLayerParms;

    /**
     * Creates the style controls.
     */
    this.createControls = function() {

        this.styleForm = new Ext.FormPanel({
            title: 'Style',
            id: 'vd-style-form',
            border: true,
            frame: true,
            autoScroll: true
        });

        this.addHelp();
        this.setNoLayer();

        this.eventsManager.register('LAYER_STYLES_SET', this, this.onLayerStylesSet);
    };

    /**
     * Adds a help button and text holder.
     */
    this.addHelp = function() {
        this.styleForm.add(new Ext.Panel({
            layout: 'hbox',
            pack: 'start',
            items: [{
                xtype: 'label',
                text: ' ',
                flex: 1
            },{
                xtype: 'button',
                id : 'vd-help-style-btn',
                enableToggle: true,
                iconCls: 'vd-help-icon',
                toggleHandler: ViewdataHelp.toggleHelp
            }]
        }));
        this.styleForm.add(new Ext.Panel({
            items: [{
                id: 'vd-help-style-text',
                hidden: true,
                cls: 'vd-help-panel'
            }]
        }));
    };

    /**
     * Displays no layer selected text.
     */
    this.setNoLayer = function() {
        this.styleForm.add(new Ext.Panel({
            layout: 'fit',
            html: 'No layer is selected.',
            style: 'text-align: center'
        }));
    };

    /**
     * Displays layer has no styles text.
     */
    this.setNoStyles = function() {
        this.styleForm.add(new Ext.Panel({
            layout: 'fit',
            html: 'The selected layer has no styles.',
            style: 'text-align: center'
        }));
    };

    /**
     * Handles a change of the selected layer.
     * Creates selectors for each style defined in the WMC.
     * @param e - event data {id, layerData}
     */
    this.onLayerStylesSet = function(e) {
        // Clear form.
        this.styleForm.removeAll(true);
        this.displayOptions = {};
        this.styleOptions = [];

        this.addHelp();

        this.selectedLayerId = e.id;

        // Find the default style if there is one.
        this.defaultSetter = new LayerDefaultSetter({}, this.defaultOptionsList);
        this.defaultParams = this.defaultSetter.getDefaults(e.layerData.getMapUrl, e.layerData.name);
        var initialStyle = this.defaultParams.styles;

        if (e.layerData !== null) {
            var layerData = e.layerData;
            var styles = layerData.styles;

            if (styles.length > 0) {
                var data = [];
                for (var i = 0; i < styles.length; ++i) {
                    data.push([styles[i].name, styles[i].title]);
                }

                // Get the previously selected style, if set, or the default, if configured.
                var style = viewdataLayerData.getProperty(this.selectedLayerId, 'styles');
                if (style == null) {
                    if (initialStyle) {
                        style = initialStyle;
                    } else {
                        style = styles[0].name;
                    }
                }
                this.setStyleValue(style);

                var styleFieldSet = new Ext.form.FieldSet({
                    defaults: {bodyStyle: 'padding: 1px 0px'}
                });
                this.createSelector('styles', 'Style', data, style, this.onStyleSelectionChanged, this, styleFieldSet, []);
                this.styleForm.add(new Ext.Panel({
                    items: [{xtype: 'label', html: '&nbsp;', style: 'font-size:5px'},
                           styleFieldSet]
                }));

                this.fieldSet = new Ext.form.FieldSet({
                    title: 'Display Options',
                    defaults: {bodyStyle: 'padding: 1px 0px'},
                    cls: 'vd-fieldset-with-help',
                    items: [{
                        layout: 'hbox',
                        pack: 'start',
                        items: [{
                            xtype: 'label',
                            text: '',
                            flex: 1
                        },{
                            xtype: 'button',
                            id : 'vd-help-style-display-options-btn',
                            enableToggle: true,
                            iconCls: 'vd-help-icon',
                            toggleHandler: ViewdataHelp.toggleHelp
                        }]
                    },{
                        id: 'vd-help-style-display-options-text',
                        hidden: true,
                        cls: 'vd-help-panel'
                    }]
                });

                if (layerData.displayOptions) {
                    this.displayOptions = layerData.displayOptions;
                    this.createDisplayOptions(style);
                }

                this.fieldSet.setVisible(this.styleOptions.length > 0);

                this.styleForm.add(this.fieldSet);
            } else {
                this.setNoStyles();
            }
        } else {
            this.setNoLayer();
        }
        this.styleForm.doLayout(false, true);
    };

    /**
     * Creates the controls for display options
     * @param style - current style for which options are to be displayed
     */
    this.createDisplayOptions = function(style) {
        var styleOptions = [];
        if (this.displayOptions['common']) {
            styleOptions = styleOptions.concat(this.displayOptions['common']);
        }
        if (this.displayOptions[style]) {
            styleOptions = styleOptions.concat(this.displayOptions[style]);
        }

        for (var optIdx = 0; optIdx < styleOptions.length; ++optIdx) {
            var opt = styleOptions[optIdx];
            // Initialise to the current value if one has been set, or the default.
            var currentValue = viewdataLayerData.getProperty(this.selectedLayerId, opt.name);
            if (!currentValue) {
                if (this.defaultParams[opt.name]) {
                    currentValue = this.defaultParams[opt.name];
                } else {
                    currentValue = opt.defaultVal
                }
            }

            if (opt.type == 'select') {
                var data = [];
                for (var i = 0; i < opt.options.length; ++i) {
                    data.push([opt.options[i], opt.options[i]]);
                }
                this.createSelector(opt.name, opt.title, data, currentValue, this.onOptionSelectionChanged,
                                    this, this.fieldSet, this.styleOptions);
            } else if (opt.type == 'bool') {
                this.createCheckBox(opt.name, opt.title, currentValue, this.onOptionCheckBoxChanged,
                                    this, this.fieldSet, this.styleOptions);
            } else if (opt.type == 'value') {
                this.createField(opt.name, opt.title, currentValue, this.onOptionFieldChanged,
                                 this, this.fieldSet, this.styleOptions);
            }
        }
    };

    /**
     * Responds to a change of style selection.
     * @param combo - combo box on which the selection has been made
     * @param record - data record returned from the underlying store
     * @param index - index of the selected item in the dropdown list
     */
    this.onStyleSelectionChanged = function(combo, record, index) {
        this.setStyleValue(record.data.value);
        for (var i = 0; i < this.styleOptions.length; ++i) {
            this.fieldSet.remove(this.styleOptions[i]);
        }
        this.createDisplayOptions(record.data.value);
        this.styleForm.doLayout(false, true);
    };

    /**
     * Saves a style value for the layer and raises an event conveying the new value.
     * @param value - value to which to set style
     */
    this.setStyleValue = function(value) {
        if (viewdataLayerData.getProperty(this.selectedLayerId, 'styles') != value) {
            viewdataLayerData.setProperty(this.selectedLayerId, 'styles', value);

            this.eventsManager.triggerEvent("LAYER_DISPLAY_CHANGED", {param: 'styles', value: value});
        }
    }

    /**
     * Creates a selector ComboBox
     * @param id - id used to identify the option
     * @param label - label to display
     * @param data - array of arrays each containing a value and display value
     * @param initialValue - initial value to select
     * @param onSelectionChanged - select event handler
     * @param scope - scope for onSelectionChanged call
     * @param parent - parent component to which to add the selector
     * @param idList - array to which to append an ID of a component to be removed when the style options change
     */
    this.createSelector = function(id, label, data, initialValue, onSelectionChanged, scope, parent, idList) {
        var store = new Ext.data.ArrayStore({
            id: 'vd-style-store_' + id,
            fields: ['value', 'display'],
            data: data
        });

        var selector = new Ext.form.ComboBox({
            id: 'vd-style-select_' + id,
            flex: 1,
            editable: false,
            forceSelection: true,
            triggerAction: 'all',
            allowBlank: false,
            lazyRender: false,
            mode: 'local',
            store: store,
            valueField: 'value',
            displayField: 'display',
            listeners: {
                select: onSelectionChanged,
                scope: scope
            },
            hideLabel: true
        });
        selector.setValue(initialValue);

        parent.add({
            id: 'vd-style-option_' + id,
            layout: 'hbox',
            pack: 'start',
            items: [
                {xtype: 'label',
                 text: label,
                 margins: {top:3, right:0, bottom:0, left:0},
                 flex: 1
                },
                selector
            ]
        });

        idList.push('vd-style-option_' + id);
    };

    /**
     * Responds to a change of option selection.
     * @param combo - combo box on which the selection has been made
     * @param record - data record returned from the underlying store
     * @param index - index of the selected item in the dropdown list
     */
    this.onOptionSelectionChanged = function(combo, record, index) {
        var optionName = combo.id.substring(16);
        var value = record.data.value;
        if (viewdataLayerData.getProperty(this.selectedLayerId, optionName) != value) {
            viewdataLayerData.setProperty(this.selectedLayerId, optionName, value);

            this.eventsManager.triggerEvent("LAYER_DISPLAY_CHANGED", {param: optionName, value: value});
        }
    };

    /**
     * Creates a checkbox
     * @param id - id used to identify the option
     * @param label - label to display
     * @param initialValue - initial value to select
     * @param onValueChanged - value changed event handler
     * @param scope - scope for onValueChanged call
     * @param parent - parent component to which to add the selector
     * @param idList - array to which to append an ID of a component to be removed when the style options change
     */
    this.createCheckBox = function(id, label, initialValue, onValueChanged, scope, parent, idList) {
        parent.add({
            id: 'vd-style-option_' + id,
            layout: 'hbox',
            pack: 'start',
            items: [{
                xtype: 'checkbox',
                id: 'vd-style-checkbox_' + id,
                name: id,
                boxLabel: label,
                checked: initialValue,
                margins: {top:0, right:0, bottom:0, left:0},
                listeners: {
                    check: onValueChanged,
                    scope: scope
                }
            }]
        });

        idList.push('vd-style-option_' + id);
    };

    /**
     * Responds to a change of option checkbox value.
     * @param field - checkbox on which the value has changed
     * @param value - checkbox value
     */
    this.onOptionCheckBoxChanged = function(field, value) {
        var optionName = field.id.substring(18);
        if (viewdataLayerData.getProperty(this.selectedLayerId, optionName) != value) {
            viewdataLayerData.setProperty(this.selectedLayerId, optionName, value);

            this.eventsManager.triggerEvent("LAYER_DISPLAY_CHANGED", {param: optionName, value: value});
        }
    };

    /**
     * Creates a text field
     * @param id - id used to identify the option
     * @param label - label to display
     * @param initialValue - initial value to select
     * @param onValueChanged - value changed event handler
     * @param scope - scope for onValueChanged call
     * @param parent - parent component to which to add the selector
     * @param idList - array to which to append an ID of a component to be removed when the style options change
     */
    this.createField = function(id, label, initialValue, onValueChanged, scope, parent, idList) {
        parent.add({
            id: 'vd-style-option_' + id,
            layout: 'hbox',
            pack: 'start',
            items: [{
                xtype: 'label',
                text: label,
                margins: {top:3, right:0, bottom:0, left:0},
                flex: 1
            },{
                xtype: 'field',
                id: 'vd-style-field_' + id,
                name: id,
                value: initialValue,
                allowBlank: true,
                flex: 1,
                listeners: {
                    change: onValueChanged,
                    specialkey: this.onFieldKey.bind({scope: scope, onValueChanged: onValueChanged}),
                    scope: scope
                }
            }]
        });

        idList.push('vd-style-option_' + id);
    };

    /**
     * Responds to a change of option field value.
     * @param field - field on which the value has changed
     * @param value - field value
     * @param oldValue - previous field value (not used)
     */
    this.onOptionFieldChanged = function(field, value, oldValue) {
        var optionName = field.id.substring(15);
        if (viewdataLayerData.getProperty(this.selectedLayerId, optionName) != value) {
            viewdataLayerData.setProperty(this.selectedLayerId, optionName, value);

            this.eventsManager.triggerEvent("LAYER_DISPLAY_CHANGED", {param: optionName, value: value});
        }
    };

    /**
     * Responds to an enter key press in an option field.
     * @param field - field on which the value has changed
     * @param e - event
     */
    this.onFieldKey = function(field, e) {
        if (e.getKey() == e.ENTER) {
            var value = field.getValue();
            this.onValueChanged.call(this.scope, field, value, value);
        }
    };
}
