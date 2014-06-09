/**
 * Manages the feature info control.
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
function ViewdataFeatureInfoManager(eventsManager) {
    this.eventsManager = eventsManager;
    this.featureInfoDivId = 'vd-feature-info';
    this.WINDOW_BORDER_HEIGHT = 30;
    this.WINDOW_BORDER_WIDTH = 12;
    this.WINDOW_SCROLL_HEIGHT = 15;
    this.WINDOW_SCROLL_WIDTH = 15;
    this.loaded = false;

    /**
     * Creates the feature info window.
     * @param parent - parent element for feature info window, within which its position is contrained.
     */
    this.createControls = function(parent) {
        this.parent = parent;
        this.featureInfoWindow = new Ext.Window({
            title: 'Feature Information',
            y: 0,
            renderTo: parent,
            constrain: true,
            autoScroll: true,
            collapsible: true,
            expandOnShow: true,
            hidden: true,
            minHeight: 50,
            minWidth: 100,
            border: false,
            shadow: false,
            closeAction: 'hide',
            html: '<div id="' + this.featureInfoDivId + '" class="vd-feature-info"></div>'
        });

        this.featureInfoDiv = document.getElementById(this.featureInfoDivId);

        this.eventsManager.register('SELECTED_LAYER_CHANGED', this, this.onCurrentLayerChanged);
        this.eventsManager.register("FEATURE_INFO", this, this.onFeatureInfoChanged);
    };

    /**
     * Handles a change of the selected layer.
     * Generates a SET_FEATURE_INFO_CONFIG event.
     * @param e - event data {id, layerData, olLayer}
     */
    this.onCurrentLayerChanged = function(e) {
        var dimValues = {};
        if (e.layerData !== null && e.olLayer !== null) {
            var layerData = e.layerData;

            var dims = layerData.dimensions;
            for (var dimIdx = 0; dimIdx < dims.length; ++dimIdx) {
                var dimData = dims[dimIdx];
                var dimName = dimData.name;
                var defaultValue = (dimData['default'] ? dimData['default'] : dimData.dimensionValues[0]);

                // Get the previously selected value, or the default.
                var dimValue = viewdataLayerData.getDimension(e.id, dimName);
                if (dimValue == null) {
                    dimValue = defaultValue;
                }
                dimValues[dimName] = dimValue;
            }
        }
        this.eventsManager.triggerEvent("SET_FEATURE_INFO_CONFIG",
                                        {olLayer: e.olLayer, layerData: e.layerData, dimensions: dimValues});
    };

    /**
     * Updates the contents of the feature info window.
     * @param e - feature info event
     */
    this.onFeatureInfoChanged = function(e) {
        // Preset a smallish size so that the window will expand from this if necessary.
        this.featureInfoWindow.setSize(300, 50);
        this.featureInfoWindow.doLayout();

        this.featureInfoDiv.innerHTML = e.info;

        // Delay resizing after the show call to allow the elements sizes to be set.
        this.featureInfoWindow.show();
        setTimeout(this.resizeWindow.bind(this), 50);
    };

    /**
     * Resizes the feature info window 
     */
    this.resizeWindow = function() {
        // Resize the window, trying to avoid scrolling of the info div within its parent element,
        // but ensuring that the window is not larger than it's parent.
        var parentEl = this.featureInfoDiv.parentNode;

        // Get the size of the window's parent.
        var windowParentWidth = this.parent.getWidth();
        var windowParentHeight = this.parent.getHeight();

        // Find out how much bigger the window is than the displayed area of the info div.
        var windowWidth = this.featureInfoWindow.getWidth();
        var windowHeight = this.featureInfoWindow.getHeight();

        var widthExtra = windowWidth - parentEl.clientWidth;
        var heightExtra = windowHeight - parentEl.clientHeight;

        // Resize to fit without scrolling.
        var width = parentEl.scrollWidth + widthExtra;
        var height = parentEl.scrollHeight + heightExtra;

        // Reduce size if necessary to make the window fit.
        var width = Math.min(width, windowParentWidth);
        var height = Math.min(height, windowParentHeight);

        this.featureInfoWindow.setSize(width, height);

        // Now check whether scroll bars were needed and if so, whether they could be avoided be resizing again.
        var resize = false;
        if ((parentEl.clientWidth < parentEl.offsetWidth) && (parentEl.clientWidth < parentEl.scrollWidth)) {
            width += parentEl.offsetWidth - parentEl.clientWidth;
            resize = true;
        }
        if ((parentEl.clientHeight < parentEl.offsetHeight) && (parentEl.clientHeight < parentEl.scrollHeight)) {
            height += parentEl.offsetHeight - parentEl.clientHeight;
            resize = true;
        }
        if (resize) {
            var width = Math.min(width, windowParentWidth);
            var height = Math.min(height, windowParentHeight);
            this.featureInfoWindow.setSize(width, height);
        }

        // Ensure that the window is positioned within its parent.
        var box = this.featureInfoWindow.getBox(true);

        var left = box.x;
        var top = box.y;

        if (left + box.width > windowParentWidth) {
            left = windowParentWidth - box.width;
        }
        if (left < 0) {
            left = 0;
        }

        if (top + box.height > windowParentHeight) {
            top = windowParentHeight - box.height;
        }
        if (top < 0) {
            top = 0;
        }

        this.featureInfoWindow.setPosition(left, top);
    };
}
