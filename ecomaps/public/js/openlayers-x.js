/** Extensions to OpenLayers to fine-tune the user interface
    
    @author Stephen Pascoe
*/

/*global OpenLayers:false */

/**
 * Extension of zoom box control that includes a sub-selection box.
 */
var SubSelectionZoomBox = OpenLayers.Class(OpenLayers.Control.ZoomBox, {
    /**
     * Overrides ZoomBox.zoomBox - sets the sub-selection box in addition to the performing parent
     * class action.
     */
    zoomBox: function (position) {
        WMSC.log("zoomBox " + position)
        if (position instanceof OpenLayers.Bounds) {
            var limits = position.toArray();
            var lb = this.map.getLonLatFromViewPortPx(new OpenLayers. Pixel(limits[0], limits[1]));
            var rt = this.map.getLonLatFromViewPortPx(new OpenLayers. Pixel(limits[2], limits[3]));
            this.activateSubsel(new OpenLayers.Bounds(lb.lon, lb.lat, rt.lon, rt.lat));
        }
        OpenLayers.Control.ZoomBox.prototype.zoomBox.apply(this, arguments);
    },

    setSubSel: function (bounds) {
        this.activateSubsel(bounds);
        this.map.zoomToExtent(bounds);
    },

    activateSubsel: function (bounds) {
        this.subselBox.bounds = bounds;
        this.subselBox.display(true);
        this.isSubselActive = true;
        /* Force a redraw */
        this.boxesLayer.moveTo(null, true);
    },

    deactivateSubsel: function () {
        this.subselBox.display(false);
        this.isSubselActive = false;
    },

    /** Get either the subselection or the complete viewport bounds  */
    getActiveBounds: function () {
        if (this.isSubselActive) {
            return this.subselBox.bounds;
        }
        else {
            var b = this.map.getExtent();
            if (b.left < -180) {
                b.left = -180;
            }
            if (b.right > 180) {
                b.right = 180;
            }
            if (b.top > 90) {
                b.top = 90;
            }
            if (b.bottom < -90) {
                b.bottom = -90
            }
            return b;
        }
    },

    /** Initialises the sub-selection box. */
    initSubsel: function () {
        var subsel = new OpenLayers.Bounds(-180,-90, 180, 90);
        this.subselBox = new OpenLayers.Marker.Box(subsel);
        this.subselBox.div.style.borderStyle = 'dashed';
        this.subselBox.display(false);
        this.boxesLayer.addMarker(this.subselBox);
        this.isSubselActive = false;
    },

    /** Check the subselection is within bounds and deactivate if not. */
    checkSubselVisibility: function () {
        if (!this.isSubselActive) { return; }
        var bounds = this.map.getExtent();
        var sbounds = this.subselBox.bounds;
        WMSC.log("Bounds " + bounds);
        WMSC.log("Sub-selection bounds " + sbounds);
        if ((bounds.left > sbounds.left) ||
            (bounds.right < sbounds.right) ||
            (bounds.bottom > sbounds.bottom) ||
            (bounds.top < sbounds.top)) {
            this.deactivateSubsel();
            WMSC.log("Deactivating sub-selection");
        }
    }
});

/**
 * Extension of NavToolbar that includes SubSelectionZoomBox, Navigation and
 * optionally WMSGetFeatureInfo tools.
 */
