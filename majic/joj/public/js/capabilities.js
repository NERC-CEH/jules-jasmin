"use strict";

/**
 * Various objects for wrappering capabilities and web map context documents
 * - borrowed from the DCIP code to use in the view functionality for WMC and granules data
 * C Byrom
 */

/*globals WMSC: false*/

/*jslint white: false, eqeqeq: false, onevar: false*/

// For resolving XML Namespaces in XPath expressions
WMSC.nsMap = {
  wms: 'http://www.opengis.net/wms',
  xlink: 'http://www.w3.org/1999/xlink'
};

/* A poor man's XPath */
WMSC._searchElement = function (node, element) 
{
    var i, node2, children;

    children = node.childNodes;
    for (i=0; i<children.length; i++) 
    {
        node2 = children[i];
        if (node2.nodeName == element) { 
            return node2;
        }
    }
    return null;
};
WMSC.traverseWMSDom = function (node, elements) {
    var i;

    for (i=0; i<elements.length; i++) {
        node = WMSC._searchElement(node, elements[i]);
    
        if (node === null) {
            return null;
        }
    }
    
    return node;
};

WMSC.getTextContent = function (el) {
    if (el.textContent) {
        return el.textContent;
    }
    else {
        return el.text;
    }
};

WMSC.trim = function (str) {
    return str.replace(/^\s+/g, "").replace(/\s+$/g, "");
};

/**
 * Class to wrapper a GetCapabilities document and expose
 * useful properties easily
 */
WMSC.Capabilities = function(domElement) {
    this.dom = domElement;
};
WMSC.Capabilities.prototype = {
        
    evaluate: function(expr, node) {
        if (node === null) {
            node = this.dom;
        }
        
        return WMSC.evalXPath(expr, node);
    },

    getTitle: function() {
        var el = WMSC.traverseWMSDom(this.dom, ['Service', 'Title']);
        return WMSC.getTextContent(el);
    },
    
    getAbstract: function() {
        var el = WMSC.traverseWMSDom(this.dom, ['Service', 'Abstract']);
        return WMSC.getTextContent(el);        
    },
    
    getRootLayer: function() {
        var rootLayer = WMSC.traverseWMSDom(this.dom, ['Capability', 'Layer']);
        if (rootLayer === null) {
            return null;
        }
        return new WMSC.Layer(rootLayer);
    },
    
    getEndpoint: function() {
        var or = WMSC.traverseWMSDom(this.dom, ['Service', 'OnlineResource']);
        if (or === null) {
            return null;
        }
        var attr = or.getAttribute('href');
        if (!attr) {
            attr = or.getAttribute('xlink:href');
        }
        return attr;
    },
    
    getSubLayers: function() {
        return this.getRootLayer().getSubLayers();
    },
    
    getAllRequests: function() {
        var reqs;
        
        var standardReqs = WMSC.traverseWMSDom(this.dom, ['Capability', 'Request']);
        
        reqs = this._getRequestsFromNode(standardReqs);
        
        var extendedReqs = WMSC.traverseWMSDom(this.dom, ['Capability', '_ExtendedCapabilities', 'Request']);
        
        if (extendedReqs !== null) {
            reqs = reqs.concat(this._getRequestsFromNode(extendedReqs));
        }
        return reqs;
    },
    
    _getRequestsFromNode: function(node) {
        var reqs = [];
        for (var i=0; i<node.childNodes.length; i++) {
            var child = node.childNodes[i];
            if (child.nodeType != 1) {
                continue;
            }
            var name = child.nodeName;
            var formats = this._getRequestFormats(child);
            var req = new WMSC.Request(name, formats);
            reqs.push(req);
        }
        return reqs;
    },
    
    _getRequestFormats: function(node) {
        var i;
        
        var formats = [];
        for (i = 0; i < node.childNodes.length; i++) {
            var child = node.childNodes[i];
            if (child.nodeName.toUpperCase() == 'FORMAT') {
                formats.push(WMSC.getTextContent(child));
            }
        } 
        return formats;
    },
    
    getRequest: function(name) {
        var reqs = this.getAllRequests();
        for (var i=0;i<reqs.length;i++) {
            if (reqs[i].name == name) {
                return reqs[i];
            }
        }
        return null;
    },
    
    supportsRequest: function(name) {
        return this.getRequest(name) !== null;
    }
};

/**
 * Class to wrapper a WMC Layer document and expose
 * useful properties easily
 */
WMSC.Layer = function(node) {
    this.node = node;
};

