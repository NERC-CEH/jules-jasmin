/*jslint onevar: false*/

/*globals WMSC: false, OpenLayers: false, document: false, AjaxRetriever: false, Utils: false*/

/**
 * @requires YAHOO.util.Dom
 * @requires YAHOO.util.Dom
 * @requires YAHOO.widget.Layout
 */

/*globals WMSC: false, document:false, YAHOO:false*/

/**
 *
 * 
 * @constructor
 */
var LayoutManager = function () {
    
};

LayoutManager.prototype = {
        
    EVENTS_RAISED: [],

    setupLayout: function() {

        var Dom = YAHOO.util.Dom;
        var Event = YAHOO.util.Event;

        this.layout = new YAHOO.widget.Layout({
            units: [
                { position: 'bottom', header: '', height: 200, resize: true, body: 'bottom1', gutter: '5px', collapse: true },
                //{ position: 'right', header: 'Layer List', width: 150, resize: true, gutter: '5px', collapse: true, scroll: true, body: 'right1', animate: true },
                //{ position: 'left', header: 'Layer List', width: 180, resize: true, gutter: '5px', collapse: true, scroll: true, body: 'right1', animate: true },
                { position: 'center', body: 'center1' }
            ]
        });

        Event.onDOMReady(this._onDomReady.bindAsEventListener(this));

        this.layout.on('resize', function(ev) {

                var center_content = Dom.get('center_content');
                Dom.setStyle(center_content, 'height',   ev.sizes.center.h + 'px');

                var targetMapHeight;
                var targetMapWidth;

                var maxMapHeight = ev.sizes.center.h -2;
                var maxMapWidth = ev.sizes.center.w -4;

                var ratio = ev.sizes.center.w / ev.sizes.center.h;

                var twiceHeight = maxMapHeight * 2;
                var twiceWidth = maxMapWidth * 2;

                // if the width is greater than half the height then height
                // will be the limiting factor
                if (ratio > 2.0) {
                    targetMapHeight = maxMapHeight;
                    targetMapWidth = twiceHeight;
                }
                else if (ratio  == 2.0) {
                    targetMapHeight = maxMapHeight;
                    targetMapWidth = Math.floor(maxMapHeight/2);
                }
                // otherwise the width will be the limiting factor
                else {
                    targetMapWidth = maxMapWidth;
                    targetMapHeight = Math.floor(maxMapWidth/2);
                }

                Dom.setStyle('map', 'width',   targetMapWidth + 'px');
                Dom.setStyle('map', 'height',  targetMapHeight + 'px');

                Dom.setStyle(('tab_content'),   'height',   ev.sizes.bottom.h - 86 + 'px');
                Dom.setStyle(('bottom_left'),   'height',   ev.sizes.bottom.h - 40 + 'px');
                Dom.setStyle(('bottom_middle'), 'height',   ev.sizes.bottom.h - 40 + 'px');
                Dom.setStyle(('bottom_right'),  'height',   ev.sizes.bottom.h - 40 + 'px');

        });

    },
    
    refreshTabWidths: function () {

        var size = this._getWidth('bottom1') - 6;

        var rightWidth = this._getWidth('bottom_right');
        var midWidth = this._getWidth('bottom_middle');
        var leftWidth = this._getWidth('bottom_left');
        var total = rightWidth + midWidth + leftWidth;
        
        var targetRightWidth = Math.floor(rightWidth/total * size );
        var targetMidWidth = Math.floor(midWidth/total * size );
        var targetLeftWidth = Math.floor(leftWidth/total * size );

        if (targetRightWidth < 100) { targetRightWidth = 100; }
        if (targetMidWidth < 100) { targetMidWidth = 100; }
        if (targetLeftWidth < 100) { targetLeftWidth = 100; }

        this._setWidth('bottom_left', targetLeftWidth);
        this._setWidth('bottom_middle', targetMidWidth);
        this._setWidth('bottom_right', targetRightWidth);        

    },
    
    
    _onDomReady: function () {
    
        this.layout.render();

        var size = this._getWidth('bottom1') - 6;

        var resizeLeft = new YAHOO.util.Resize('bottom_left', {

            handles: ['r'],
            minWidth: 100,
            maxWidth: size - 200
        });

        resizeLeft.on('resize', this._onLeftResize.bindAsEventListener(this));

        var resizeMid = new YAHOO.util.Resize('bottom_middle', {
            handles: ['r'],
            minWidth: 100,
            maxWidth: size - 200
        });

        resizeMid.on('resize', this._onMiddleResize.bindAsEventListener(this));

                
    },
    
    _onLeftResize: function(ev) {
        var w = ev.width;
        var size = this._getWidth('bottom1') - 6;

        var rightWidth = this._getWidth('bottom_right');
        var midWidth = this._getWidth('bottom_middle');

        var resizeRight = true;
        var targetMidWidth = null;
        var targetRightWidth = null;

        if (midWidth > 100) {
            targetMidWidth = size - w - rightWidth;
            if (targetMidWidth > 100) {
                resizeRight = false;
            }
            else {
                targetMidWidth = 100;
            }
        }
        else {
            targetMidWidth = 100;
        }

        if (resizeRight) {
            targetRightWidth = size - w - targetMidWidth;
            if (targetRightWidth < 100) {
                targetRightWidth = 100;
                w = size - targetMidWidth - targetRightWidth;
            }
        }

        this._setWidth('bottom_left', w);
        this._setWidth('bottom_middle', targetMidWidth);
        this._setWidth('bottom_right', targetRightWidth);
    },
    
    _onMiddleResize: function(ev) {
        var w = ev.width;
        var size = this._getWidth('bottom1') - 6;

        var rightWidth = this._getWidth('bottom_right');
        var leftWidth = this._getWidth('bottom_left');

        targetRightWidth = size - w - leftWidth;

        if (targetRightWidth < 100) {
            targetRightWidth = 100;
            w = size - targetRightWidth - leftWidth;
        }

        this._setWidth('bottom_middle', w);
        this._setWidth('bottom_right', targetRightWidth);        
    },
    
    _getWidth: function (elt) {
        var reg = YAHOO.util.Dom.getRegion(elt);
        var w = reg.right - reg.left;
        return w;
    },
    
    _setWidth: function (elt, w) {
        YAHOO.util.Dom.setStyle(elt, 'width', (w) + 'px');
    }
    
};
