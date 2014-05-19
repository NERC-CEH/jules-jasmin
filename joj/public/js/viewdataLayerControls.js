/** 
 * Creates and manages the layer selection controls.
 * @class
 *
 * @requires OpenLayers/Events.js
 * 
 * @author R. Wilkinson
 */

/**
 * Constructor to initialise layer controls.
 * @constructor
 *
 * @param eventsManager - event manager
*/
function ViewdataLayerControls(eventsManager, maxLayers, loginDialog) {
    this.ROW_SELECT_COL = 1; // the column that is selected to indicate selection of the row
    this.eventsManager = eventsManager;
    this.maxLayers = maxLayers;
    this.loginDialog = loginDialog;
    this.displayOptionsRetriever = new DisplayOptionsRetriever();

    /**
     * Creates the layer selection controls.
     * @param selectOnLoad - list of layer IDs to select when first found
     */
    this.createControls = function(selectOnLoad) {
        // Override a tree loader function to make the timeout configurable.
        Ext.tree.TreeLoader.override({
            requestData : function(node, callback, scope){
                if (this.fireEvent("beforeload", this, node, callback) !== false) {
                    if (this.directFn) {
                        var args = this.getParams(node);
                        args.push(this.processDirectResponse.createDelegate(this, [{callback: callback, node: node, scope: scope}], true));
                        this.directFn.apply(window, args);
                    } else {
                        this.transId = Ext.Ajax.request({
                            method: this.requestMethod,
                            url: this.dataUrl||this.url,
                            success: this.handleResponse,
                            failure: this.handleFailure,
                            timeout: this.timeout || 30000,
                            scope: this,
                            argument: {callback: callback, node: node, scope: scope},
                            params: this.getParams(node)
                        });
                    }
                } else {
                    // if the load is cancelled, make sure we notify
                    // the node that we are done
                    this.runCallback(callback, scope || node, []);
                }
            },

            processResponse : function(response, node, callback, scope){
                var json = response.responseText;
                try {
                    var o = response.responseData || Ext.decode(json);
                    node.beginUpdate();
                    for(var i = 0, len = o.length; i < len; i++){
                        var n = this.createNode(o[i]);
                        if(n){
                            node.appendChild(n);
                        }
                    }
                    node.endUpdate();
                    this.runCallback(callback, scope || node, [node]);
                }catch(e){
                    this.handleFailure(response);
                }
            }
        });

        // Define datasets tree.
        var datasetTreeLoader = new Ext.tree.TreeLoader({
            uiProviders: {dataset: Ext.ux.tree.DatasetTreeNodeUI},
            dataUrl: "./get_datasets",
            listeners: {
                loadexception: this.nodeLoadFailed,
                scope: this
            }
        });

        datasetTreeLoader.timeout = 120000;

        var selectOnLoad = selectOnLoad;
        /**
         * Handle a node loaded event. Selects any layers in the preselected list the first time
         * they are found.
         * @param node - tree node that has been selected
         */
        var nodeLoaded = function(node) {
            var newSelectOnLoad = [];
            for (var i = 0; i < selectOnLoad.length; ++i) {
                var node = this.datasetTree.getNodeById(selectOnLoad[i]);
                if (node) {
                    this.selectLayerByNode(node);
                } else {
                    newSelectOnLoad.push(selectOnLoad[i]);
                }
            }
            selectOnLoad = newSelectOnLoad;
            if (selectOnLoad.length == 0) {
                this.datasetTree.removeListener('load', nodeLoaded, this);
            }
        };

        this.datasetTree = new Ext.tree.TreePanel({
            title: 'Datasets',
            tabTip: 'Datasets and endpoints',
            id: 'tree_datasets',
            loader: datasetTreeLoader,
            root: new Ext.tree.AsyncTreeNode({
                text: null,
                expanded: true,
                draggable: false,
                id: '0'
            }),
            rootVisible: false,
            listeners: {
                click: this.layerSelected,
                load: nodeLoaded,
                removeclicked: this.removeEndpoint,
                scope: this
            },
            autoScroll: true,
            border: false
        });


        // Define layer list.
        var layerListStore = new Ext.data.ArrayStore({
            // store configs
            autoDestroy: true,
            storeId: 'myStore',
            // reader configs
            idIndex: 0,
            listeners: {
                update: this.layerRecordUpdated,
                scope: this
            },
            fields: [
                'id', 'layer', {name: 'display', type: 'bool'}
            ],
            data: []
        });

        this.layerListColumnModel = new Ext.grid.ColumnModel({
            columns: [{
                header: 'ID',
                hidden: true,
                dataIndex: 'id'
            },{
                id: 'layer',
                header: 'Layer',
                width: 250,
                dataIndex: 'layer',
                renderer: function(val, cell) {
                    var strings = val.split('\f');
                    var title = strings[0].replace(/"/g, '&quot;');
                    var tip = strings[1].replace(/"/g, '&quot;');
                    cell.attr = 'ext:qtitle="' + title + '" ext:qtip="' + tip + '" ext:qwidth="350"';
                    return strings[0];
                }
            },{
                xtype: 'checkcolumn',
                header: 'Display',
                width: 20,
                dataIndex: 'display',
                tooltip: 'Display layer'
            },{
                xtype: 'actioncolumn',
                width: 20,
                items: [{
                    iconCls: 'vd-remove-icon',
                    tooltip: 'Remove layer',
                    handler: this.layerRowRemoved,
                    scope: this
                }]
            }]
        });

        this.layerList = new Ext.grid.EditorGridPanel({
            store: layerListStore,
            region: 'center',
            autoScroll: true,
            selModel: new Ext.grid.CellSelectionModel({
                singleSelect: true,
                listeners: {
                    beforecellselect: this.beforeLayerCellSelected,
                    cellselect: this.layerCellSelected,
                    scope: this
                }
            }),
            enableDragDrop: true,
            hideHeaders: true,
            emptyText: 'No layers',
            autoExpandColumn: 'layer',
            colModel: this.layerListColumnModel,
            plugins: [new Ext.ux.dd.GridDragDropRowOrder({
                listeners: {
                    afterrowmove: this.layersReordered,
                    scope: this
                }
            })]
        });
    };

    /**
     * Displays an error message when loading of data for a tree node fails.
     * @param scope - tree loader
     * @param node - tree node that has been selected
     * @param response - response from data load request
     */
    this.nodeLoadFailed = function(scope, node, response) {
        if (response.status === 401) {
            this.loginDialog.showUnauthorisedDialog(this.nodeReload.bind(this, node));
        } else {
            Ext.MessageBox.show({title: "Load failure",
                                 msg: "Loading of data for " + node.text + " failed: " +
                                 response.status + " " + response.statusText,
                                 buttons: Ext.MessageBox.OK, minWidth: 250});
        }
    };

    this.nodeReload = function(node) {
        node.reload();
    };

    /**
     * Handle a layer selected event.
     * @param node - tree node that has been selected
     * @param event - selection event
     */
    this.layerSelected = function(node, event) {
        if (node.id == "ep:new_session_endpoint") {
            this.promptForNewEndpoint(node);
        } else {
            this.selectLayerByNode(node);
        }
    };

    /**
     * Handles a remove node event.
     * @param node - tree node that has been selected
     * @param event - click event
     */
    this.removeEndpoint = function(node, event) {
        var params = {'endpointId': node.id};
        var req = new Ajax.Request('./remove_session_endpoint',
                                   {
                                       parameters: params,
                                       method: "get",
                                       onSuccess: this.removeEndpointOnSuccess.bind(this, node),
                                       onException: function(resp, e) {
                                           WMSC.log("Exception:" + e);
                                       },
                                       onFailure: function(resp) {
                                           WMSC.log("Failure:" + resp);
                                       }
                                   }
                                  );
    };

    /**
     * In response to a selection of a layer in the dataset tree, adds it to the layer list and
     * updates the map display.
     * @param node - tree node that has been selected
     */
    this.selectLayerByNode = function(node) {
        var nodeType = ViewdataLayerControls.nodeTypeFromId(node.id);
        if (nodeType === "ds" || nodeType==="ll") {
            var text = node.text;

            var parentNode = node.parentNode;
            if (parentNode && parentNode.text) {
                text = text + " (" + parentNode.text + ")";
            }

            // Construct tooltip from the strings defined for the node and its antecedents.
            var qtipList = [];
            for (var n = node; n != null; n = n.parentNode) {
                if (n.attributes.qtip) {
                    var qtip = n.text;
                    if (n.attributes.qtip && (n.text !== n.attributes.qtip)) {
                        qtip = qtip + " - <span style='font-style: italic;'>" + n.attributes.qtip + "</span>";
                    }
                    qtipList.push(qtip);
                }
            }
            if (qtipList.length > 1) {
                qtipList.reverse();
                var qtip = "<ul style='list-style:disc inside none;'><li>" + qtipList.join('</li><li>') + '</li></ul>';
            } else if (qtipList.length == 1) {
                var qtip = qtipList[0];
            } else {
                var qtip = '';
            }

            // Add new layer to top of list.
            var newLayer = [node.id, text + '\f' + qtip, true];
            var mergeResult = this.mergeLayer(node.id, newLayer);

            if (mergeResult.selectedLayers.length > this.maxLayers) {
                Ext.MessageBox.show({msg: "No more than " + this.maxLayers + " layers can be selected.",
                                     buttons: Ext.MessageBox.OK,
                                     minWidth: 250});
                return;
            }

            this.handleSelectedLayer(node.id, mergeResult);
        }
    };

    /**
     * Updates the list of layers in the layer list after a layer has been selected.
     * @param mergeResult - result of merging the selected layer into the list
     */
    this.updateLayerList = function(mergeResult) {
        var layerListStore = new Ext.data.ArrayStore({
            // store configs
            autoDestroy: true,
            storeId: 'layerListStore',
            // reader configs
            idIndex: 0,
            listeners: {
                update: this.layerRecordUpdated,
                scope: this
            },
            fields: [
                'id', 'layer', {name: 'display', type: 'bool'}
            ],
            data: mergeResult.selectedLayers
        });

        this.layerList.reconfigure(layerListStore, this.layerListColumnModel);

        // Select the newly added row.
        var selModel = this.layerList.getSelectionModel();
        selModel.suspendEvents(false);
        selModel.select(mergeResult.newRowIndex, this.ROW_SELECT_COL);
        selModel.resumeEvents();
    };

    /**
     * Merges a new layer into the selected layer list. It will be placed first in order unless the
     * top layer is distinct from the new one and has the property 'stickyAtTop' set. It determines
     * whether the new layer is already in the list, in which case the result is just a reordering
     * (or no change).
     * @param newId - ID of new layer
     * @param newLayer - record for the new layer
     * @return merge result: {selectedLayers, reorder, newRowIndex}
     */
    this.mergeLayer = function(newId, newLayer) {
        var selectedLayers = [];
        var store = this.layerList.getStore();
        var records = store.getRange();
        var reorder = false;
        var rowsAbove = (((records.length > 0) && (records[0].data.id != newId)
                          && (viewdataLayerData.getProperty(records[0].data.id, 'stickyAtTop'))) ? 1 : 0);
        for (var i = 0; i < rowsAbove; ++i) {
            // Append existing layer unless it's the selected one in which case it has already been added.
            if (records[i].data.id == newId) {
                reorder = true;
            } else {
                selectedLayers.push([records[i].data.id, records[i].data.layer, records[i].data.display]);
            }
        }
        selectedLayers.push(newLayer);
        for (var i = rowsAbove; i < records.length; ++i) {
            // Append existing layer unless it's the selected one in which case it has already been added.
            if (records[i].data.id == newId) {
                reorder = true;
            } else {
                selectedLayers.push([records[i].data.id, records[i].data.layer, records[i].data.display]);
            }
        }

        return {selectedLayers: selectedLayers, reorder: reorder, newRowIndex: rowsAbove};
    }

    /**
     * Get data for the selected layer and display it.
     * @param nodeId - ID of selected tree node
     * @param mergeResult - result of merging the selected layer into the list
     */
    this.handleSelectedLayer = function(nodeId, mergeResult) {
        if (viewdataLayerData.getProperty(nodeId, 'layerData') == null) {
            this.getLayerData(nodeId, mergeResult);
        } else {
            this.displayLayer(nodeId, mergeResult);
        }
    };

    /**
     * Retrieve layer data by AJAX call to application server.
     * @param nodeId - ID of selected tree node
     * @param mergeResult - result of merging the selected layer into the list
     */
    this.getLayerData = function(nodeId, mergeResult) {
        var params = {'layerid': nodeId};
        var req = new Ajax.Request('./get_layer_data',
                                   {
                                       parameters: params,
                                       method: "get",
                                       onSuccess: this.getLayerDataOnSuccess.bind(this, nodeId, mergeResult),
                                       onException: (function(resp, e) {
                                           WMSC.log("Exception in get_layer_data request: " + e);
                                           this.getLayerDataOnError("Error retrieving information about layer: " + e);
                                       }).bind(this),
                                       onFailure: (function(resp) {
                                           WMSC.log("Failure in get_layer_data request: " + resp);
                                           this.getLayerDataOnError("Error retrieving information about layer: " + resp.status +
                                                                    " " + resp.statusText);
                                       }).bind(this)
                                   }
                                  );
    };

    /**
     * Handle successful retrieval of the capabilities for a layer.
     * @param nodeId - ID of selected tree node
     * @param mergeResult - result of merging the selected layer into the list
     * @param resp - XML HTTP request response
     */
    this.getLayerDataOnSuccess = function(nodeId, mergeResult, resp) {
        if (resp.responseText) {
            var responseObj = JSON.parse(resp.responseText)
            if (responseObj) {
                viewdataLayerData.setProperty(nodeId, 'layerData', responseObj);
                this.displayLayer(nodeId, mergeResult);
            } else {
                WMSC.log("Invalid response to get_layer_data request");
                this.getLayerDataOnError("Error retrieving information about layer");
            }
        } else {
            WMSC.log("Empty response to get_layer_data request");
            this.getLayerDataOnError("Error retrieving information about layer");
        }
    };

    /**
     * Display message when retrieval of the capabilities for a layer fails.
     * @param msg - message to display
     */
    this.getLayerDataOnError = function(msg) {
        Ext.MessageBox.show({title: "Load failure", msg: msg,
                             buttons: Ext.MessageBox.OK,
                             minWidth: 250});
    };

    /**
     * Display a layer defined through its web map capabilities.
     * If the layer is in the layer list already, this will result in a update to which layer is
     * currently selected, an update to the order of the layers in the map and a redisplay of the
     * map.
     * @param nodeId - ID of layer corresponding to the selected node
     * @param mergeResult - result of merging the selected layer into the list
     */
    this.displayLayer = function(nodeId, mergeResult) {
        this.updateLayerList(mergeResult);

        var layerDataResult = viewdataLayerData.getProperty(nodeId, 'layerData');

        if (layerDataResult instanceof Array) {

            for(var i=0; i <layerDataResult.length;i++) {
                layerData = layerDataResult[i];
                var newId = nodeId + '_' + i;
                var result = this.mergeLayer(newId, [newId, layerData.title + '\f' + layerData.title, true]);
                this.updateLayerList(result);
                this.eventsManager.triggerEvent("LEGEND_LAYER_INVALID");
                if (!mergeResult.reorder) {
                    this.eventsManager.triggerEvent("LAYER_ADDED", {id: newId, layerData: layerData});
                }

                this.eventsManager.triggerEvent("LAYER_SELECTED",
                                                {id: newId, layerData: layerData, eventToPropagate: "SELECTED_LAYER_CHANGED"});

                //this.getLayerDisplayOptcheckions(newId, layerData);

                this.handleLayersReordered();
            }
        }
        else {

            this.eventsManager.triggerEvent("LEGEND_LAYER_INVALID");
            if (!mergeResult.reorder) {
                this.eventsManager.triggerEvent("LAYER_ADDED", {id: nodeId, layerData: layerDataResult});
            }

            this.eventsManager.triggerEvent("LAYER_SELECTED",
                                            {id: nodeId, layerData: layerDataResult, eventToPropagate: "SELECTED_LAYER_CHANGED"});
            this.getLayerDisplayOptions(nodeId, layerDataResult);

            this.handleLayersReordered();
        }
    };

    /**
     * Gets display options for the layer if there is a GetDisplayOptions URL and triggers
     * LAYER_SELECTED events for update of layer styles and the legend (which depends on the syle).
     * @param nodeId - ID of layer corresponding to the selected node
     * @param layerData - layer data for selected layer
     */
    this.getLayerDisplayOptions = function(nodeId, layerData) {
        if (layerData.getDisplayOptionsUrl) {
            this.displayOptionsRetriever.getDisplayOptions(layerData.getDisplayOptionsUrl,
                                                           this.getLayerDisplayOptionsOnSuccess.bind(
                                                               {id: nodeId, layerData: layerData, scope: this}),
                                                           this.getLayerDisplayOptionsOnException.bind(
                                                               {id: nodeId, layerData: layerData, scope: this}),
                                                           this.getLayerDisplayOptionsOnFailure.bind(
                                                               {id: nodeId, layerData: layerData, scope: this}));
        } else {
            this.eventsManager.triggerEvent("LAYER_STYLES_SET", {id: nodeId, layerData: layerData});
            this.eventsManager.triggerEvent("LAYER_SELECTED",
                                            {id: nodeId, layerData: layerData, eventToPropagate: "LEGEND_LAYER_CHANGED"});
        }
    };

    /**
     * On success handler for DisplayOptionsRetriever.getDisplayOptions - adds the display options
     * to the layers stored data, triggers LAYER_SELECTED events for update of layer styles and the
     * legend.
     * @param displayOptions - retrieved display options
     */
    this.getLayerDisplayOptionsOnSuccess = function(displayOptions) {
        this.layerData.displayOptions = displayOptions;
        this.scope.eventsManager.triggerEvent("LAYER_STYLES_SET", {id: this.id, layerData: this.layerData});
        this.scope.eventsManager.triggerEvent("LAYER_SELECTED",
                                              {id: this.id, layerData: this.layerData, eventToPropagate: "LEGEND_LAYER_CHANGED"});
    };

    /**
     * On failure handler for DisplayOptionsRetriever.getDisplayOptions - triggers LAYER_SELECTED
     * events for update of layer styles and the legend.
     * @param displayOptions - retrieved display options
     */
    this.getLayerDisplayOptionsOnException = function(resp, e) {
        this.scope.eventsManager.triggerEvent("LAYER_STYLES_SET", {id: this.id, layerData: this.layerData});
        this.scope.eventsManager.triggerEvent("LAYER_SELECTED",
                                              {id: this.id, layerData: this.layerData, eventToPropagate: "LEGEND_LAYER_CHANGED"});
        WMSC.log("Exception:" + e);
    };

    /**
     * On failure handler for DisplayOptionsRetriever.getDisplayOptions - triggers LAYER_SELECTED
     * events for update of layer styles and the legend.
     * @param displayOptions - retrieved display options
     */
    this.getLayerDisplayOptionsOnFailure = function(resp) {
        this.scope.eventsManager.triggerEvent("LAYER_STYLES_SET", {id: this.id, layerData: this.layerData});
        // Update legend after styles
        this.scope.eventsManager.triggerEvent("LAYER_SELECTED",
                                              {id: this.id, layerData: this.layerData, eventToPropagate: "LEGEND_LAYER_CHANGED"});
        WMSC.log("Failure:" + resp);
    };

    /**
     * Prompts for the user to enter the URL of a new endpoint.
     * @param node - tree node from which request was initiated
     */
    this.promptForNewEndpoint = function(node) {
        Ext.MessageBox.show({title: "Add Map Service", prompt: true, msg: "Enter the URL of a Web Map Service",
                             scope: {layerControls: this, node: node}, fn: this.addEndpoint,
                             buttons: Ext.MessageBox.OKCANCEL, width: 500});
    };

    /**
     * Adds a user entered endpoint URL.
     * @param btnId - ID string of the button pressed
     * @param value - the user entered URL value
     */
    this.addEndpoint = function(btnId, value) {
        if (btnId != "ok") {
            return;
        }

        var params = {'url': value};
        var req = new Ajax.Request('./add_session_endpoint',
                                   {
                                       parameters: params,
                                       method: "get",
                                       onSuccess: this.layerControls.addEndpointOnSuccess.bind(this.layerControls, this.node, value),
                                       onException: function(resp, e) {
                                           WMSC.log("Exception:" + e);
                                       },
                                       onFailure: function(resp) {
                                           WMSC.log("Failure:" + resp);
                                       }
                                   }
                                  );
    };

    /**
     * Handler after a session endpoint has been added.
     * @param node - tree node from which request was initiated
     * @param value - new endpoint URL
     * @param resp - AJAX response
     */
    this.addEndpointOnSuccess = function(node, value, resp) {
        if (resp.responseText) {
            var responseObj = JSON.parse(resp.responseText)
            if (responseObj) {
                if (responseObj.error) {
                    Ext.MessageBox.show({title: "Add map service failure",
                                         msg: responseObj.error,
                                         buttons: Ext.MessageBox.OK, minWidth: 250});
                } else {
                    node.parentNode.appendChild(responseObj);
                }
            }
        }
    };

    /**
     * Handler after a session endpoint has been removed.
     * @param node - tree node from which request was initiated
     * @param resp - AJAX response
     */
    this.removeEndpointOnSuccess = function(node, resp) {
        node.remove();
    };

    /**
     * Handler after the layer list is reordered.
     * @param gridDropTarget - Ext.ux.dd.GridDragDropRowOrder plugin
     * @param rowIndex - source index of moved data
     * @param rindex - index of row to which row(s) moved
     * @param selections - data records for row(s) moved
     */
    this.layersReordered = function(gridDropTarget, rowIndex, rindex, selections) {
        this.handleLayersReordered();
    };

    /**
     * Triggers a LAYER_LIST_REORDERED event with the new ordering of the layers.
     */
    this.handleLayersReordered = function() {
        var store = this.layerList.getStore();
        var records = store.getRange();
        var layerIds = this.getLayerIdsToDisplay(records);
        this.eventsManager.triggerEvent("LAYER_LIST_REORDERED", layerIds);
    };

    /**
     * Before selection handler for a layer in the layer list - only allow selection to procede if
     * the cell is in the name column.
     * @param selectionModel - selection model
     * @param rowIndex - index of selected row
     * @param record - record corresponding to selected row
     */
    this.beforeLayerCellSelected = function(selectionModel, rowIndex, colIndex) {
        return (colIndex == this.ROW_SELECT_COL);
    };

    /**
     * Handler for selection of a layer in the layer list - displays the corresponding legend.
     * @param selectionModel - selection model
     * @param rowIndex - index of selected row
     * @param record - record corresponding to selected row
     */
    this.layerCellSelected = function(selectionModel, rowIndex, colIndex) {
        var store = this.layerList.getStore();
        var records = store.getRange();
        var record = records[rowIndex]
        var layerData = viewdataLayerData.getProperty(record.data.id, 'layerData');
        this.eventsManager.triggerEvent("LEGEND_LAYER_INVALID");
        this.eventsManager.triggerEvent("LAYER_SELECTED", {id: record.data.id, layerData: layerData, eventToPropagate: "SELECTED_LAYER_CHANGED"});
        this.eventsManager.triggerEvent("LAYER_STYLES_SET", {id: record.data.id, layerData: layerData});
        this.eventsManager.triggerEvent("LAYER_SELECTED", {id: record.data.id, layerData: layerData, eventToPropagate: "LEGEND_LAYER_CHANGED"});
    };

    /**
     * Handler update of record. Only the display value is editable, so this
     * method controls selective display of layers.
     * @param store - store containing the record
     * @param record - updated record
     * @param operation - operation performed on record
     */
    this.layerRecordUpdated = function(store, record, operation) {
        if (operation == Ext.data.Record.EDIT) {
            // Removes dirty record indicator.
            record.commit();

            var records = store.getRange();
            var layerIds = this.getLayerIdsToDisplay(records);
            this.eventsManager.triggerEvent("LAYER_LIST_REORDERED", layerIds);
        }
    };

    /**
     * Handler for removal of a layer from the layer list.
     * @param grid - grid from which row is removed
     * @param rowIndex - index of selected row
     * @param colIndex - index of column
     */
    this.layerRowRemoved = function(grid, rowIndex, colIndex) {
        var store = grid.getStore();
        var record = store.getAt(rowIndex);
        var removedId = record.data.id;
        var selModel = grid.getSelectionModel();
        var selCell = selModel.getSelectedCell();
        var selRow = 0;
        if (selCell) {
            selRow = selCell[0];
        }

        store.removeAt(rowIndex);
        if (!viewdataLayerData.getProperty(removedId, 'preconfigured')) {
            viewdataLayerData.deleteLayer(removedId);
        }

        var records = store.getRange();
        var layerIds = this.getLayerIdsToDisplay(records);
        this.eventsManager.triggerEvent("LAYER_LIST_REORDERED", layerIds);
        this.eventsManager.triggerEvent("LAYER_REMOVED", removedId);

        // Reselect the currently selected row or the one above if the selection was deleted.
        if ((selRow >= rowIndex) && (selRow > 0)) {
            --selRow;
        }
        if (records.length > 0) {
            selModel.select(selRow, this.ROW_SELECT_COL);
        } else {
            this.eventsManager.triggerEvent("LAYER_SELECTED",
                                            {id: null, layerData: null, eventToPropagate: "SELECTED_LAYER_CHANGED"});
            this.eventsManager.triggerEvent("LAYER_SELECTED",
                                            {id: null, layerData: null, eventToPropagate: "LEGEND_LAYER_CHANGED"});
        }
    };

    /**
     * Gets the IDs of the layers enabled for display in order.
     * @param records - list records
     */
    this.getLayerIdsToDisplay = function(records) {
        var layerIds = [];
        for (var i = 0; i < records.length; ++i) {
            layerIds.push({id: records[i].data.id, display: records[i].data.display});
        }
        return layerIds;
    };
}

/**
 * Determines a node type from a node ID.
 * @param id - node ID
 */
ViewdataLayerControls.nodeTypeFromId = function(id) {

    if(id.substr(0,2) === "ds") {
        return id.substr(0,2);
    }

    var pos = id.indexOf(":");
    if (pos > 0) {
        return id.substr(0, pos);
    } else {
        return "";
    }
};