WMSC.Layer.prototype = {
    getName: function() {
        var node = WMSC.traverseWMSDom(this.node, ['Name']);
        if (node === null) {
            return null;
        }
        return WMSC.getTextContent(node);
    },
    
    getTitle: function() {
        var el = WMSC.traverseWMSDom(this.node, ['Title']);
        return WMSC.getTextContent(el);
    },
    
    getAbstract: function() {
        var el = WMSC.traverseWMSDom(this.node, ['Abstract']);
        // NB, WMC layers may not have abstracts
        if (!el) {
            return "";
        }
            
        return WMSC.getTextContent(el);
    },
    
    getDimensions: function() {
        var i;
        var dimObj;
        var dims = {};
        var dimEls = this.node.getElementsByTagName('Dimension');
        for (i=0; i<dimEls.length; i++) 
        {
            dimObj = new WMSC.Dimension(dimEls[i]);
            dims[dimObj.getName()] = dimObj;
        }

        return dims;
    },

    getSubLayers: function() {
        var i, children, n;
        var layers = [];
    
        children = this.node.childNodes;
        for (i=0; i<children.length; i++) {
            n = children[i];
            if (n.nodeName == 'Layer') {
                layers[layers.length] = new WMSC.Layer(n);
            }
        }
        return layers;
    },
    
    // if layer is part of a web map context, it should have
    // an endpoint defined
    getEndpoint: function() {
        var or = WMSC.traverseWMSDom(this.node, ['Server', 'OnlineResource']);
        if (or === null) {
            return null;
        }
    
        var attr = or.getAttribute('href');
        if (!attr) {
            attr = or.getAttribute('xlink:href');
        }
        return attr;
    },
    
    getStyles: function() {
      var styles = [];
      
      for (var j=0 ; j < this.node.getElementsByTagName('Style').length; j++) {
          var styleElt = this.node.getElementsByTagName('Style')[j];
          
          var nameElt = WMSC.traverseWMSDom(styleElt, ['Name']); 
          var titleElt = WMSC.traverseWMSDom(styleElt, ['Title']);
          
          var nameStr = WMSC.getTextContent(nameElt);
          var titleStr = WMSC.getTextContent(titleElt);
          styles.push(new WMSC.Style(nameStr, titleStr));
      }
      
      return styles;
      
    },
        
    getLegendURL: function(style) {
        if (style === null || style === "") {
            style = undefined;
        }
        
        var styles = this.getStyles();
        
        //can't get the legend URL if there are no styles
        if (styles.length === 0) {
            return null;
        }
        
        //!TODO: check that the style is in the layers styles
        
        WMSC.log("style = " + style);
        
        //if no style specified just return the first
        if (style === undefined) {
            return this._getLegendURLForStyle(styles[0].name);
        }
        else {
            return this._getLegendURLForStyle(style);
        }
    },
    
    _getLegendURLForStyle: function(style) {
        var url = null;
                
        for (var j = 0; j < this.node.getElementsByTagName('Style').length; j++) {
             
            var styleElt = this.node.getElementsByTagName('Style')[j];
            var styleNameElt = WMSC.traverseWMSDom(styleElt, ['Name']);
            var styleName = WMSC.getTextContent(styleNameElt);
             
            if (styleName === style) {
                var onlineResElt = WMSC.traverseWMSDom(styleElt, ['LegendURL', 'OnlineResource']);

                url = this._getLinkFromORElement(onlineResElt);
                break;
            }
        }
         
        return url;
    },
    
    getDisplayOptionsURL: function() {
        var displayOpts = null;
        
        for (var i = 0; i < this.node.getElementsByTagName('MetadataURL').length; i++) {
            var metaURL = this.node.getElementsByTagName('MetadataURL')[i];

            if (metaURL !== undefined && metaURL.getAttribute('type') == 'display_options') {
                var olr = WMSC.traverseWMSDom(metaURL, ['OnlineResource']);
                
                displayOpts = this._getLinkFromORElement(olr);
            }
        }
        
        return displayOpts;
    },
    
    getAxisConfigURL: function() {
        var url = null;
        
        for (var i = 0; i < this.node.getElementsByTagName('MetadataURL').length; i++) {
            var metaURL = this.node.getElementsByTagName('MetadataURL')[i];

            if (metaURL !== undefined && metaURL.getAttribute('type') == 'axis_config') {
                var olr = WMSC.traverseWMSDom(metaURL, ['OnlineResource']); 
                url = this._getLinkFromORElement(olr);
            }
        }
        
        return url;
    },
    
    _getLinkFromORElement: function(onlineResElt) {
        var url = null;
        
        // for some reason in opera 10 this isn't working.
        //url = onlineResElt.getAttribute('xlink:href');
        
        for (var i = 0; i < onlineResElt.attributes.length; i++) {
            if (onlineResElt.attributes[i].name == 'xlink:href') {
                url = onlineResElt.attributes[i].value;
            }
        }
        
        return url;
    }
};


/**
 * Class to wrapper a WMC Layers dimension document and expose
 * useful properties easily
 */
WMSC.Dimension = function(node) {
    this.node = node;
};

WMSC.Dimension.prototype = {
        
    getName: function() {
        var attr = this.node.attributes.getNamedItem('name');
        return attr.value;
    },
    
    getUnits: function() {
        var attr = this.node.attributes.getNamedItem('units');
        return attr.value;
    },
    
    getExtent: function() {
        if (this.node.textContent) {
            return WMSC.trim(this.node.textContent).split(',');
        }
        else {
            return WMSC.trim(this.node.text).split(',');
        }
    }
};

WMSC.Style = function(name, title) {
    this.name = name;
    this.title = title;
};


WMSC.Request = function(name, formats) {
    this.name = name;
    this.formats = formats;
};

/**
 * Class to wrapper a WebMapContext document and expose
 * useful properties easily
 * @author C Byrom
 */
WMSC.WebMapContext = function(domElement) 
{
    this.dom = domElement;
};
WMSC.WebMapContext.prototype = 
{
    /**
     * Evaluate an XPATH expression on a specified dom node
     * @param expr: XPATH expression to use
     * @param node: node to evaluate expr on
     */
    evaluate: function(expr, node) 
    {
        if (node === null) { 
            node = this.dom;
        }

        return WMSC.evalXPath(expr, node);
    },

    /**
     * Retrieve the general title of the WMC doc
     * @return WMC Title string
     */
    getTitle: function() 
    {
        var el = WMSC.traverseWMSDom(this.dom, ['General', 'Title']);
        return WMSC.getTextContent(el);
    },
    
    /**
     * Retrieve the sublayers of the WMC doc
     * @return array of WMCS.Layer objects
     */
    getSubLayers: function()
    {
        var layerList = WMSC._searchElement(this.dom, 'LayerList');
         
        var children = layerList.childNodes;
        var layers = [];
        for (var i=0; i<children.length; i++) 
        {
            if (children[i].nodeName == 'Layer') {
                layers[layers.length] = new WMSC.Layer(children[i]);
            }
        }
        return layers;
    } 
};