var SubSelectionMouseToolbar = OpenLayers.Class(OpenLayers.Control.NavToolbar, {
    MODE_FEATUREINFO: "featureinfo",
    MODE_PAN: "pan",
    MODE_ZOOMBOX: "zoombox",

    TOOLTIP_FEATUREINFO: "Click on a position on the map to retrieve feature information if available.",
    TOOLTIP_PAN: "Drag with the mouse to pan the map: shift drag to zoom to a region.",
    TOOLTIP_ZOOMBOX: "Drag with the mouse to set a selection region.",

    /**
     * Initialises the toolbar and the associated tools.
     * @param boxesLayer  Layer used that displays the selection box
     * @param options  options passed to the toolbar OpenLayers.Control.Panel; additionally the
     *     boolean option featureInfoTool controls whether the GetFeatureInfo tool is set up.
     */
    initialize: function(boxesLayer, options) {
        OpenLayers.Control.Panel.prototype.initialize.apply(this, [options]);
        this.zoomBox = new SubSelectionZoomBox({title: this.TOOLTIP_ZOOMBOX});
        this.navigationTool = new OpenLayers.Control.Navigation({title: this.TOOLTIP_PAN});
        this.featureInfo = null;

        var controls = [this.zoomBox, this.navigationTool];
        
        if (options['featureInfoTool']) {
            // GetFeatureInfo requests are proxied through the ecomaps server to avoid cross-site
            // AJAX request blocking by the browser.
            OpenLayers.ProxyHost = '?REQUEST=proxy&URL='
            this.featureInfo = new OpenLayers.Control.WMSGetFeatureInfo({
                type: OpenLayers.Control.TYPE_TOOL,
                infoFormat: 'text/html', // Only handle HTML response
                title: this.TOOLTIP_FEATUREINFO
            });
            controls.push(this.featureInfo);
        }

        this.addControls(controls);

        // Add the sub-selection box to the boxes layer.
        this.zoomBox.boxesLayer = boxesLayer;
        this.zoomBox.initSubsel();
    },

    /**
     * Sets a handler for the results of GetFeatureInfo requests.
     * @param scope  scope in which to call handler
     * @param handler  handler to call
     */
    setFeatureInfoHandler: function (scope, handler) {
        if (this.featureInfo) {
            this.featureInfo.events.register("getfeatureinfo", scope, handler);
        }
    },

    /**
     * Sets the layer to which GetFeatureInfo requests apply.
     * @param layer  Layer for which requests should be made
     * @param getMapUrl  URL for the layer's GetMap requests
     * @param getFeatureInfoUrl  URL for the layer's GetFeatureInfo requests
     */
    setQueryLayer: function (layer, getMapUrl, getFeatureInfoUrl) {
        if (this.featureInfo) {
            this.featureInfo.layers = [layer];
            this.featureInfo.layerUrls = [getMapUrl];
            this.featureInfo.url = getFeatureInfoUrl;

            this.featureInfo.vendorParams = {};
            WMSC.log("setQueryLayer: " + getMapUrl);
        }
    },

    /**
     * Sets the value of a dimension to be included in the parameters for a GetFeatureInfo request.
     * @param name  name of dimension
     * @param value  value of dimension
     */
    setQueryDimension: function (name, value) {
        if (this.featureInfo) {
            this.featureInfo.vendorParams[name] = value;
            WMSC.log("setQueryDimension: " + name + "=" + value);
        }
    },

    /**
     * Method: draw 
     * calls the default draw, and then activates mouse defaults.
     */
    draw: function() {
        var div = OpenLayers.Control.Panel.prototype.draw.apply(this, arguments);
        this.activateControl(this.navigationTool);
        this.mode = this.MODE_PAN;
        return div;
    },

    /**
     * Method: switchModeTo 
     * Switches the toolbar to a named mode.
     * @param mode  mode to which to switch {String} 
     */
    switchModeTo: function (mode) {
        if (mode != this.mode) {
            switch(mode) {
            case this.MODE_FEATUREINFO:
                if (this.featureInfo) {
                    this.activateControl(this.featureInfo);
                    this.mode = this.MODE_FEATUREINFO;
                }
                break;
            case this.MODE_ZOOMBOX:
                this.activateControl(this.zoomBox);
                this.mode = this.MODE_ZOOMBOX;
                break;
            default:
                this.activateControl(this.navigationTool);
                this.mode = this.MODE_PAN;
                break;
            }
        }
    },


    // Methods below call the corresponding methods on the toolbar's SubSelectionZoomBox.

    setSubSel: function (bounds) {
        this.zoomBox.setSubSel(bounds);
    },

    activateSubsel: function (bounds) {
        this.zoomBox.activateSubsel(bounds);
    },

    deactivateSubsel: function () {
        this.zoomBox.deactivateSubsel();
    },

    getActiveBounds: function () {
        return this.zoomBox.getActiveBounds();
    },

    checkSubselVisibility: function () {
        this.zoomBox.checkSubselVisibility();
    }
});

var DDCVisMap = OpenLayers.Class(OpenLayers.Map, {
    setCenter: function(center, zoom, dragging) {
                
        if (center == null) {
            center = this.getCenter();
        }                
        if (zoom == null) {
            zoom = this.getZoom();
        }
                
        var resolution = this.baseLayer.resolutions[zoom];
        var size = this.getSize();
        var w_deg = size.w * resolution;
        var h_deg = size.h * resolution;
                    
        var bounds = new OpenLayers.Bounds(center.lon - w_deg / 2,
                                           center.lat - h_deg / 2,
                                           center.lon + w_deg / 2,
                                           center.lat + h_deg / 2);
                
        if (w_deg < 360.0) {
            if (bounds.left < -180.0) {
                center.lon = w_deg / 2 - 180.0;
            }
            else if (bounds.right > 180.0) {
                center.lon = 180.0 - w_deg / 2;
            }
        } else {
            if (bounds.left > -180.0) {
                center.lon = w_deg / 2 - 180.0;
            }
            else if (bounds.right < 180.0) {
                center.lon = 180.0 - w_deg / 2;
            }
        }

        if (h_deg < 180.0) {
            if (bounds.bottom < -90.0) {
                    center.lat = center.lat + (-90.0 - bounds.bottom);
            }
            else if (bounds.top > 90.0) {
                center.lat = center.lat - (bounds.top - 90.0);
            }
        } else {
            if (bounds.bottom > -90.0) {
                    center.lat = center.lat + (-90.0 - bounds.bottom);
            }
            else if (bounds.top < 90.0) {
                center.lat = center.lat - (bounds.top - 90.0);
            }
        }

        OpenLayers.Map.prototype.setCenter.apply(this, [center, zoom, dragging]);
    }

});
