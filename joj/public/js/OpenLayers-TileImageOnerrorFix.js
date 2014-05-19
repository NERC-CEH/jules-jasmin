/** 
 * Patch for onerror callback in OpenLayers.Tile.Image.initImgDiv for OpenLayers 2.10 and 2.11.
 * The unpatched version assumes (as stated in a comment) that OpenLayers.Util.onImageLoadError will
 * be called before onerror defined in OpenLayers.Tile.Image.initImgDiv - this is not true on (at
 * least) Internet Explorer 8. In this case, imgDiv._attempts is not defined and a load error is not
 * detected nor is onload ever called.
 * In OpenLayers 2.12 OpenLayers.Tile.Image has been substantially rewritten and does not suffer
 * from this problem, but, at least as of 2.12-rc3, other problems with rendering on IE8 prevent
 * upgrading to this version.
 */
if (OpenLayers.VERSION_NUMBER === "OpenLayers 2.10 -- $Revision: 10721 $") {
    WMSC.log("Fixing OpenLayers.Tile.Image.initImgDiv onerror for OpenLayers 2.10");
    /**
     * Method: initImgDiv
     * Creates the imgDiv property on the tile.
     */
    OpenLayers.Tile.Image.prototype.initImgDiv = function() {
        
        var offset = this.layer.imageOffset; 
        var size = this.layer.getImageSize(this.bounds); 
     
        if (this.layerAlphaHack) {
            this.imgDiv = OpenLayers.Util.createAlphaImageDiv(null,
                                                           offset,
                                                           size,
                                                           null,
                                                           "relative",
                                                           null,
                                                           null,
                                                           null,
                                                           true);
        } else {
            this.imgDiv = OpenLayers.Util.createImage(null,
                                                      offset,
                                                      size,
                                                      null,
                                                      "relative",
                                                      null,
                                                      null,
                                                      true);
        }
        
        this.imgDiv.className = 'olTileImage';

        /* checkImgURL used to be used to called as a work around, but it
           ended up hiding problems instead of solving them and broke things
           like relative URLs. See discussion on the dev list:
           http://openlayers.org/pipermail/dev/2007-January/000205.html

        OpenLayers.Event.observe( this.imgDiv, "load",
            OpenLayers.Function.bind(this.checkImgURL, this) );
        */
        this.frame.style.zIndex = this.isBackBuffer ? 0 : 1;
        this.frame.appendChild(this.imgDiv); 
        this.layer.div.appendChild(this.frame); 

        if(this.layer.opacity != null) {
            
            OpenLayers.Util.modifyDOMElement(this.imgDiv, null, null, null,
                                             null, null, null, 
                                             this.layer.opacity);
        }

        // we need this reference to check back the viewRequestID
        this.imgDiv.map = this.layer.map;

        //bind a listener to the onload of the image div so that we 
        // can register when a tile has finished loading.
        var onload = function() {
            
            //normally isLoading should always be true here but there are some 
            // right funky conditions where loading and then reloading a tile
            // with the same url *really*fast*. this check prevents sending 
            // a 'loadend' if the msg has already been sent
            //
            if (this.isLoading) { 
                this.isLoading = false; 
                this.events.triggerEvent("loadend"); 
            }
        };
        
        if (this.layerAlphaHack) { 
            OpenLayers.Event.observe(this.imgDiv.childNodes[0], 'load', 
                                     OpenLayers.Function.bind(onload, this));    
        } else { 
            OpenLayers.Event.observe(this.imgDiv, 'load', 
                                 OpenLayers.Function.bind(onload, this)); 
        } 
        

        // Bind a listener to the onerror of the image div so that we
        // can registere when a tile has finished loading with errors.
        var onerror = function() {

            // If we have gone through all image reload attempts, it is time
            // to realize that we are done with this image. Since
            // OpenLayers.Util.onImageLoadError already has taken care about
            // the error, we can continue as if the image was loaded
            // successfully.
            this.imgDiv._attempts = (this.imgDiv._attempts) ? (this.imgDiv._attempts + 1) : 1;
            if (this.imgDiv._attempts > OpenLayers.IMAGE_RELOAD_ATTEMPTS) {
                onload.call(this);
            }
        };
        OpenLayers.Event.observe(this.imgDiv, "error",
                                 OpenLayers.Function.bind(onerror, this));
    };
}
else if (OpenLayers.VERSION_NUMBER === "Release 2.11") {
    WMSC.log("Fixing OpenLayers.Tile.Image.initImgDiv onerror for OpenLayers 2.11");
    /**
     * Method: initImgDiv
     * Creates the imgDiv property on the tile.
     */
    OpenLayers.Tile.Image.prototype.initImgDiv = function() {
        if (this.imgDiv == null) {
            var offset = this.layer.imageOffset; 
            var size = this.layer.getImageSize(this.bounds); 

            if (this.layerAlphaHack) {
                this.imgDiv = OpenLayers.Util.createAlphaImageDiv(null,
                                                               offset,
                                                               size,
                                                               null,
                                                               "relative",
                                                               null,
                                                               null,
                                                               null,
                                                               true);
            } else {
                this.imgDiv = OpenLayers.Util.createImage(null,
                                                          offset,
                                                          size,
                                                          null,
                                                          "relative",
                                                          null,
                                                          null,
                                                          true);
            }

            // needed for changing to a different server for onload error
            if (OpenLayers.Util.isArray(this.layer.url)) {
                this.imgDiv.urls = this.layer.url.slice();
            }
      
            this.imgDiv.className = 'olTileImage';

            /* checkImgURL used to be used to called as a work around, but it
               ended up hiding problems instead of solving them and broke things
               like relative URLs. See discussion on the dev list:
               http://openlayers.org/pipermail/dev/2007-January/000205.html

            OpenLayers.Event.observe( this.imgDiv, "load",
                OpenLayers.Function.bind(this.checkImgURL, this) );
            */
            this.frame.style.zIndex = this.isBackBuffer ? 0 : 1;
            this.frame.appendChild(this.imgDiv); 
            this.layer.div.appendChild(this.frame); 

            if(this.layer.opacity != null) {

                OpenLayers.Util.modifyDOMElement(this.imgDiv, null, null, null,
                                                 null, null, null, 
                                                 this.layer.opacity);
            }

            // we need this reference to check back the viewRequestID
            this.imgDiv.map = this.layer.map;

            //bind a listener to the onload of the image div so that we 
            // can register when a tile has finished loading.
            var onload = function() {

                //normally isLoading should always be true here but there are some 
                // right funky conditions where loading and then reloading a tile
                // with the same url *really*fast*. this check prevents sending 
                // a 'loadend' if the msg has already been sent
                //
                if (this.isLoading) { 
                    this.isLoading = false; 
                    this.events.triggerEvent("loadend"); 
                }
            };

            if (this.layerAlphaHack) { 
                OpenLayers.Event.observe(this.imgDiv.childNodes[0], 'load', 
                                         OpenLayers.Function.bind(onload, this));    
            } else { 
                OpenLayers.Event.observe(this.imgDiv, 'load', 
                                     OpenLayers.Function.bind(onload, this)); 
            } 


            // Bind a listener to the onerror of the image div so that we
            // can registere when a tile has finished loading with errors.
            var onerror = function() {

                // If we have gone through all image reload attempts, it is time
                // to realize that we are done with this image. Since
                // OpenLayers.Util.onImageLoadError already has taken care about
                // the error, we can continue as if the image was loaded
                // successfully.
                this.imgDiv._attempts = (this.imgDiv._attempts) ? (this.imgDiv._attempts + 1) : 1;
                if (this.imgDiv._attempts > OpenLayers.IMAGE_RELOAD_ATTEMPTS) {
                    onload.call(this);
                }
            };
            OpenLayers.Event.observe(this.imgDiv, "error",
                                     OpenLayers.Function.bind(onerror, this));
        }
        
        this.imgDiv.viewRequestID = this.layer.map.viewRequestID;
    };
}
