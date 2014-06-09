/**
 * Manages login dialog.
 *
 * @author R. Wilkinson
 */

/**
 * Window containing an IFrame.
 */
Ext.IframeWindow = Ext.extend(Ext.Window, {
    onRender: function() {
        this.bodyCfg = {
            id: this.iframeId,
            tag: 'iframe',
            src: this.src,
            cls: this.bodyCls,
            style: {
                border: '0px none'
            }
        };
        Ext.IframeWindow.superclass.onRender.apply(this, arguments);
    }
});

/**
 * Constructor to login dialog.
 * @constructor
 *
 * @param loginUrl - URL to set for login dialog
 * @param loggedInUrl - URL reached after login
 */
function ViewdataLogin(loginUrl, loggedInUrl) {
    this.loginUrl = loginUrl;
    this.loggedInUrl = loggedInUrl;
    this.iframeId = 'viewdataloginiframe';

    // Reuse one login window (destroying window with iframe gives errors on
    // Firefox).
    this.loginWindow = new Ext.IframeWindow({
        id: id,
        width: 900,
        height: 650,
        title: 'Login',
        closeAction: 'hide',
        src: this.loginUrl,
        iframeId: this.iframeId
    });


    /** 
     * Method: showUnauthorisedDialog
     * Displays a dialog box indicating that the user is not authorised to
     * access the requested data. The dialog has options to log in and to retry
     * loading the data.
     *
     * Parameters:
     * retryCallback - {function} function to call to try again to load the data
     */
    this.showUnauthorisedDialog = function(retryCallback) {
        Ext.MessageBox.show(
            {title: "Unauthorised",
             msg: "<p>Authorisation is required for this data.</p>",
             minWidth: 250,
             buttons: {ok: 'Log in', cancel: 'Cancel'},
             fn: this.buttonHandler.bind(this, retryCallback)});
    };

    /** 
     * Method: buttonHandler
     * Handles a button press on the load error message box.
     * If the redraw button is pressed, triggers a map redraw.
     *
     * Parameters:
     * retryCallback - {function} function to call after login
     * buttonId - {String} ID of button pressed
     * text - {String} Input value (unused)
     * opt - {Object} Config object passed to show method (unused)
     */
    this.buttonHandler = function(retryCallback, buttonId, text, opt) {
        if (buttonId === 'ok') {
            this.showLoginDialog(retryCallback);
        }
    };

    /**
     * Displays the login window.
     * @param retryCallback - function to call after login, to retry the action
     *        that required login
     */
    this.showLoginDialog = function(retryCallback) {
        this.retryCallback = retryCallback;
        this.initialLoad = true;
        this.loginWindow.show();

        if (!('iframeEl' in this)) {
            this.iframeEl = document.getElementById(this.iframeId);
            if (this.iframeEl.addEventListener) {
                this.iframeEl.addEventListener('load', this.onLoad.bind(this), false);
            } else if (this.iframeEl.attachEvent) {
                this.iframeEl.attachEvent('onload', this.onLoad.bind(this));
            }
        } else {
            this.iframeEl.src = this.loginUrl;
        }
    };

    /**
     * On-load event handler for login window - determines whether the
     * logged-in URL has been reached, and if to, hides the login window and
     * calls the retry callback.
     */
    this.onLoad = function() {
        // Always display first loaded page.
        if (this.initialLoad) {
            this.initialLoad = false;
            return;
        }
        try {
            var url = this.iframeEl.contentWindow.location.href;
        } catch (exc) {
            return;
        }
        if (url.lastIndexOf(this.loggedInUrl) + this.loggedInUrl.length == url.length) {
            this.loginWindow.hide();
            this.retryCallback();
        }
    };
}
