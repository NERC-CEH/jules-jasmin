/**
 * @requires OpenLayers/Control.js
 *
 * Class: OpenLayers.Control.LoadErrors
 * Checks for errors after loading layers. For layers that have failed, retries
 * checking for an unauthorized HTTP status, in which case a link to a login
 * form is displayed.
 *
 * Inherits from:
 *  - <OpenLayers.Control>
 */
OpenLayers.Control.LoadErrors = OpenLayers.Class(OpenLayers.Control, {

    /**
     * Property: counter
     * {Integer} A counter for the number of layers loading
     */ 
    counter: 0,

    /**
     * Property: loadErrorClassRe
     * {String} Regular expression for matching the CSS class set for map
     * images for which loading failed
     */ 
    loadErrorClassRe: new RegExp("(^|\\s)" + "olImageLoadError" + "(\\s|$)"),

    /**
     * Constructor: OpenLayers.Control.LoadErrors
     * Initialises the control.
     *
     * Parameters:
     * options - {Object} additional options.
     */
    initialize: function(options) {
         OpenLayers.Control.prototype.initialize.apply(this, [options]);
    },

    /**
     * Method: addLayer
     * Attach event handlers when new layer gets added to the map.
     *
     * Parameters:
     * evt - {Event}
     */
    addLayer: function(evt) {
        if (evt.layer) {
            WMSC.log("LoadErrors.addLayer: Added layer " + evt.layer.id);
            evt.layer.events.register('loadstart', this, this.increaseCounter);
            evt.layer.events.register('loadend', this, this.decreaseCounter);
        }
    },

    /**
     * Method: setMap
     * Set the map property for the control and all handlers.
     *
     * Parameters: 
     * map - {<OpenLayers.Map>} The control's map.
     */
    setMap: function(map) {
        OpenLayers.Control.prototype.setMap.apply(this, arguments);
        this.map.events.register('preaddlayer', this, this.addLayer);
        for (var i = 0; i < this.map.layers.length; i++) {
            var layer = this.map.layers[i];
            layer.events.register('loadstart', this, this.increaseCounter);
            layer.events.register('loadend', this, this.decreaseCounter);
        }
    },

    /**
     * Method: increaseCounter
     * Increase the counter.
     */
    increaseCounter: function(evt) {
        this.counter++;
        WMSC.log("LoadErrors.increaseCounter: Layer loading count incremented to " + this.counter + " (" + evt.object.id + ")");
    },
    
    /**
     * Method: decreaseCounter
     * Decrease the counter and perform the error check if loading is complete.
     */
    decreaseCounter: function(evt) {
        var doCheck = (this.counter == 1);
        if (this.counter > 0) {
            this.counter--;
        }
        WMSC.log("LoadErrors.decreaseCounter: Layer loading count decremented to " + this.counter + " (" + evt.object.id + ")");
        if (doCheck) {
            this.checkForLoadErrors();
        }
    },

    /** 
     * Method: destroy
     * Destroy the control.
     */
    destroy: function() {
        if (this.map) {
            this.map.events.unregister('preaddlayer', this, this.addLayer);
            if (this.map.layers) {
                for (var i = 0; i < this.map.layers.length; i++) {
                    var layer = this.map.layers[i];
                    layer.events.unregister('loadstart', this, 
                        this.increaseCounter);
                    layer.events.unregister('loadend', this, 
                        this.decreaseCounter);
                }
            }
        }
        OpenLayers.Control.prototype.destroy.apply(this, arguments);
    },     

    /** 
     * Method: checkForLoadErrors
     * Checks whether any layers have tile images with an error class set.
     */
    checkForLoadErrors: function() {
        if (this.map) {
            if (this.map.layers) {
                for (var i = 0; i < this.map.layers.length; i++) {
                    var layer = this.map.layers[i];
                    if (layer.div.getElementsByClassName) {
                        var errorImgs = layer.div.getElementsByClassName("olImageLoadError");
                        var error = (errorImgs.length > 0);
                        var method = "getElementsByClassName";
                    } else {
                        var imgs = layer.div.getElementsByTagName("img");
                        var errorImgs = new Array();
                        var error = false;
                        for (var j = 0; j < imgs.length; j++) {
                            if (this.loadErrorClassRe.test(imgs[j].className)) {
                                errorImgs.push(imgs[j]);
                                error = true;
                                break;
                            }
                        }
                        var method = "getElementsByTagName / RE";
                    }
                    if (error) {
                        this.getLoadStatus(errorImgs[0].src);
                    }
                }
            }
        }
    },     

    /** 
     * Method: getLoadStatus
     * Makes a request for a URL to determine the HTTP status.
     *
     * Parameters:
     * url - {String} URL for which to check the load HTTP status
     */
    getLoadStatus: function(url) {
        WMSC.log("LoadErrors.getLoadStatus: Getting load status for " + url);
        var req = new Ajax.Request(url,
                                   {
                                       method: "get",
                                       onSuccess: this.getLoadStatusHandler.bind(this),
                                       onFailure: this.getLoadStatusHandler.bind(this),
                                       onException: this.getLoadStatusHandler.bind(this)
                                   }
                                  );
    },

    /** 
     * Method: getLoadStatusHandler
     * Checks the HTTP request status and displays a dialog box if the status is
     * "unauthorized"/401.
     *
     * Parameters:
     * resp - {XMLHttpRequest} HTTP response
     */
    getLoadStatusHandler: function(resp) {
        WMSC.log("LoadErrors.getLoadStatusHandler: Load status is " + resp.status);
        if (resp.status === 401) {
            this.loginDialog.showUnauthorisedDialog(this.redrawMap.bind(this));
        }
    },

    /** 
     * Method: redrawMap
     * Raises an event to cause the map to be redrawn.
     */
    redrawMap: function() {
        WMSC.log("redrawMap called");
        this.eventsManager.triggerEvent("REDRAW_LAYERS");
    },

    CLASS_NAME: "OpenLayers.Control.LoadErrors"

});
