/**
 * Manages the legend control.
 * @class
 *
 * @requires OpenLayers/Events.js
 *
 * @author R. Wilkinson
 * Partly based on legendContainer.js.
 */

/**
 * Constructor to initialise legend controls.
 * @constructor
 *
 * @param eventsManager - event manager
*/
function ViewdataLegendManager(eventsManager) {
    this.eventsManager = eventsManager;
    this.legendDivId = 'vd-legend';
    this.layerValid = false;
    this.doResize = true;
    this.WINDOW_BORDER_HEIGHT = 30;
    this.WINDOW_BORDER_WIDTH = 12;

    /**
     * Creates the legend window.
     * @param parent - parent element for legend window, within which its position is contrained.
     */
    this.createControls = function(parent) {
        this.parent = parent;
        this.legendWindow = new Ext.Window({
//            title: 'Legend',
//            x: -3000,
            y: 3000,
            renderTo: parent,
            constrain: true,
//            autoHeight: true,
//            autoWidth: true,
            collapsible: true,
            expandOnShow: true,
            hidden: true,
            boxMinHeight: 100,
            boxMinWidth: 100,
            border: false,
            shadow: false,
            closeAction: 'hide',
            listeners: {
                'bodyresize': this.onBodyResize,
                'scope': this
            }
        });

        this.legendDiv = this.legendWindow.body.dom;
        this.imageScale = 1.0;
        this._retriever = new AjaxRetriever();

        this.eventsManager.register("LAYER_PROPERTY_CHANGED", this, this.onLayerPropertyChanged);
        this.eventsManager.register("LEGEND_LAYER_CHANGED", this, this.onLayerChanged);
        this.eventsManager.register("LEGEND_LAYER_INVALID", this, this.onLayerInvalid);
    };

    /**
     * Handles the LEGEND_LAYER_CHANGED event, replaces the legend
     * with one correponding to the new layer (if the new layer isn't null).
     * @param e - event data {olLayer, layerData}
     */
    this.onLayerChanged = function(e) {
        this.layerValid = true;
        this.setLegendForLayer(e.olLayer, e.layerData);
    };

    /**
     * Handles the LEGEND_LAYER_INVALID event - flags the current layer as no
     * longer to be updated on property changes.
     */
    this.onLayerInvalid = function() {
        this.layerValid = false;
    };

    /**
     * Handles the LAYER_PROPERTY_CHANGED event. A property on the layer has
     * changed, need to re-draw the legend.
     * @param e - event data {olLayer, layerData}
     */
    this.onLayerPropertyChanged = function(e) {
        if (this.layerValid) {
            this.setLegendForLayer(e.layer, e.layerData);
        }
    };

    /**
     * Sets a legend appropriate to the layer and the selected style.
     * @param olLayer - OpenLayers layer
     * @param layerData - layer data retrieved from the WMS capabilities document
     */
    this.setLegendForLayer = function(olLayer, layerData) {

        var legendLoaded = false;

        if (layerData !== null && olLayer !== null) {

            var style = olLayer.params.STYLES;

            var url = this._getLegendURL(layerData, style);

            WMSC.log("Legend url = " + url);

            if (url !== null) {

                // add the current openlayers layer parameters
                // to the GetLegend url
                url = Utils.addParamsToUrl(url, olLayer.params);

                this.loadNewLegend(url);
                this.legendWindow.setTitle(layerData.title);

                legendLoaded = true;
            }
        }

        if (legendLoaded === false) {
            this.clearLegend();
            this.legendWindow.hide();
        }
    };

    /**
     * Finds the legend URL for the specified layer and style, determining if a style is set.
     * @param layerData - layer data retrieved from the WMS capabilities document
     * @param style - style name
     */
    this._getLegendURL = function(layerData, style) {
        if (style === null || style === "") {
            style = undefined;
        }

        var styles = layerData.styles;

        // Can't get the legend URL if there are no styles.
        if (styles.length === 0) {
            return null;
        }

        WMSC.log("style = " + style);

        // If no style specified just return the first.
        if (style === undefined) {
            return this._getLegendURLForStyle(layerData, styles[0].name);
        }
        else {
            return this._getLegendURLForStyle(layerData, style);
        }
    };

    /**
     * Constructs the legend URL for the specified layer and style.
     * @param layerData - layer data retrieved from the WMS capabilities document
     * @param style - style name
     */
    this._getLegendURLForStyle = function(layerData, style) {
        var url = null;

        for (var j = 0; j < layerData.styles.length; j++) {
            var layerStyle = layerData.styles[j];
            if (layerStyle.name === style) {
                if (layerStyle.legendURL && layerStyle.legendURL.onlineResource) {
                    url = layerStyle.legendURL.onlineResource;
                } else {
                    url = null;
                }
                break;
            }
        }

        return url;
    };

    /**
     * Loads a new legend from the given url, this uses the legendRetriver
     * to get the new legend html using AJAX and then calls the .setLegend
     * function.
     * @param url - legend URL
     */
    this.loadNewLegend = function(url) {

        WMSC.log("getting legend url = " + url);

        var onSuccessFn = this.setLegend.bind(this);

        var params = {REQUEST: 'GetLegendUrl', ENDPOINT: url};

        this._retriever.getResponse(params, onSuccessFn);
    };

    /**
     * Takes the XHR response text and places it inside the legend div.
     * The response text should be a valid <img> element.
     * @param xhr - XHR response
     */
    this.setLegend = function(xhr) {
        WMSC.log("setting legend at" + new Date());
        this.legendDiv.innerHTML = '<img style="display: block; margin-left: auto; margin-right: auto; text-align: center;">';
        var url = xhr.responseText;

        // Set an event listener for when the legend has loaded so that its position can be reset if
        // necessary depending on its size.
        var el = this.legendDiv.firstChild;
        if (el.addEventListener) {
            el.addEventListener('load', this.onLoad.bind(this), false);
        } else if (el.attachEvent) {
            el.attachEvent('onload', this.onLoad.bind(this));
        } else {
            // Fall back to a timer.
            WMSC.log("setting timer for legend image");
            setTimeout(this.onLoad.bind(this), 500);
        }
        el.setAttribute("src", url);
    };

    /**
     * Clears the content from the legendDiv.
     */
    this.clearLegend = function(xhr) {
        this.legendDiv.innerHTML = '';
    };

    /**
     * Event handler for when the legend image has loaded within the legend window.
     * Checks that the legend window is positioned within its parent.
     */
    this.onLoad = function() {
        var el = this.legendDiv.firstChild;
        if (el) {
            // Resize the legend image if a scale factor is in force.
            this.imageOriginalWidth = el.clientWidth;
            this.imageOriginalHeight = el.clientHeight;
            WMSC.log("Image size: " + this.imageOriginalWidth + " x " + this.imageOriginalHeight);
            if (this.legendWindow.hidden) {
                this.imageScale = 1.0;
            }
            WMSC.log("imageScale: " + this.imageScale);
            var newWidth = el.clientWidth * this.imageScale;
            var newHeight = el.clientHeight * this.imageScale;
            el.width = newWidth;
            el.height = newHeight;
            WMSC.log("New size: " + newWidth + " x " + newHeight);

            // Find the width of the header contents.
            var headerInnerWidth = 10;
            var headerChildren = this.legendWindow.header.dom.children
            for (var i = 0; i < headerChildren.length; ++i) {
                headerInnerWidth += headerChildren[i].offsetWidth;
            }
            WMSC.log("headerInnerWidth: " + headerInnerWidth);

            // Resize the window to fit the header and image.
            var windowWidth = Math.max(newWidth, headerInnerWidth) + this.legendWindow.getFrameWidth();
            this.doResize = false;
            this.legendWindow.setSize(windowWidth, newHeight + this.legendWindow.getFrameHeight());
            this.doResize = true;

            // Allow the window to position itself the first time, otherwise ensure that it is placed within its parent.
            if (!this.legendWindow.hidden) {
                this.ensurePositionedWithinParent();
            }

            this.legendWindow.show();
        }
    };

    /**
     * Repositions the window within its parent if it is currently not wholly within it.
     */
    this.ensurePositionedWithinParent = function() {
        var box = this.legendWindow.getBox(true);
        var parentWidth = this.parent.getSize().width;
        var parentHeight = this.parent.getSize().height;

        var left = box.x;
        var top = box.y;

        if (left + box.width > parentWidth) {
            left = parentWidth - box.width;
        }
        if (left < 0) {
            left = 0;
        }

        if (top + box.height > parentHeight) {
            top = parentHeight - box.height;
        }
        if (top < 0) {
            top = 0;
        }

        this.legendWindow.setPosition(left, top);
    };

    /**
     * Event handler for when the legend window is resized.
     * Resizes the legend image to fit within the window.
     */
    this.onBodyResize = function(c, w, h) {
        if (!this.doResize || typeof(w) != 'number' || typeof(h) != 'number') {
            return;
        }
        var imgEl = this.legendDiv.firstChild;
        if (imgEl) {
            var origWidth = this.imageOriginalWidth;
            var origHeight = this.imageOriginalHeight;
            if ((origWidth / origHeight) >= (w / h)) {
                // Constrained by width
                var newWidth = w;
                var newHeight = w * origHeight / origWidth;
            } else {
                // Constrained by height
                var newHeight = h;
                var newWidth = h * origWidth / origHeight;
            }

            imgEl.width = newWidth;
            imgEl.height = newHeight;
            this.imageScale = newWidth / origWidth;
            WMSC.log("imageScale: " + this.imageScale);
        }
    };
}
