/** 
 * Creates and manages the dimension controls.
 * @class
 *
 * @requires OpenLayers/Events.js
 * 
 * @author R. Wilkinson
 */

/**
 * Constructor to initialise dimension controls.
 * @constructor
 *
 * @param eventsManager - event manager
*/
function ViewdataDimensionControls(eventsManager) {
    this.eventsManager = eventsManager;
    this.selectedLayerId = null;

    /**
     * Creates the dimension controls.
     */
    this.createControls = function() {

        this.dimensionsForm = new Ext.FormPanel({
            title: 'Dimensions',
            id: 'vd-dimensions',
            border: true,
            frame: true,
            autoScroll: true
        });

        this.addHelp();
        this.setNoLayer();

        this.eventsManager.register('SELECTED_LAYER_CHANGED', this, this.onCurrentLayerChanged);
    };

    /**
     * Adds a help button and text holder.
     */
    this.addHelp = function() {
        this.dimensionsForm.add(new Ext.Panel({
            layout: 'hbox',
            pack: 'start',
            items: [{
                xtype: 'label',
                text: ' ',
                flex: 1
            },{
                xtype: 'button',
                id : 'vd-help-dimensions-btn',
                enableToggle: true,
                iconCls: 'vd-help-icon',
                toggleHandler: ViewdataHelp.toggleHelp
            }]
        }));
        this.dimensionsForm.add(new Ext.Panel({
            items: [{
                id: 'vd-help-dimensions-text',
                hidden: true,
                cls: 'vd-help-panel'
            }]
        }));
    };

    /**
     * Displays no layer selected text.
     */
    this.setNoLayer = function() {
        this.dimensionsForm.add(new Ext.Panel({
            layout: 'fit',
            html: 'No layer is selected.',
            style: 'text-align: center'
        }));
    };

    /**
     * Displays layer has no dimensions text.
     */
    this.setNoDimensions = function() {
        this.dimensionsForm.add(new Ext.Panel({
            layout: 'fit',
            html: 'The selected layer has no dimensions.',
            style: 'text-align: center'
        }));
    };

    /**
     * Handles a change of the selected layer.
     * Creates selectors for each dimension defined in the WMC.
     * Note: This is based on code in LayerDimensions._onCurrentLayerChanged, but does not process axis configuration
     * so always creates a single selector per dimension.
     * @param e - event data {layerData, olLayer}
     */
    this.onCurrentLayerChanged = function(e) {
        // Clear form.
        this.dimensionsForm.removeAll(true);

        this.addHelp();

        this.selectedLayerId = e.id;
        this.selectorsForDimension = {}

        if (e.layerData !== null && e.olLayer !== null) {
            var layerData = e.layerData;
            var olLayer = e.olLayer;

            var dims = layerData.dimensions;
            if (dims.length == 0) {
                this.setNoDimensions();
            }
            for (var dimIdx = 0; dimIdx < dims.length; ++dimIdx) {
                var dimData = dims[dimIdx];
                var dimName = dimData.name;
                var dimLabel = dimData.label;
                var unitString = dimData.units;
                if (dimData.unitSymbol && (dimData.unitSymbol != dimData.units)) {
                    unitString += ' ' + dimData.unitSymbol;
                }
                if (dimLabel) {
                    var title = dimLabel;
                } else {
                    var title = dimName + ' (' + unitString + ')';
                }

                // Add field display labels to title if present.
                if (dimData.displayLabels) {
                    var labels = [];
                    for (var i = 0; i < dimData.displayLabels.length; ++i) {
                        if (dimData.displayLabels[i] && dimData.displayLabels[i].length > 0) {
                            labels.push(dimData.displayLabels[i]);
                        }
                    }
                    
                    if (labels.length > 0) {
                        title = title + ' (' + dimData.displayLabels.join(', ') + ')'
                    }
                }

                var selectorPanel = new Ext.Panel({
                    layout: 'hbox',
                    pack: 'start'
                });

                // Create ComboBox(es) for selecting dimension value.
                var selectorConfiguration = new ViewdataSelectorConfiguration(selectorPanel);
                selectorConfiguration.configureSelectors(dimData, 'vd-dimension', this.onDimensionSelectionChanged, this);
                this.selectorsForDimension[dimName] = selectorConfiguration;


                var items = [selectorPanel];
                if (selectorConfiguration.isMultiValued()) {
                    var progressPanel = new Ext.Panel({
                        layout: 'hbox',
                        pack: 'start',
                        items: [
                            {xtype: 'progress',
                             id: 'vd-dimension-progress_' + dimName,
                             flex: 1,
                             listeners: {
                                 render: function(p) {
                                     p.getEl().addListener('click', this.onProgressBarClick, {vddc: this, progress: p});
                                 },
                                 scope: this
                             }
                            }
                        ]
                    });
                    var controlButtonPanel = new Ext.Panel({
                        layout: 'hbox',
                        pack: 'start',
                        items: [
                            {xtype: 'label', html: '&nbsp;', flex: 10},
                            {xtype: 'button',
                             iconCls: 'vd-start-icon',
                             id: 'vd-dimension-gotostart_' + dimName,
                             listeners: {
                                 click: this.onGoToStart,
                                 scope: this
                             }
                            },
                            {xtype: 'label', html: '&nbsp;', flex: 1},
                            {xtype: 'button',
                             iconCls: 'vd-step-backwards-icon',
                             id: 'vd-dimension-stepbackwards_' + dimName,
                             listeners: {
                                 click: this.onStepBackwards,
                                 scope: this
                             }
                            },
                            {xtype: 'label', html: '&nbsp;', flex: 1},
                            {xtype: 'button',
                             iconCls: 'vd-step-forwards-icon',
                             id: 'vd-dimension-stepforwards_' + dimName,
                             listeners: {
                                 click: this.onStepForward,
                                 scope: this
                             }
                            },
                            {xtype: 'label', html: '&nbsp;', flex: 1},
                            {xtype: 'button',
                             iconCls: 'vd-end-icon',
                             id: 'vd-dimension-gotoend_' + dimName,
                             listeners: {
                                 click: this.onGoToEnd,
                                 scope: this
                             }
                            },
                            {xtype: 'label', html: '&nbsp;', flex: 10}
                        ]
                    });
                    items.push(progressPanel);
                    items.push(controlButtonPanel);
                }

                // Add ComboBox, progress bar and step controls to a field set.
                this.dimensionsForm.add(new Ext.form.FieldSet({
                    title: title,
                    hideLabel: true,
                    defaults: {bodyStyle: 'padding: 3px 0px'},
                    items: items
                }));

                // Get the previously selected value, if set, and apply it, or a default, to the
                // selector and progress bar.
                var dimValue = viewdataLayerData.getDimension(this.selectedLayerId, dimName);
                selectorConfiguration.setValue(dimValue);
                dimValue = selectorConfiguration.getValue();
                if (selectorConfiguration.isMultiValued()) {
                    var conf = this.getDimensionData(dimName, false);
                    conf.progress.updateProgress((1.0 * conf.currentIndex) / (conf.data.length - 1.0));
                    ViewdataDimensionControls.setActiveButtons(dimName, conf.currentIndex, conf.data.length);
                }
                this.setDimensionValue(dimName, dimValue);
            }
        } else {
            this.setNoLayer();
        }
        this.dimensionsForm.doLayout(false, true);
    };

    /**
     * Responds to click on progress bar by setting the dimension value according to the click position.
     * @param e - evnt
     */
    this.onProgressBarClick = function(e) {
        var vddc = this.vddc;
        var progress = this.progress;
        var dim = progress.id.substring(22);

        var conf = vddc.getDimensionData(dim);
        // Find interal corresponding to point clicked.
        var xOffset = e.xy[0] - progress.getPosition()[0];
        // For consistency with progress bar (rather than progress.getWidth()):
        var width = progress.el.dom.firstChild.offsetWidth;
        var idx = Math.floor((conf.data.length - 1.0) * xOffset / width + 0.5);
        var val = conf.data[idx];
        vddc.selectorsForDimension[dim].setValueByIndex(idx);
        conf.progress.updateProgress((1.0 * idx) / (conf.data.length - 1.0));
        ViewdataDimensionControls.setActiveButtons(dim, idx, conf.data.length);
        vddc.setDimensionValue(dim, val);
    }

    /**
     * Responds to press of go to start button.
     * @param btn - button
     * @param e - evnt
     */
    this.onGoToStart = function(btn, e) {
        var dim = btn.id.substring(23);
        var conf = this.getDimensionData(dim, true);
        if (conf.currentIndex > 0) {
            var idx = 0;
            var val = conf.data[idx];
            this.selectorsForDimension[dim].setValueByIndex(idx);
            conf.progress.updateProgress((1.0 * idx) / (conf.data.length - 1.0));
            ViewdataDimensionControls.setActiveButtons(dim, idx, conf.data.length);
            this.setDimensionValue(dim, val);
        }
    };

    /**
     * Responds to press of step backwards button.
     * @param btn - button
     * @param e - evnt
     */
    this.onStepBackwards = function(btn, e) {
        var dim = btn.id.substring(27);
        var conf = this.getDimensionData(dim, true);
        if (conf.currentIndex > 0) {
            var idx = conf.currentIndex - 1;
            var val = conf.data[idx];
            this.selectorsForDimension[dim].setValueByIndex(idx);
            conf.progress.updateProgress((1.0 * idx) / (conf.data.length - 1.0));
            ViewdataDimensionControls.setActiveButtons(dim, idx, conf.data.length);
            this.setDimensionValue(dim, val);
        }
    };

    /**
     * Responds to press of step forward button.
     * @param btn - button
     * @param e - evnt
     */
    this.onStepForward = function(btn, e) {
        var dim = btn.id.substring(26);
        var conf = this.getDimensionData(dim, true);
        if (conf.currentIndex < conf.data.length - 1) {
            var idx = conf.currentIndex + 1;
            var val = conf.data[idx];
            this.selectorsForDimension[dim].setValueByIndex(idx);
            conf.progress.updateProgress((1.0 * idx) / (conf.data.length - 1.0));
            ViewdataDimensionControls.setActiveButtons(dim, idx, conf.data.length);
            this.setDimensionValue(dim, val);
        }
    };

    /**
     * Responds to press of go to end button.
     * @param btn - button
     * @param e - evnt
     */
    this.onGoToEnd = function(btn, e) {
        var dim = btn.id.substring(21);
        var conf = this.getDimensionData(dim, true);
        if (conf.currentIndex < conf.data.length - 1) {
            var idx = conf.data.length - 1;
            var val = conf.data[idx];
            this.selectorsForDimension[dim].setValueByIndex(idx);
            conf.progress.updateProgress((1.0 * idx) / (conf.data.length - 1.0));
            ViewdataDimensionControls.setActiveButtons(dim, idx, conf.data.length);
            this.setDimensionValue(dim, val);
        }
    };

    /**
     * Responds to a change of selected dimension value.
     * @param combo - combo box on which the selection has been made
     * @param record - data record returned from the underlying store
     * @param index - index of the selected item in the dropdown list
     */
    this.onDimensionSelectionChanged = function(combo, record, index) {
        var dim = combo.id.substring(20).replace(/_\d+$/, '');
        var conf = this.getDimensionData(dim, false);

        if (conf.currentIndex != null) {
            conf.progress.updateProgress((1.0 * conf.currentIndex) / (conf.data.length - 1.0));
            ViewdataDimensionControls.setActiveButtons(dim, conf.currentIndex, conf.data.length);
            this.setDimensionValue(dim, conf.data[conf.currentIndex]);
        }
    };

    /**
     * Sets the value of a dimension in the cached value store and triggers a LAYER_DIMENSION_CHANGED
     * event to cause the layer to be redrawn.
     * @param dim - name of dimension
     * @param value - dimension value
     */
    this.setDimensionValue = function(dim, value) {
        if (viewdataLayerData.getDimension(this.selectedLayerId, dim) != value) {
            viewdataLayerData.setDimension(this.selectedLayerId, dim, value);

            this.eventsManager.triggerEvent("LAYER_DIMENSION_CHANGED", {param: dim, value: value});
        }
    };

    /**
     * Gets data relating a dimension.
     * @param dimName - name of dimension
     * @return {combo - ComboxBox for the dimension value
     *          progress - ProgressBar for the dimension
     *          data - data held in the store used for the ComboxBox
     *          currentIndex - currently selected index on the ComboxBox}
     */
    this.getDimensionData = function(dimName, resetToValid) {
        var prog = Ext.getCmp('vd-dimension-progress_' + dimName);
        var selectorConfiguration = this.selectorsForDimension[dimName];

        var idx = selectorConfiguration.getValueByIndex();
        if (!idx && resetToValid) {
            selectorConfiguration.resetToLastValue();
            idx = selectorConfiguration.getValueByIndex();
        }
        return {progress: prog,
                data: selectorConfiguration.dimensionData.dimensionValues,
                currentIndex: idx
               }
    };
}

/**
 * Sets the control buttons as enabled or disabled depending on whether the current value is at one end of the range.
 * @param dim - name of dimension
 * @param idx - index of currently selected value
 * @param numberValues - number of possible values
 */
ViewdataDimensionControls.setActiveButtons = function(dim, idx, numberValues) {
    var maxIdx = numberValues - 1;
    Ext.getCmp('vd-dimension-gotostart_' + dim).setDisabled((idx == 0));
    Ext.getCmp('vd-dimension-stepbackwards_' + dim).setDisabled((idx == 0));
    Ext.getCmp('vd-dimension-stepforwards_' + dim).setDisabled((idx == maxIdx));
    Ext.getCmp('vd-dimension-gotoend_' + dim).setDisabled((idx == maxIdx));
};
