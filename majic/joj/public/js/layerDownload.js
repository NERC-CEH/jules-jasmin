"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, document: false */

var LayerDownload = function (containingDivId, initailBounds, makeFigureURL, eventsManager, controlMarkup) {
    
    this._containingDiv = document.getElementById(containingDivId);
    
    if (controlMarkup) {
        this.controlMarkup = controlMarkup;
    }

    this._containingDiv.innerHTML = this.controlMarkup;
    
    this.figBuilder = new FigureBuilder('composite_figure_container', makeFigureURL, initailBounds, eventsManager)
    this.wcsdown = new WCSDownloadControl('wcs_download_div', initailBounds, eventsManager);
    this.figDownload = new LayerFigureDownload('get_figure_container', eventsManager);
    
};


LayerDownload.prototype = {
    EVENTS_RAISED: [],
                
    controlMarkup: '\
    <label>Generate Composite Figure</label>\
        <div id="composite_figure_container"></div>\
    <label>Download Data from Selected Layer</label>\
        <div id="wcs_download_div"></div>\
    <div id="get_figure_container"></div>'

};

