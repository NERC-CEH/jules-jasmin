/** 
 * Creates and manages the bounding box controls.
 * @class
 *
 * @requires OpenLayers/Events.js
 * 
 * @author R. Wilkinson
 */

/**
 * Constructor to initialise bounding box controls.
 * @constructor
 *
 * @param eventsManager - event manager
*/
function ViewdataBoundingBoxControls(eventsManager) {
    this.eventsManager = eventsManager;

    /**
     * Creates the dimension controls.
     */
    this.createControls = function() {
        var panelWidth = 222;
        this.boundingBoxForm = new Ext.Panel({
            title: 'Bounding Box',
            id: 'vd-boundingbox',
            layout: 'form',
            border: true,
            frame: true,
            autoScroll: true,
            items: [{
                width: panelWidth,
                items: [{
                    layout: 'hbox',
                    pack: 'start',
                    items: [{
                        xtype: 'label',
                        text: ' ',
                        flex: 1
                    },{
                        xtype: 'button',
                        id : 'vd-help-bounding-box-btn',
                        enableToggle: true,
                        iconCls: 'vd-help-icon',
                        toggleHandler: ViewdataHelp.toggleHelp
                    }]
                },{
                    id: 'vd-help-bounding-box-text',
                    hidden: true,
                    cls: 'vd-help-panel'
                },{
                    items: [{
                        xtype: 'fieldset',
                        width: panelWidth,
                        items: [{
                            // Add some space since padding not rendered on IE.
                            items: [{xtype: 'label', html: '&nbsp;', style: 'font-size:3px'}]
                        },{
                            layout: 'vbox',
                            // width: 200,
                            height: 200,
                            layoutConfig: {
                                align: 'stretch'
                            },
                            items: [{
                                layout: 'column',
                                flex: 1,
                                border: false,
                                items: [{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .5
                                },{
                                    id: 'bboxN',
                                    name: 'bboxN',
                                    xtype: 'numberfield',
                                    autoCreate: {tag: 'input', type: 'text', size: '5', autocomplete: 'off'}
                                },{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .5
                                }]
                            },{
                                layout: 'column',
                                flex: 0.75,
                                border: false,
                                items: [{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .5
                                },{
                                    xtype: 'label',
                                    text: 'N',
                                    style: 'font-weight:bold',
                                    flex: 1
                                },{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .5
                                }]
                            },{
                                layout: 'column',
                                flex: 1,
                                border: false,
                                items: [{
                                    id: 'bboxW',
                                    name: 'bboxW',
                                    xtype: 'numberfield',
                                    autoCreate: {tag: 'input', type: 'text', size: '5', autocomplete: 'off'},
                                    columnWidth: .2
                                },{
                                    xtype: 'label',
                                    text: 'W',
                                    style: 'text-align: center; font-weight:bold',
                                    columnWidth: .2
                                },{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .2
                                },{
                                    xtype: 'label',
                                    text: 'E',
                                    style: 'text-align: center; font-weight:bold',
                                    columnWidth: .2
                                },{
                                    id: 'bboxE',
                                    name: 'bboxE',
                                    xtype: 'numberfield',
                                    autoCreate: {tag: 'input', type: 'text', size: '5', autocomplete: 'off'},
                                    columnWidth: .2
                                }]
                            },{
                                layout: 'column',
                                flex: 0.75,
                                border: false,
                                items: [{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .5
                                },{
                                    xtype: 'label',
                                    text: 'S',
                                    style: 'font-weight:bold',
                                    flex: 1
                                },{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .5
                                }]
                            },{
                                layout: 'column',
                                flex: 1,
                                border: false,
                                items: [{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .5
                                },{
                                    id: 'bboxS',
                                    name: 'bboxS',
                                    xtype: 'numberfield',
                                    autoCreate: {tag: 'input', type: 'text', size: '5', autocomplete: 'off'}
                                },{
                                    xtype: 'label',
                                    html: '&nbsp;',
                                    columnWidth: .5
                                }]
                            }]
                        }],
                        buttons: [{
                            text: 'Set selection',
                            id: 'WMSC_set_bounds'
                        }, {
                            text: 'Reset selection',
                            id: 'WMSC_clear'
                        }]
                    }]
                }]
            }]
        });
    };
}
