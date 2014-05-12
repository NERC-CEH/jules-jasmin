"use strict";

/*jslint onevar: false*/

/** 
 * Control to handle the layer selections when dealing with WMC docs
 * @class
 *
 * @requires OpenLayers/Events.js
 * @requres YAHOO.widget
 * 
 * @author C Byrom
 */

/*global document:false, WMSC:false, Utils:false, OpenLayers:false, YAHOO:false, 
         $:false, LayerDefaultSetter:false, alert:false, window:false, Event:false */

/*jslint sub: true, */


WMSC.VisAppLayers = OpenLayers.Class.create();

//used to insert an element at the top of the list (used for drag and drop list of map layers)
function prependChild(parent, node) {
    parent.insertBefore(node, parent.firstChild);
}

function isPopupBlocker() {
    var oWin = window.open("./", "testpopupblocker");

    if (oWin === null || typeof(oWin) === "undefined") {
        return true;
    } else {
        oWin.close();
        return false;
    }
}
   
WMSC.VisAppLayers.prototype = {
    EVENT_TYPES: ["NEW_LAYER"],

    // The id of an element in which to render the layer selection tree
    treeDiv: null,
    
    // The id of an element in which to render the field selection list
    layerDiv: null,

    // OpenLayers Events object managing EVENT_TYPES
    events: null,

    /**
     * Constructor to initialise layer control
     * @constructor
     *
     * @param treeDiv - ID of div element in which to place the tree view control
     * @param layerDiv - ID of div element in which to place the layers drag and drop control
     * @param coordControl - coordinate control to use with layerControl
     *     NB, this control must include a method, updateDomainDiv(OpenLayers.Bounds)
     */
    initialize: function (treeDiv, layerDiv, wmcRetriever, newEndpointInputId, addNewEndpointBtnId, defaultOptionsList, eventsManager, furtherInfoLinks) 
    {
        WMSC.log("Initialising Control");
        this.treeDiv = treeDiv;
        this.layerDiv = layerDiv;
        
        this.wmcRetriever = wmcRetriever;
        
        this.endpointInputBox = $(newEndpointInputId);
        this.addNewEndpointBtn = $(addNewEndpointBtnId);
        
        if (this.addNewEndpointBtn !== null) {
            this.addNewEndpointBtn.onclick = this.onNewEndpointClick.bindAsEventListener(this);
        }
        
        this.eventsManager = eventsManager;
        this.furtherInfoLinks = furtherInfoLinks;

        this._selectedTreeNode = null;
        this._selectedLayer = null;
                
        this.tree = new YAHOO.widget.TreeView(this.treeDiv);
        
        // the label click event doesn't occur if the selected node is clicked on
        // because someone might want to add multiple copies of one layer 
        // (to compare different dimensions maybe) using the simple clickEvent which is always called
        //this.tree.subscribe('labelClick', this._selectTreeNode.bindAsEventListener(this));
        this.tree.subscribe('clickEvent', this._onTreeClick.bindAsEventListener(this));
        
        // Restrict behaviour of tree so that the selected node is always
        // on the open branch.
        this.tree.subscribe('expand', function (node) 
        {
            this._selectTreeNode(node);
            return true;
        }.bindAsEventListener(this));
        
        this.idIndex = 0;
        
        var globalDefaultParams = {
            format: 'image/png', 
            version: '1.3.0', 
            CRS: 'CRS:84', 
            transparent: 'true'
        };
        
        this.defaultSetter = new LayerDefaultSetter(globalDefaultParams, defaultOptionsList);
        
        this.layersToSelect = {};
        
        this._delIconHandlers = {};
        
        this.eventsManager.register('NEW_ENDPOINT', this, this.onNewEndpoint);
        
    },
    
    /**
     * Cleaning up is important for IE.
     */
    destroy: function () 
    {
        this.tree.unsubscribe();
    },
    
    /**
     * Add listeners to the delete icons on the tree view nodes
     * NB, these are lost each time the tree redraws itself, hence the
     * need to constantly refresh this list
     */
    addListeners: function ()
    {
        var i;
        
        for (i = 0; i < this.tree.getRoot().children.length; i++)
        {
            var index = this.tree.getRoot().children[i].index;
            var delIcon = document.getElementById("delIcon_" + index);
            if (delIcon !== null)
            {
                this._delIconHandlers[delIcon.id] = Utils.addHTMLEventListener(delIcon, 
                        'click', this._removeNode, this);                
            }
        }
        
        var infoNodes = document.getElementsByClassName('nodeInfo');
        for (i = 0; i < infoNodes.length; i++) {
            Utils.addHTMLEventListener(infoNodes[i], 'click', this._onInfoNodeClick, this);
        }
    },
    
    /**
     * Remove all the delete icon handlers form the current tree. This
     * should happen right before the tree is re-drawn.
     */
    removeListeners: function () {
        Utils.removeEventHandlersFromLookup(this._delIconHandlers);
        this._delIconHandlers = {};
    },
    
    /**
     * Redraw the whole tree control. This is needed as the event hanlders need
     * to be re-applied after the tree is re-drawn.
     */
    redrawTree: function () {
        
        WMSC.log("Redrawing tree");
        
        this.removeListeners();
        this.tree.draw();
        
        // add listeners again to the delete icons; these are lost when the tree redraws
        this.addListeners();
        
        //re apply the selected node (as the html will have been re-built
        if (this._selectedLayer !== null) {
            if (this._selectedLayer.labelElId) {
                var selectedElt = $(this._selectedLayer.labelElId);
                if (selectedElt === null) {
                    this._selectedLayer = null;
                }
                else {
                    selectedElt.className = 'WMSC_selectedField';
                }
            }
        }
    },

    /**
     * Add a WMC document to the tree view
     * @param wmsEndpoint - endpoint to retrieve the WMC doc from - NB, this is typically the localhost
     */
    addWebMapContext: function (wmcEndpoint) 
    {
        var root = this.tree.getRoot();
        var loadingLabel = '<table><tr><td class="nodeTitle">...loading</td></tr></table>';
        var loadingNode = new YAHOO.widget.TextNode({label: loadingLabel}, root, false);
                
        var bindDataToTree = function (wmc) 
        {
            this.tree.removeNode(loadingNode);
            var WMCNode = this._addWMCTree(wmc, wmcEndpoint);
            
            this.redrawTree();
            
            if (this.layersToSelect[wmcEndpoint] !== undefined) {
                this._selectEndpointLayers(wmcEndpoint, this.layersToSelect[wmcEndpoint]);
                this.layersToSelect[wmcEndpoint] = undefined;
            }
            
        };
        
        
        var onSecurityFail = function (resp) {
            this.tree.removeNode(loadingNode);
            this.redrawTree();
            if (resp.status == 403){
            alert('Login to secure service was unsucessful: you are logged in but do not have the correct permissions to access this data.');
            }
            else {alert('Login to secure service was unsucessful: the server responded with - '+ resp.text)
                 }
            return false;
        };
        
        var onRetriveWMCFail = function (resp) {
	    WMSC.log('response status = ' + resp.status);
            if (resp.status === 401) {
                
                //If the user's browser can show a modal dialog window and not
                //block it with a popup blocker, then show it
                var loginpage='./securitylogin?endpoint=' + wmcEndpoint;
                if (!isPopupBlocker()) {    
                    window.showModalDialog(loginpage, 'please log in', 'dialogHeight=500px', 'dialogWidth=800px');
                
                    //when logged in and new window closed, try again:
                    var successFn = bindDataToTree.bindAsEventListener(this);
                    var failureFn = onSecurityFail.bindAsEventListener(this);
                    this.wmcRetriever.getWMC(wmcEndpoint, successFn, failureFn);
                }
                else {
                    alert('Please enable popups for this site to login to the secure WMS');
                }
               
    
            }
            else if (resp.status == 403) {
                alert('Login to secure service was unsucessful: you are logged in but do not have the correct permissions to access this data.');
                this.tree.removeNode(loadingNode);
                this.redrawTree();
                WMSC.log("Attempt to retrive endpoint " + wmcEndpoint + " failed, response.status = " + resp.status + " (" + resp.statusText + ")" + ".");
            }
            else {
                alert("Attempt to retrive endpoint " + wmcEndpoint + " failed, response.status = " + resp.status + " (" + resp.statusText + ")" + ".");
                this.tree.removeNode(loadingNode);
                this.redrawTree();
                WMSC.log("Attempt to retrive endpoint " + wmcEndpoint + " failed, response.status = " + resp.status + " (" + resp.statusText + ")" + ".");
            } 
        };
        
        this.redrawTree();
        
        var successFn = bindDataToTree.bindAsEventListener(this);
        var failureFn = onRetriveWMCFail.bindAsEventListener(this);
                
        this.wmcRetriever.getWMC(wmcEndpoint, successFn, failureFn);
    },
    
    
    /**
     * Add WMC sub-layers to tree view as a new tree node
     *
     * @param wmc - the wmc object to add a root node for
     * @param wmcEndpoint - the endpoint url for the wmc object
     * @param parentNode - parent node in treeview
     */
    _addWMCTree: function (wmc, wmcEndpoint, parentNode) 
    {
        var i;
        var nodeData = {};
        var labelText = wmc.getTitle();// + " (" + wmcEndpoint + ")";

        var matchingInfoLinks = [];
        
        if (this.furtherInfoLinks !== null) {
            for (i = 0; i < this.furtherInfoLinks.length; i++) {
                var link = this.furtherInfoLinks[i];
                
                if (link.match(wmcEndpoint)) {
                    matchingInfoLinks.push(link);
                }
            }
        }
        
        
        nodeData.label = labelText;
        nodeData.layer = wmc.getTitle();
        nodeData['abstract'] = wmc.getTitle();
        nodeData.wmcEndpoint = wmcEndpoint;
        
        var wmcTreeNode = new YAHOO.widget.MenuNode(nodeData, this.tree.getRoot(), false);
        
        wmcTreeNode.label = this._createNodeLabel(labelText, wmcTreeNode.index, matchingInfoLinks);
        
        // add in the child nodes
        var subLayers = wmc.getSubLayers();
        
        for (i = 0; i < subLayers.length; i++) 
        {
            this._addLayerTree(subLayers[i], wmcEndpoint, wmcTreeNode);
        }
        
        return wmcTreeNode;
    },
    
    
    /**
     * Add WMS sub-layers to tree view as a new tree node
     *
     * @param layer - WMS sublayer to add
     * @param wmcEndpoint - the endpoint url this node is part of
     * @param parentNode - parent node in treeview
     */
    _addLayerTree: function (layer, wmcEndpoint, parentNode) {
        
        var labelText = layer.getAbstract();
        
        if (labelText === null || labelText === "") {
            labelText = layer.getTitle();
        }
        
        var nodeData = {};
        nodeData.wmcEndpoint = wmcEndpoint;
        nodeData.label = labelText;
        nodeData.layer = layer.getName();
        nodeData['abstract'] = layer.getAbstract();
        nodeData.layerData = layer;
        nodeData.title = layer.getAbstract(); //used for tooltips
        
        var treeNode = new YAHOO.widget.MenuNode(nodeData, parentNode, false);
        
        var subLayers = layer.getSubLayers();
        
        for (var i = 0; i < subLayers.length; i++) {
            this._addLayerTree(subLayers[i], wmcEndpoint, treeNode);
        }
         
        return treeNode;
    },
    
    /**
     * Add a label to a tree node - with a delete icon appended
     * 
     * @param nodeLabel - text content of label
     * @param nodeIndex - index in tree of label - used to identify the delete event
     */
    _createNodeLabel: function (nodeLabel, nodeIndex, infoLinks)
    {
        
        if (infoLinks === undefined || infoLinks.length === 0) {
            return '<table><tr><td class="nodeTitle">' + 
                nodeLabel + '</td><td class="delIcon">' +
                '<img id="delIcon_' + nodeIndex + '" src="js/img/close.gif" /></td></tr></table>';
        }
        else {
            
            var nodeInfo = '';
            
            for (var i = 0; i < infoLinks.length; i++) {
                var link = infoLinks[i];
                nodeInfo += '<td class="nodeInfo">' + link.getHTML() + '</td>';
            }
            
            return '<table><tr><td class="nodeTitle">' + 
            nodeLabel + '</td>' + nodeInfo + '<td class="delIcon">' +
            '<img id="delIcon_' + nodeIndex + '" src="js/img/close.gif" /></td></tr></table>';
        }
    },
     
    /**    
     * Respond to the user clicking on the delete icon for node - by removing this node
     *
     * @param evt
     */
    _removeNode: function (evt)
    {
        var delIcon = Event.element(evt);

        // get the node name from the icon ID
        var nodeIndex = delIcon.id.substring(delIcon.id.indexOf("_") + 1, delIcon.id.length);            
        
        var node = this.tree.getNodeByIndex(nodeIndex);
        
        this.tree.removeNode(node);
        
        // need to redraw to show this change 
        this.redrawTree();
    },
    
    /**
     * Called when a tree node is clicked on, because the clickEvent arguments 
     * are slightly different to the labelClick or Expand events just pulling out
     * the node and then calling _selectedTreeNode. 
     */
    _onTreeClick: function (args) {
        var node = args.node;
        this._selectTreeNode(node);
    },
    
    /**
     * Respond to a tree node being selected
     * - by highlighting this node and, if the node is
     * a layer, by adding it to the selected layer div
     */
    _selectTreeNode: function (node) {
        
        if (this._selectedLayer) {
            {
                $(this._selectedLayer.labelElId).className = node.labelStyle;
            }   
        }
        
        $(node.labelElId).className = 'WMSC_selectedField';
        
        // set the selected layer
        this._selectedLayer = node;        
        
        // If this node is a leaf, display the different layers available
        // NB, need to treat differently depending on whether we're dealing
        // with a GetCapabilities or a GetWebMapContext call
        if (node.children.length === 0) 
        {
        
            // check this isn't the 'loading...' leaf; escape if it is
            if (node.label.indexOf("...loading") > -1) {
                return;
            }

            //add the selected layer to the layers panel
            this._addLayer(node);

        }
    },
    
    /**
     * Add a new Layer to the layer list
     */
    _addLayer: function (node) 
    {    
        
        
        var newLayer = this.makeNewLayer(node.data.wmcEndpoint, node.data.layer);
        
        this.eventsManager.triggerEvent("NEW_LAYER", {layer: newLayer});
        
        return;
        
    },
    
    /**
     * create a new layer object using the default params and the url/name 
     * provided.
     * 
     * The layer.id is a combination of the url, layer name and an incrimenting 
     * index to ensure that it is unique for each layer
     */
    makeNewLayer: function (url, layerName) {
        
        var defaultParams = this.defaultSetter.getDefaults(url, layerName); 
        
        // because openlayesr adds the request and service params to the url
        // they have to be removed if they already exist to avoid confustion
        
        var removeParams = ['request', 'service'];
        url = Utils.removeParamsInUrl(url, removeParams);
        
        var layer = new OpenLayers.Layer.WMS("#" + this.idIndex + " " + layerName, 
                url, defaultParams, {isBaseLayer: false, buffer: 0});

        layer.params['LAYERS'] = layerName;
        layer.id = url + "_" + layer.name + "_" + this.idIndex;

        this.idIndex += 1;

        return layer;
    },
    
    /**
     * Event handler for the new endpoint button click
     */
    onNewEndpointClick: function (evt) {
        this.addWebMapContext(this.endpointInputBox.value);
    },
    
    onNewEndpoint: function (e) {
        this.addWebMapContext(e.url);
    },
    
    /**
     * Adds a layer to select on a particular endpoint when that endpoint is 
     * loaded.
     */
    addLayersToSelect: function (endpoint, layers) {
        this.layersToSelect[endpoint] = layers;
    },
    
    /**
     * Selects a given layer on a particular endpoint, this is used to setup 
     * the initial selection when the page is loaded.
     */
    _selectEndpointLayers: function (endpointURL, layers) {
        
        var endpointNode = this._getNodeForEndpoint(endpointURL);
        
        if (endpointNode === null) {
            WMSC.log("No node found for endpoint " + endpointURL);
            return;
        }
        
        if (endpointNode.expanded === false) {
            endpointNode.expand();
        }
        
        for (var i = 0; i < layers.length; i++) {
            var layerName = layers[i];
            var layerNode = this._getChildNodeForLayer(endpointNode, layerName);
            
            if (layerNode === null) {
                WMSC.log("No node found for layer " + layerName + " in endpoint " + endpointURL);
                continue;
            }
            
            this._expandNodeParentsFirst(layerNode);
            //layerNode.expand();
        }
        
    },
    
    /**
     * To avoid trying to set the selected class no nodes that haven't been 
     * created in the DOM yet, expand the given nodes from the bottom up. This
     * means that all the pairent nodes will be added to the DOM. 
     */
    _expandNodeParentsFirst: function (node) {
        if (node.parent) {
            this._expandNodeParentsFirst(node.parent);
        }
        
        if (node.expanded === false) {
            node.expand();
        }        
    },
    
    /**
     * Retrieve a node form the tree vieew that corresponds to a given endpoint
     */
    _getNodeForEndpoint: function (endpointURL) {
        var endpointNodes = this.tree.root.children;
        
        for (var i = 0; i < endpointNodes.length; i++) {
            var node = endpointNodes[i];
            if (node.data.wmcEndpoint === endpointURL) {
                return node;
            }
        }
        return null;
    },
    
    /**
     * Find the child node that matches the layerName given for a endpoint's node.
     */
    _getChildNodeForLayer: function (endpointNode, layerName) {
        
        for (var i = 0; i < endpointNode.children.length; i++) {
            var child = endpointNode.children[i];
            
            if (child.data.layer === layerName) {
                return child;
            }
            
            if (child.children.length >= 0) {
                var found = this._getChildNodeForLayer(child, layerName);
                
                if (found !== null) {
                    return found;
                }
            }
        }
        
        
        return null;
    },
    
    
    /**
     * This is needed to stop the event from triggering the treeview, any
     * links found in the info node should still be triggered. 
     */
    _onInfoNodeClick: function (e) {
        if (!e) {
            e = window.event;
        }
        
        e.cancelBubble = true;
        
        if (e.stopPropagation) {
            e.stopPropagation();
        }

        return false;
    }
};




