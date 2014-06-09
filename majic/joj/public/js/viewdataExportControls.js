/** 
 * Creates and manages the export controls.
 * @class
 *
 * @requires OpenLayers/Events.js
 * 
 * @author R. Wilkinson
 */

/**
 * Constructor to initialise export controls.
 * @constructor
 *
 * @param eventsManager - event manager
*/
function ViewdataExportControls(eventsManager, initialBounds, configOptions, formId, formats, defaultFormat) {
    this.eventsManager = eventsManager;
    this.currentSelection = initialBounds;
    this.configOptions = configOptions;
    this.formId = formId;
    this.formats = formats;
    this.defaultFormat = defaultFormat;
    this.selectedDimensionData = null;
    this.selectedLayerData = null;
    this.selectedFormat = this.defaultFormat;
    this.includeCaptionOptions = (configOptions.style == 'viewdata');
    this.oneLayerOnly = (configOptions.style == 'ipcc-ddc');
    this.defaultGrid = (configOptions.style == 'ipcc-ddc');

    this.formatDetails = {
        AVI_MJPEG: {description: 'AVI / MJPEG Video', isVideo: true, isAnimation: true, protocol: 'WMS', sequential: false},
        FLV: {description: 'Flash Video', isVideo: true, isAnimation: true, protocol: 'WMS', sequential: false},
        MOV: {description: 'Quicktime Video', isVideo: true, isAnimation: true, protocol: 'WMS', sequential: false},
        MPEG2: {description: 'MPEG-2 Video', isVideo: true, isAnimation: true, protocol: 'WMS', sequential: false},
        KML: {description: 'KML', isVideo: false, isAnimation: true, protocol: 'WMS', sequential: false},
        SVSX: {description: 'SVS Export', isVideo: true, isAnimation: true, protocol: 'WMS', sequential: false},
        WMS: {description: 'WMS Details', isVideo: false, isAnimation: false, protocol: 'WMS', sequential: false},
        WCS: {description: 'WCS Download', isVideo: false, isAnimation: true, protocol: 'WCS', sequential: true}
    };

    /**
     * Creates the export controls.
     */
    this.createControls = function() {

        this.exportForm = new Ext.FormPanel({
            title: this.configOptions.title,
            id: 'vd-export-' + this.formId,
            url: './make_export',
            border: true,
            frame: true,
            autoScroll: true,
            buttons: [{
                text: 'Make file',
                id: 'vd-export-' + this.formId + '-make',
                listeners: {
                    click: this.onMakeExport,
                    scope: this
                }
            }]
        });
        this.createForm();

        this.eventsManager.register('MAP_SELECTION_CHANGED', this, this.onChangeSelection);
        this.eventsManager.register('SELECTED_LAYER_CHANGED', this, this.onCurrentLayerChanged);
        this.eventsManager.register('LAYER_DIMENSION_CHANGED', this, this.onLayerDimensionChanged);
        this.eventsManager.register('LAYER_DISPLAY_CHANGED', this, this.onLayerParameterChanged);
        this.eventsManager.register('LAYER_LIST_REORDERED', this, this.onLayerParameterChanged);
    };

    /**
     * Handles a change of map selected region.
     * @param e - event data {selection}
     */
    this.onChangeSelection = function(e) {
        this.currentSelection = e.selection;
        this.clearDownloadArea();
    };

    /**
     * Handles a change of the selected layer.
     * @param e - event data {layerData, olLayer}
     */
    this.onCurrentLayerChanged = function(e) {
        this.selectedLayerData = e.layerData;
        this.selectedDimensionData = null;

        if (e.layerData !== null && e.olLayer !== null) {
            var dims = e.layerData.dimensions;

            // Select the first dimension by default.
            if (dims.length > 0) {
                this.selectedDimensionData = dims[0];
            }
        }

        this.configureDimensionSelector();
    };

    /**
     * Handles a change of dimension value for the current layer.
     * @param e - event data {param, value}
     */
    this.onLayerDimensionChanged = function(e) {
        // Save the value to use as default for animation start.
        this.setStartEndSelectorValues();
        this.onLayerParameterChanged();
    }

    /**
     * Handles a change of parameter value for the current layer.
     * Removes the link to the download file since it no longer corresponds to the current
     * parameters.
     * @param e - event data {param, value}
     */
    this.onLayerParameterChanged = function(e) {
        this.clearDownloadArea();
    }

    /**
     * Responds to a change of selected dimension.
     * @param combo - combo box on which the selection has been made
     * @param record - data record returned from the underlying store
     * @param index - index of the selected item in the dropdown list
     */
    this.onDimensionSelectionChanged = function(combo, record, index) {
        var selectedLayerDim = record.data.value;

        this.clearDownloadArea();

        this.selectedDimensionData = null;
        if (this.selectedLayerData !== null) {

            // Find the dimension data for the selected dimension.
            var dims = this.selectedLayerData.dimensions;
            if (dims && (dims.length > 0)) {
                this.selectedDimensionData = dims[0];
                for (var dimIdx = 0; dimIdx < dims.length; ++dimIdx) {
                    if (dims[dimIdx].name === selectedLayerDim) {
                        this.selectedDimensionData = dims[dimIdx];
                        break;
                    }
                }
            }
        }

        this.configureStartEndSelectors();
    };

    /**
     * Responds to a change of selected format.
     * @param combo - combo box on which the selection has been made
     * @param record - data record returned from the underlying store
     * @param index - index of the selected item in the dropdown list
     */
    this.onFormatSelectionChanged = function(combo, record, index) {
        this.selectedFormat = record.data.value;
        this.clearDownloadArea();
        this.configureForFormat();
    };

    /**
     * Configures the form with the fields appropriate for the selected format.
     */
    this.configureForFormat = function() {
        var isVideo = this.formatDetails[this.selectedFormat].isVideo;
        var cmp = Ext.getCmp('vd-' + formId + '-video-settings');
        if (cmp) {
            cmp.setVisible(isVideo);
            Ext.getCmp('vd-' + formId + '-height').setDisabled(!isVideo);
            Ext.getCmp('vd-' + formId + '-width').setDisabled(!isVideo);
            Ext.getCmp('vd-' + formId + '-framerate').setDisabled(!isVideo);
            Ext.getCmp('vd-' + formId + '-grid').setDisabled(!isVideo);
        }
        cmp = Ext.getCmp('vd-' + formId + '-caption-settings');
        if (cmp) {
            cmp.setVisible(isVideo);
            Ext.getCmp('vd-' + formId + '-legend-show-bounding-box').setDisabled(!isVideo);
            Ext.getCmp('vd-' + formId + '-legend-show-layer-names').setDisabled(!isVideo);
            Ext.getCmp('vd-' + formId + '-legend-show-style-names').setDisabled(!isVideo);
            Ext.getCmp('vd-' + formId + '-legend-show-dimensions').setDisabled(!isVideo);
        }
        this.enableDimensionSelectors();

        this.exportForm.doLayout(false, true);
    };

    /**
     * Enables or disables the dimension selectors depending on the selected format and whether the
     * selected layer has any dimensions.
     */
    this.enableDimensionSelectors = function() {
        var enable = this.dimensionsData && (this.dimensionsData.length > 0) && this.formatDetails[this.selectedFormat].isAnimation;
        this.animationFieldSet.setVisible(enable);
        this.dimensionSelector.setDisabled(!enable);
        this.startSelectorConfiguration.setDisabled(!enable);
        this.endSelectorConfiguration.setDisabled(!enable);
        this.numberStepsField.setDisabled(!enable);
        this.numberStepsField.setReadOnly(this.formatDetails[this.selectedFormat].sequential);
    };

    /**
     * Responds to a change of start or end value.
     */
    this.onLimitsChanged = function() {
        this.initialiseNumberOfSteps();
        this.onParameterChanged();
    }

    /**
     * Responds to a change of parameter value - clears the download text/link.
     */
    this.onParameterChanged = function() {
        this.clearDownloadArea();
    };

    /**
     * Creates the form contents.
     */
    this.createForm = function() {
        var formItems = [];

        // Add the format selector - include this even if no dimensions to allow single frame export.
        var formatData = [];
        for (var i = 0; i < this.formats.length; ++i) {
            formatData.push([this.formats[i], this.formatDetails[this.formats[i]].description]);
        }
        var formatStore = new Ext.data.ArrayStore({
            id: 'vd-' + formId + '-format_store',
            fields: ['value', 'display'],
            data: formatData
        });

        formItems.push([{
            xtype: 'fieldset',
            title: 'Output File',
            defaults: {bodyStyle: 'padding: 1px 0px'},
            items: [{
                layout: 'hbox',
                pack: 'start',
                hidden: (this.formats.length < 2),
                items: [{
                    xtype: 'label',
                    text: 'Format',
                    flex: 2,
                    margins: {top:3, right:0, bottom:0, left:0}
                },{
                    xtype: 'combo',
                    hiddenName: 'animation-format',
                    editable: false,
                    forceSelection: true,
                    triggerAction: 'all',
                    allowBlank: false,
                    lazyRender: false,
                    mode: 'local',
                    store: formatStore,
                    valueField: 'value',
                    displayField: 'display',
                    value: this.selectedFormat,
                    flex: 3,
                    listeners: {
                        select: this.onFormatSelectionChanged,
                        scope: this
                    }
                },{
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-format-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-format-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                id: 'vd-' + formId + '-prefix-box',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'File name prefix (optional)',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 2
                },{
                    xtype: 'textfield',
                    id: 'vd-' + formId + '-prefix',
                    name: 'animation-prefix',
                    maskRe: new RegExp('[a-zA-Z0-9_-]'),
                    maxLength: 20,
                    value: '',
                    flex: 3,
                    listeners: {
                        change: this.onParameterChanged,
                        scope: this
                    }
                },{
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-prefix-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-prefix-text',
                hidden: true,
                cls: 'vd-help-panel'
            }]
        }]);

        this.downloadUrl = new Ext.Panel({
            html: ''
        });

        this.downloadFieldSet = new Ext.form.FieldSet({
            title: 'Download',
            cls: 'vd-fieldset-with-help',
            hidden: true,
            items: [{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: '',
                    flex: 1
                },{
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-download-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-download-text',
                hidden: true,
                cls: 'vd-help-panel'
            },
                this.downloadUrl
            ]});
        formItems.push(this.downloadFieldSet);

        var dimensionsData = [];
        var dimName = '';
        dimensionsData.push([dimName, dimName]);

        var dimensionStore = new Ext.data.ArrayStore({
            id: 'vd-' + formId + '-dimension_store',
            fields: ['value', 'display'],
            data: dimensionsData
        });

        this.dimensionSelector = new Ext.form.ComboBox({
            hiddenName: 'animation-dimension',
            disabled: true,
            editable: false,
            forceSelection: true,
            triggerAction: 'all',
            allowBlank: false,
            lazyRender: false,
            mode: 'local',
            store: dimensionStore,
            valueField: 'value',
            displayField: 'display',
            value: dimName,
            flex: 1,
            listeners: {
                select: this.onDimensionSelectionChanged,
                scope: this
            }
        });

        this.startSelectorPanel = new Ext.Panel({
            layout: 'hbox',
            pack: 'start',
            flex: 4
        });
        this.endSelectorPanel = new Ext.Panel({
            layout: 'hbox',
            pack: 'start',
            flex: 4
        });
        this.startSelectorConfiguration = new ViewdataSelectorConfiguration(this.startSelectorPanel);
        this.endSelectorConfiguration = new ViewdataSelectorConfiguration(this.endSelectorPanel);

        this.numberStepsField = new Ext.form.NumberField({
            id: 'vd-' + formId + '-number-steps',
            name: 'animation-number-steps',
            value: this.configOptions.defaultnumbersteps,
            allowBlank: false,
            allowDecimals: false,
            allowNegative: false,
            minValue: 1,
            maxValue: this.configOptions.maxnumbersteps,
            flex: 1,
            listeners: {
                change: this.onParameterChanged,
                scope: this
            }
        });

        this.animationFieldSet = new Ext.form.FieldSet({
            id: 'vd-' + formId + '-animation-settings',
//            title: 'Animation',
            title: this.configOptions.headingAnimation,
            defaults: {bodyStyle: 'padding: 1px 0px'},
            hidden: true,
            items: [{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Dimension',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 1
                },
                    this.dimensionSelector,
                {
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-dimension-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-dimension-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Start',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 1
                },
                    this.startSelectorPanel,
                {
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-start-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-start-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'End',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 1
                },
                    this.endSelectorPanel,
                {
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-end-btn',
                    enableToggle: true,
                    margins: {top:0, right:0, bottom:0, left:3},
                    iconCls: 'vd-help-icon',
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-end-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Number of steps',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 1
                },
                this.numberStepsField,
                {
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-number-steps-btn',
                    enableToggle: true,
                    margins: {top:0, right:0, bottom:0, left:3},
                    iconCls: 'vd-help-icon',
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-number-steps-text',
                hidden: true,
                cls: 'vd-help-panel'
            }]
        });
        formItems.push(this.animationFieldSet);

        formItems.push([{
            xtype: 'fieldset',
            id: 'vd-' + formId + '-video-settings',
            title: 'Video Settings',
            defaults: {bodyStyle: 'padding: 1px 0px'},
            items: [{
                layout: 'hbox',
                id: 'vd-' + formId + '-height-box',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Height',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 2
                },{
                    xtype: 'numberfield',
                    id: 'vd-' + formId + '-height',
                    name: 'HEIGHT',
                    value: this.configOptions.defaultheight,
                    allowBlank: false,
                    allowDecimals: false,
                    allowNegative: false,
                    minValue: this.configOptions.minheight,
                    maxValue: this.configOptions.maxheight,
                    flex: 3,
                    listeners: {
                        change: this.onParameterChanged,
                        scope: this
                    }
                },{
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-height-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-height-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                id: 'vd-' + formId + '-width-box',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Width',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 2
                },{
                    xtype: 'numberfield',
                    id: 'vd-' + formId + '-width',
                    name: 'WIDTH',
                    value: this.configOptions.defaultwidth,
                    allowBlank: false,
                    allowDecimals: false,
                    allowNegative: false,
                    minValue: this.configOptions.minwidth,
                    maxValue: this.configOptions.maxwidth,
                    flex: 3,
                    listeners: {
                        change: this.onParameterChanged,
                        scope: this
                    }
                },{
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-width-btn',
                    enableToggle: true,
                    margins: {top:0, right:0, bottom:0, left:3},
                    iconCls: 'vd-help-icon',
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-width-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                id: 'vd-' + formId + '-framerate-box',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Frames/sec',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 2
                },{
                    xtype: 'numberfield',
                    id: 'vd-' + formId + '-framerate',
                    name: 'animation-framerate',
                    value: 2,
                    allowBlank: false,
                    allowDecimals: true,
                    allowNegative: false,
                    flex: 3,
                    listeners: {
                        change: this.onParameterChanged,
                        scope: this
                    }
                },{
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-framerate-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-framerate-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'checkbox',
                    id: 'vd-' + formId + '-grid',
                    name: 'figure-grid',
                    boxLabel: 'Draw grid',
                    checked: this.defaultGrid,
                    margins: {top:0, right:0, bottom:0, left:0}
                },{
                    flex: 1
                },{
                    xtype: 'button',
                    id : 'vd-help-' + formId + '-grid-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-' + formId + '-grid-text',
                hidden: true,
                cls: 'vd-help-panel'
            }]
        }]);

        if (this.includeCaptionOptions) {
            formItems.push([{
                xtype: 'fieldset',
                id: 'vd-' + formId + '-caption-settings',
                title: 'Caption',
                defaults: {bodyStyle: 'padding: 1px 0px'},
                items: [{
                    layout: 'hbox',
                    pack: 'start',
                    items: [{
                        xtype: 'label',
                        text: 'Include:',
                        flex: 1,
                        margins: {top:0, right:0, bottom:0, left:2}
                    },{
                        xtype: 'button',
                        id : 'vd-help-' + formId + '-caption-include-btn',
                        enableToggle: true,
                        iconCls: 'vd-help-icon',
                        toggleHandler: ViewdataHelp.toggleHelp
                    }]
                },{
                    id: 'vd-help-' + formId + '-caption-include-text',
                    hidden: true,
                    cls: 'vd-help-panel'
                },{
                    layout: 'hbox',
                    pack: 'start',
                    items: [{
                        xtype: 'checkbox',
                        id: 'vd-' + formId + '-legend-show-bounding-box',
                        name: 'figure-legend-show-bounding-box',
                        boxLabel: 'Bounding box',
                        checked: true,
                        margins: {top:0, right:0, bottom:0, left:20}
                    }]
                },{
                    layout: 'hbox',
                    pack: 'start',
                    items: [{
                        xtype: 'checkbox',
                        id: 'vd-' + formId + '-legend-show-layer-names',
                        name: 'figure-legend-show-layer-names',
                        boxLabel: 'Layer names',
                        checked: true,
                        margins: {top:0, right:0, bottom:0, left:20}
                    }]
                },{
                    layout: 'hbox',
                    pack: 'start',
                    items: [{
                        xtype: 'checkbox',
                        id: 'vd-' + formId + '-legend-show-style-names',
                        name: 'figure-legend-show-style-names',
                        boxLabel: 'Layer style names',
                        checked: true,
                        margins: {top:0, right:0, bottom:0, left:20}
                    }]
                },{
                    layout: 'hbox',
                    pack: 'start',
                    items: [{
                        xtype: 'checkbox',
                        id: 'vd-' + formId + '-legend-show-dimensions',
                        name: 'figure-legend-show-dimensions',
                        boxLabel: 'Layer dimension names and values',
                        checked: true,
                        margins: {top:0, right:0, bottom:0, left:20}
                    }]
                }]
            }]);
        }

        this.exportForm.add(formItems);
        this.configureForFormat();
        this.exportForm.doLayout(false, true);
    };

    /**
     * Reconfigures the dimensions selector for the currently selected layer.
     */
    this.configureDimensionSelector = function() {

        var disable = true;
        if (this.selectedLayerData !== null) {

            // Find the dimensions for the current layer and set on the selector.
            var dims = this.selectedLayerData.dimensions;

            this.dimensionsData = [];
            for (var dimIdx = 0; dimIdx < dims.length; ++dimIdx) {
                var dimName = dims[dimIdx].name;
                this.dimensionsData.push([dimName, dimName]);
            }
            var dimensionStore = this.dimensionSelector.getStore();
            dimensionStore.removeAll(true);

            if (this.dimensionsData.length > 0) {
                dimensionStore.loadData(this.dimensionsData);
                this.dimensionSelector.setValue(this.dimensionsData[0][0]);
                disable = false;
            }
        }

        // Enable the selectors if the layer has any dimensions (otherwise disable).
        if (disable) {
            this.dimensionSelector.setValue('');
        }
        this.enableDimensionSelectors();

        // Update the start and end selectors for the selected dimension.
        this.configureStartEndSelectors();

        this.animationFieldSet.setVisible(!disable);
    };

    /**
     * Reconfigures the animation start and end selectors for the currently selected layer and dimension.
     */
    this.configureStartEndSelectors = function() {
        if (this.selectedDimensionData !== null) {
            var dimensionData = this.selectedDimensionData;
        } else {
            // Create a dummy selector to help with layout.
            var dimensionData = {dimensionValues: [1]};
        }
        this.startSelectorConfiguration.configureSelectors(dimensionData,
                                                           'vd-export-' + this.formId + '-start',
                                                           this.onLimitsChanged, this);
        this.endSelectorConfiguration.configureSelectors(dimensionData,
                                                         'vd-export-' + this.formId + '-end',
                                                         this.onLimitsChanged, this);
        this.setStartEndSelectorValues();
        this.exportForm.doLayout(false, true);
    };

    /**
     * Sets the animation start and end selectors values.
     */
    this.setStartEndSelectorValues = function() {
        if ((this.selectedDimensionData !== null) && (this.selectedLayerData !== null)) {

            // Set the dimension values as data for the start and end selectors.
            var extent = this.selectedDimensionData.dimensionValues;

            // Make the start value the current value on the map.
            var firstIndex = 0;
            var startValue = viewdataLayerData.getDimension(this.selectedLayerData.id, this.selectedDimensionData.name);

            if (startValue) {
                for (var i = 0; i < extent.length; ++i) {
                    if (startValue  == extent[i]) {
                        firstIndex = i;
                        break;
                    }
                }
            }

            var valueData = [];
            // Initialise to the next (defaultnumbersteps) values.
            var firstValue = extent[firstIndex];
            var lastValue = extent[Math.min(firstIndex + (+this.configOptions.defaultnumbersteps), extent.length) - 1];

            this.startSelectorConfiguration.setValue(firstValue);
            this.endSelectorConfiguration.setValue(lastValue);
        }

        this.initialiseNumberOfSteps();
    };

    /**
     * Initialises the number of steps such that all dimension values between the start and end
     * value (inclusive) would be included in the animation (unless it exceeds the configured
     * maximum nuber of steps).
     */
    this.initialiseNumberOfSteps = function() {
        if (this.selectedDimensionData !== null) {
            var startVal = this.startSelectorConfiguration.getValue();
            var endVal = this.endSelectorConfiguration.getValue();

            var extent = this.selectedDimensionData.dimensionValues;
            var startIdx = 0;
            var endIdx = extent.length - 1;
            for (var i = 0; i < extent.length; ++i) {
                if (extent[i] == startVal) {
                    startIdx = i;
                }
                if (extent[i] == endVal) {
                    endIdx = i;
                }
            }

            var numberSteps = Math.max(startIdx, endIdx) - Math.min(startIdx, endIdx) + 1;
            if (this.formatDetails[this.selectedFormat].sequential) {
                // Number of steps cannot be reduced so as not to exceed the limit.
                this.numberStepsField.setMaxValue(+this.configOptions.maxnumbersteps);
                this.numberStepsField.maxText = 'Change the start or end value so that the number of steps does not exceed {0}';
            } else {
                // Only allow the number of steps to be reduced.
                numberSteps = Math.min(numberSteps, (+this.configOptions.maxnumbersteps));
                this.numberStepsField.setMaxValue(numberSteps);
                this.numberStepsField.maxText = 'The number of steps cannot exceed {0}, the number of steps in the range from the start value to the end value';
            }
            this.numberStepsField.setValue(numberSteps);
        } else {
            this.numberStepsField.setValue(1);
            this.numberStepsField.setMaxValue(1);
        }
    };

    /**
     * Responds to the make export button.
     * @param btn - the pressed button
     * @param e - button click event
     */
    this.onMakeExport = function(btn, e) {
        var tempParams = {};
        var layerParams = viewdataMapManager.makeLayerParameters(this.oneLayerOnly);
        for (var i = 0; i < layerParams.length; ++i) {
            tempParams[layerParams[i].name] = layerParams[i].value;
        }

        // Overwrite endpoint for WCS protocol.
        if (this.formatDetails[this.selectedFormat].protocol == 'WCS') {
            for (var i = 1; ; ++i) {
                if (!tempParams['' + i + '_LAYER_ID']) {
                    break;
                }
                layerData = viewdataLayerData.layerData[tempParams['' + i + '_LAYER_ID']]
                if (layerData.layerData.getCoverageUrl) {
                    tempParams['' + i + '_ENDPOINT'] = layerData.layerData.getCoverageUrl;
                }
            }
        }

        if (this.selectedLayerData) {
            var animationLayer = viewdataMapManager.getLayerNumberById(this.selectedLayerData.id);
            tempParams['animation-layer-number'] = animationLayer;
        }

        if (!this.startSelectorConfiguration.disabled) {
            var animationStart = this.startSelectorConfiguration.getValue();
            if (animationStart) {
                tempParams['animation-start'] = animationStart;
            }
        }
        if (!this.endSelectorConfiguration.disabled) {
            var animationEnd = this.endSelectorConfiguration.getValue();
            if (animationEnd) {
                tempParams['animation-end'] = animationEnd;
            }
        }

        var bboxString = this.currentSelection.left + "," + this.currentSelection.bottom + ","
            + this.currentSelection.right + "," + this.currentSelection.top;
        if ((this.currentSelection.left >= this.currentSelection.right)
            || (this.currentSelection.bottom >= this.currentSelection.top)) {
                Ext.MessageBox.show({msg: "The selection bounding box " + bboxString + " is invalid: ",
                                     buttons: Ext.MessageBox.OK,
                                     midWidth: 250});
                return;
        }
        tempParams['BBOX'] = bboxString;
        tempParams['figure-style'] = this.configOptions.style;

        this.downloadUrl.update("<div><img src='../layout/images/loading7.gif' style='width:24; height:24; margin-right:32'>Creating file...</div>");
        this.downloadFieldSet.setVisible(true);
        this.exportForm.doLayout(false, true);
        this.scrollToDownload.defer(250, this);

        var form = this.exportForm.getForm();
        form.submit({
            params: tempParams,
            scope: this,
            timeout: this.configOptions.browsertimeout,
            success: function(form, action) {
                this.downloadUrl.update("<div><p>Open or download from this link:</p><p><a href='" + action.result.url
                                        + "' target='_blank'>" + action.result.url + "</a></p></div>");
                this.downloadFieldSet.setVisible(true);
                this.exportForm.doLayout(false, true);
                this.scrollToDownload();
            },
            failure: function(form, action) {
                this.clearDownloadArea();
                if (action.failureType === Ext.form.Action.CONNECT_FAILURE){
                    Ext.Msg.alert('Failure', 'Server reported:' + action.response.status + ' ' + action.response.statusText);
                }
                if (action.failureType === Ext.form.Action.SERVER_INVALID){
                    Ext.Msg.alert('Warning', action.result.errorMessage);
                }
                if (action.failureType === Ext.form.Action.CLIENT_INVALID){
                    Ext.Msg.alert('Failure', 'Please correct invalid selections and try again.');
                }
                if (action.failureType === Ext.form.Action.LOAD_FAILURE){
                    Ext.Msg.alert('Failure', 'Error loading data from server');
                }
            }
        });
    };

    /**
     * Scrolls the download fieldset into view.
     */
    this.scrollToDownload = function() {
        var downloadFieldSetEl = this.downloadFieldSet.getEl();
        var exportFormEl = this.exportForm.getForm().getEl();
        downloadFieldSetEl.scrollIntoView(exportFormEl);
    };

    /**
     * Clears the download URL and hides the download fieldset.
     */
    this.clearDownloadArea = function() {
        this.downloadUrl.update("");
        this.downloadFieldSet.setVisible(false);
        this.exportForm.doLayout(false, true);
    };
}
