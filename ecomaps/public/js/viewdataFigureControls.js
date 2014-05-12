/** 
 * Creates and manages the controls for generating figures.
 * @class
 *
 * @requires OpenLayers/Events.js
 * 
 * @author R. Wilkinson
 */

/**
 * Constructor to initialise figure controls.
 * @constructor
 *
 * @param eventsManager - event manager
*/
function ViewdataFigureControls(eventsManager, initialBounds, figureOptions) {
    this.eventsManager = eventsManager;
    this.currentSelection = initialBounds;
    this.figureStyle = figureOptions.style;
    this.includeCaptionOptions = (figureOptions.style == 'viewdata');
    this.oneLayerOnly = (figureOptions.style == 'ipcc-ddc');
    this.defaultGrid = (figureOptions.style == 'ipcc-ddc');

    /**
     * Creates the figure controls.
     */
    this.createControls = function() {

        var formatStore = new Ext.data.ArrayStore({
            id: 'vd-figure-format_store',
            fields: ['value', 'display'],
            data: [
                ['image/png', 'PNG'],
                ['image/jpeg', 'JPG'],
                ['image/gif', 'GIF']
//                ['application/postscript', 'EPS'],
//                ['image/svg+xml', 'SVG']
            ]
        });

        var formItems = [];
        formItems.push({
            xtype: 'fieldset',
            title: 'Image',
            defaults: {bodyStyle: 'padding: 1px 0px'},
            items: [{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Format',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 1
                },{
                    xtype: 'combo',
                    hiddenName: 'figFormat',
                    editable: false,
                    forceSelection: true,
                    triggerAction: 'all',
                    allowBlank: false,
                    lazyRender: false,
                    mode: 'local',
                    store: formatStore,
                    valueField: 'value',
                    displayField: 'display',
                    fieldLabel: 'Format',
                    value: 'image/png',
                    flex: 2
                },{
                    xtype: 'button',
                    id : 'vd-help-figure-format-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-figure-format-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Height',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 1
                },{
                    xtype: 'numberfield',
                    id: 'vd-figure-height',
                    name: 'HEIGHT',
                    value: figureOptions.defaultheight,
                    allowBlank: false,
                    allowDecimals: false,
                    allowNegative: false,
                    minValue: figureOptions.minheight,
                    maxValue: figureOptions.maxheight,
                    flex: 2
                },{
                    xtype: 'button',
                    id : 'vd-help-figure-height-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-figure-height-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'label',
                    text: 'Width',
                    margins: {top:3, right:0, bottom:0, left:0},
                    flex: 1
                },{
                    xtype: 'numberfield',
                    id: 'vd-figure-width',
                    name: 'WIDTH',
                    value: figureOptions.defaultwidth,
                    allowBlank: false,
                    allowDecimals: false,
                    allowNegative: false,
                    minValue: figureOptions.minwidth,
                    maxValue: figureOptions.maxwidth,
                    flex: 2
                },{
                    xtype: 'button',
                    id : 'vd-help-figure-width-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-figure-width-text',
                hidden: true,
                cls: 'vd-help-panel'
            },{
                layout: 'hbox',
                pack: 'start',
                items: [{
                    xtype: 'checkbox',
                    id: 'vd-figure-grid',
                    name: 'figure-grid',
                    boxLabel: 'Draw grid',
                    checked: this.defaultGrid,
                    margins: {top:0, right:0, bottom:0, left:0}
                },{
                    flex: 1
                },{
                    xtype: 'button',
                    id : 'vd-help-figure-grid-btn',
                    enableToggle: true,
                    iconCls: 'vd-help-icon',
                    margins: {top:0, right:0, bottom:0, left:3},
                    toggleHandler: ViewdataHelp.toggleHelp
                }]
            },{
                id: 'vd-help-figure-grid-text',
                hidden: true,
                cls: 'vd-help-panel'
            }]
        });

        if (this.includeCaptionOptions) {
            formItems.push({
                xtype: 'fieldset',
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
                        id : 'vd-help-figure-caption-include-btn',
                        enableToggle: true,
                        iconCls: 'vd-help-icon',
                        toggleHandler: ViewdataHelp.toggleHelp
                    }]
                },{
                    id: 'vd-help-figure-caption-include-text',
                    hidden: true,
                    cls: 'vd-help-panel'
                },{
                    layout: 'hbox',
                    pack: 'start',
                    items: [{
                        xtype: 'checkbox',
                        id: 'vd-figure-legend-show-bounding-box',
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
                        id: 'vd-figure-legend-show-layer-names',
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
                        id: 'vd-figure-legend-show-style-names',
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
                        id: 'vd-figure-legend-show-dimensions',
                        name: 'figure-legend-show-dimensions',
                        boxLabel: 'Layer dimension names and values',
                        checked: true,
                        margins: {top:0, right:0, bottom:0, left:20}
                    }]
//                },{
//                    layout: 'hbox',
//                    pack: 'start',
//                    items: [{
//                        xtype: 'label',
//                        text: 'Height',
//                        margins: {top:3, right:0, bottom:0, left:0},
//                        flex: 1
//                    },{
//                        xtype: 'numberfield',
//                        id: 'vd-figure-legend-width',
//                        name: 'figure-legend-width',
//                        value: 600,
//                        allowDecimals: false,
//                        allowNegative: false,
//                        flex: 2
//                    }]
//                },{
//                    layout: 'hbox',
//                    pack: 'start',
//                    items: [{
//                        xtype: 'label',
//                        text: 'Width',
//                        margins: {top:3, right:0, bottom:0, left:0},
//                        flex: 1
//                    },{
//                        xtype: 'numberfield',
//                        id: 'vd-figure-legend-height',
//                        name: 'figure-legend-height',
//                        value: 200,
//                        allowDecimals: false,
//                        allowNegative: false,
//                        flex: 2
//                    }]
                }]
            });
        }

        this.figureForm = new Ext.FormPanel({
            title: 'Figure',
            id: 'vd-figure',
            standardSubmit: true,
            method: 'GET',
            url: './get_figure',
            border: true,
            frame: true,
            autoScroll: true,
            items: formItems,
            buttons: [{
                text: 'Make figure',
                id: 'vd-figure-make',
                listeners: {
                    click: this.onMakeFigure,
                    scope: this
                }
            }]
        });

        this.eventsManager.register('MAP_SELECTION_CHANGED', this, this.onChangeSelection);
    };

    this.onChangeSelection = function(e) {
        this.currentSelection = e.selection;
    };

    /**
     * Responds to the make figure button by collecting the parameters for the
     * figure and layers, and submitting a request to generate the figure.
     * @param btn - the pressed button
     * @param e - button click event
     */
    this.onMakeFigure = function(btn, e) {
        var tempInputs = [];
        var layerParams = [];// viewdataMapManager.makeLayerParameters(this.oneLayerOnly);
        for (var i = 0; i < layerParams.length; ++i) {
            tempInputs.push(new Ext.form.Hidden({id: layerParams[i].name, name: layerParams[i].name, value: layerParams[i].value}));
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
        tempInputs.push(new Ext.form.Hidden({id: 'BBOX', name: 'BBOX', value: bboxString}));
        tempInputs.push(new Ext.form.Hidden({id: 'figure-style', name: 'figure-style', value: this.figureStyle}));

        this.figureForm.add(tempInputs);
        this.figureForm.doLayout();
        var form = this.figureForm.getForm();
        form.getEl().dom.target = '_blank';
        form.submit();
        for (var i = 0; i < tempInputs.length; ++i) {
            this.figureForm.remove(tempInputs[i]);
        }
    };
}
