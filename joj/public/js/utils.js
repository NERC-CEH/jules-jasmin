"use strict";

/*jslint onevar: false*/

/*globals WMSC: false, document: false, YAHOO: false, setTimeout: false
          alert: false, window: false */

var Utils = {};

Utils.addHTMLEventListener = function (element, eventName, eventHandler, scope) {

    var scopedEventHandler = function (e) {
        eventHandler.apply(scope, [e, this]);
    };

    
    if (element.addEventListener) {
        element.addEventListener(eventName, scopedEventHandler, false);
    } 
    else if (element.attachEvent) {
        element.attachEvent("on" + eventName, scopedEventHandler);
    }
    
    return scopedEventHandler; // this is useful if you want to remove the handler later
};

Utils.removeHTMLEventListener = function (element, eventName, handler) {

    if (element.removeEventListener) {
        element.removeEventListener(eventName, handler, false);
    } 
    else if (element.detachEvent) {
        element.detachEvent("on" + eventName, handler);
    }
};

Utils.buildScopedFunction = function (fn, scope) {
	return function (e) {
	    fn.apply(scope, [e]); 
	};
};


Utils.buildSelectBox = function (id, descritptions, values, defaultVal) {
    return Utils.buildSelect('select_' + id, 'select_' + id, descritptions, values, defaultVal);
};

Utils.buildSelect = function (id, name, descritptions, values, defaultVal) {
    var i;
    
    var select = document.createElement('select');
    if (name !== null) {
        select.name = name;
    }
    
    if (id !== null) {
        select.id =  id;
    }
    
    for (i = 0; i < values.length; i++) {
        var option = document.createElement('option');
        option.innerHTML = descritptions[i];
        // Required for IE6
        option.value = values[i];
        select.appendChild(option);
    }
                
    // select the default value
    if (defaultVal !== null && defaultVal !== undefined) {
        for (i = 0; i < values.length; i++) {
            if (values[i] === defaultVal) {
                select.selectedIndex = i;
                break;
            }
        }
    }     
    
    return select;  
};

Utils.buildLabel = function (labelText, atts) {
    var label = document.createElement("label");
    label.innerHTML = labelText;
    
    for (var x in atts) {
        label[x] = atts[x];
    }
    
    return label;
};

Utils.buildLabelInputDiv = function (labelText, inputElement, divClass, labelClass) {
    var div = document.createElement("div");
    if (divClass !== undefined) {
        div.className = divClass;
    }
    
    var label = document.createElement("label");
    if (labelClass !== undefined) {
        label.className = labelClass;
    }
    
    label.innerHTML = labelText;
    div.appendChild(label);
    div.appendChild(inputElement);
    
    return div;
};

Utils.addHandlerToFormElements = function (form, eventName, handlerFunction, scope) {
    var handlerLookup = {};
    
    // only attach events to the active elements, this avoids the fieldset element
    // which could cause handlers to be called twice, or not be called at all
    // in IE.
    var activeElements = Utils.getActiveFormElements(form);
    
    for (var i = 0; i < activeElements.length; i++) {
        var element = activeElements[i];

        handlerLookup[element.id] = Utils.addHTMLEventListener(element, 
                                           eventName, handlerFunction, scope);
    }
    
    return handlerLookup;
};

Utils.getActiveFormElements = function (form) {
    var elementList = [];
    var elementTypes = ['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON'];
    
    for (var i = 0; i < form.elements.length; i++) {
        var element = form.elements[i];
        
        if (Utils.isValueInList(element.tagName.toUpperCase(), elementTypes)) {
            elementList.push(element);
        }
    }
    
    return elementList;
};


Utils.removeEventHandlersFromLookup = function (lookup, eventType) {
    
    // default to the change event type
    if (eventType === undefined) {
        eventType = 'change';
    }
    
    for (var id in lookup) {
    	if (id === "") {
    		continue;
    	}
    	
        var element = document.getElementById(id);
        
        if (element === null || element === "") {
        	WMSC.log("Element not found for id=" + id);
        }
        
        var handler = lookup[id];
        
        if (handler !== null) {
            Utils.removeHTMLEventListener(element, eventType, handler);
        }
    }

};

Utils.removeItems = function (array, item) {
    var i = 0;
    while (i < array.length) {
        if (array[i] === item) {
            array.splice(i, 1);
        } else {
            i++;
        }
    }
    return array;
};

Utils.buildHiddenInputElement = function (name, value, id) {
    var input = document.createElement('input');
    input.type = "hidden";
    input.name = name;
    input.value = value;
    
    if (id !== undefined) { 
        input.id = id;
    }
    
    return input;
};

/**
 * Adds the yahoo YUI components to an input, span and div element to create a
 * combobox. The element should be layed out like:
 * 
 *  <container element>
 *    <input id="inputId" type="text" ><//input> <span id="toggleId"><//span>
 *      <div id="optionsContainerId"><//div>
 *  </container element>
 * 
 * @param {String} inputId the id of the input box to be used
 * @param {String} toggleId the id of the element to be used as a button
 * @param {String} optionsContainerId the id of the div to contain the options
 * @param {Array}  the options for the combobox
 * @param {function} [changeHandler] on text changed event handler
 */
Utils.makeCombobox = function (inputId, toggleId, optionsContainerId, dataList, changeHandler) {

    // Instantiate AutoCompletes
    var oConfigs = {
        prehighlightClassName: "yui-ac-prehighlight",
        useShadow: true,
        queryDelay: 0,
        minQueryLength: 0,
        animVert: 0.01,
        maxResultsDisplayed: 25
    };

    var DS = new YAHOO.util.LocalDataSource(dataList);
    
    var AC = new YAHOO.widget.AutoComplete(inputId, optionsContainerId, DS, oConfigs);
    
    if (changeHandler !== null && changeHandler !== undefined) {
        AC.textboxChangeEvent.subscribe(changeHandler);
    }
    
    var lToggler = document.getElementById(toggleId);
    var oPushButtonL = new YAHOO.widget.Button({container: lToggler});
    var toggleL = function (e) {
        YAHOO.util.Event.stopEvent(e);
        if (!YAHOO.util.Dom.hasClass(lToggler, "open")) {
            YAHOO.util.Dom.addClass(lToggler, "open");
        }

        // Is open
        if (AC.isContainerOpen()) {
            AC.collapseContainer();
        }
        // Is closed
        else {
            AC.getInputEl().focus(); // Needed to keep widget active
            setTimeout(function () { // For IE
                AC.sendQuery("");
            }, 0);
        }
    };
    
    //oPushButtonL.on("click", toggleL);
    oPushButtonL.on("mousedown", toggleL);
    AC.containerCollapseEvent.subscribe(function () {
            YAHOO.util.Dom.removeClass(lToggler, "open");
        }
    );

};

/**
 * Adds additional parameters onto the end of a url string, if the string already
 * has a parameter with the same name set, the additional parameter is ignored.
 * 
 * @param {String} url The url to add the parameters to
 * @param {Object} params An object whos attributes correspond to the params to 
 *      be added, so that params[paramName] = paramValue.
 */
Utils.addParamsToUrl = function (url, params) {
       
    // build a list of uppercase params already on the url
    var urlParams = Utils.getParamsFromURL(url);

    var existingParams = [];
    for (var pName in urlParams) {
        existingParams.push(pName.toUpperCase());
    }
    
    //check the existing params to see if we will be adding the first param
    var first = true;
    if (existingParams.length > 0) {
        first = false;
    }
    
    var paramsStr = "";
    for (var p in params) {
        
        // if the paramer is already on the list then ignore it
        if (Utils.isValueInList(p.toUpperCase(), existingParams)) {
            continue;
        }

        // build up a string of the new parameters 
        if (first === true) {
            paramsStr += "?";
            first = false;
        }
        else {
            paramsStr += "&";
        }
        
        paramsStr += p + "=" + params[p];    
    }
    
    return url + paramsStr;
};

/**
 * Replaces existing parameters in a url with the new ones provided. If the new 
 * parameters don't already exist in the url they will be added.
 * 
 * @param {String} url The url to add the parameters to
 * @param {Object} params An object whos attributes correspond to the params to 
 *      be added, so that params[paramName] = paramValue.
 */
Utils.replaceParamsInUrl = function (url, params) {
    var addedFirst = false;
    var urlStart = url;
    if (url.indexOf('?') > 0) {
        urlStart = url.substring(0, url.indexOf('?'));
    }
    
    var paramsString = "";
    var newParams = [];
    
    for (var p in params) {
        
        newParams.push(p.toUpperCase());
        
        if (addedFirst === false) {
            paramsString += "?";
            addedFirst = true;
        } 
        else {
            paramsString += "&";    
        }
        
        paramsString += p + "=" + params[p];
    }
    
    // build a list of uppercase params already on the url
    var existingParams = Utils.getParamsFromURL(url);

    for (p in existingParams) {
        if (Utils.isValueInList(p.toUpperCase(), newParams)) {
            continue;
        }
        else if (existingParams[p] === "") {
            continue;
        }
        
        if (addedFirst === false) {
            paramsString += "?";
            addedFirst = true;
        } 
        else {
            paramsString += "&";    
        }
        
        paramsString += p + "=" + existingParams[p];        
    }
    
    return urlStart + paramsString;
};

/**
 * Removes existing parameters in a url with the new ones provided.
 * 
 * @param {String} url The url to add the parameters to
 * @param {Array} an array of params to remove from the url
 */
Utils.removeParamsInUrl = function (url, params) {
    var urlStart = url;
    if (url.indexOf('?') > 0) {
        urlStart = url.substring(0, url.indexOf('?'));
    }
    
    var paramsString = "";
    var removeParams = [];
    
    for (var i = 0; i < params.length; i++) {
        removeParams.push(params[i].toUpperCase());
    }
    
    // build a list of uppercase params already on the url
    var existingParams = Utils.getParamsFromURL(url);

    var addedFirst = false;
    for (var p in existingParams) {
        if (Utils.isValueInList(p.toUpperCase(), removeParams)) {
            continue;
        }
        
        if (addedFirst === false) {
            paramsString += "?";
            addedFirst = true;
        } 
        else {
            paramsString += "&";    
        }
        
        paramsString += p + "=" + existingParams[p];        
    }
    
    return urlStart + paramsString;
};

/**
 * finds out if a list contains a particular value
 * 
 * @param {javascript primative} value The javascript primative object to search for
 * @param {Array} list The list of values to search
 * @returns bool indicating if the value was found
 */
Utils.isValueInList = function (value, list) {
    var included = false;
    
    for (var i = 0; i < list.length; i++) {
        if (value === list[i]) {
            included = true;
            break;
        }
    }    
    
    return included;
};


/**
 * Gets the parameters form a given url.
 * 
 * @param {String} url The url to retrive the parameters from
 * @returns An object where the attributes correspond to the parameters found
 *      (like a dictionary, obj[paramName] = paramValue)
 */
Utils.getParamsFromURL = function (url) {
    var params = {};
    if (url.indexOf('?') > 0) {
        var paramsStr = url.substr(url.indexOf('?') + 1);
        
        for (var i = 0; i < 2000; i++) {
            
            var end = paramsStr.indexOf('&');
            if (end === -1) {
                end = paramsStr.length;
            }
            
            var pName = paramsStr.substring(0, paramsStr.indexOf('='));
            var pValue = paramsStr.substring(paramsStr.indexOf('=') + 1, end);
            if (pName) {
                params[pName] = pValue;
            }

            if (paramsStr.indexOf('&') < 0) { 
                break; 
            }
            
            paramsStr = paramsStr.substr(paramsStr.indexOf('&') + 1);
        }
    }
    
    return params;
};

Utils.findPos = function (obj) {
    var curleft = 0;
    var curtop = 0;
    if (obj.offsetParent) {
        
        do {
            curleft += obj.offsetLeft;
            curtop += obj.offsetTop;
            WMSC.log(" obj, height, width , left, top= " + obj + "," + obj.offsetHeight + "," + obj.offsetWidth + "," + obj.offsetLeft + "," + obj.offsetTop);
            obj = obj.offsetParent;
        } while (obj);
        
        return [curleft, curtop];
    }
};

Utils.reMatch = function (expression, txt) {
    var re = new RegExp(expression);
    var result = re.test(txt);
    //WMSC.log("expression =" + expression + " text =" + txt + " match = " + result);
    return result;
};

Utils.alertErrorMessage = function (msg, u, l) {
    var txt = "Error: " + msg + "\n";
    txt += "URL: " + u + "\n";
    txt += "Line: " + l + "\n\n";
    alert(txt);
};

Utils.disableEnterKey = function (e) {
    var key;     
    if (window.event) {
        key = window.event.keyCode; // for IE
    }
    else {
        key = e.which; // for FF 
    }
    
    var allow;
    if (key === 13) {
        WMSC.log("Enter detected");
        allow = false;
        e.preventDefault();
    }
    else {
        allow = true;
    }
    
    return allow;
};

Utils.logAtts = function (obj) {
    for (var x in obj) {
        if (typeof(obj[x]) === 'function') {
            WMSC.log(" " + x + " method");
        }
        else {
            WMSC.log(" " + x + " = " + obj[x]);
        }
    }
};

Utils.getContainedElementsByName = function (node, name) {
    var children = node.getElementsByTagName('*');
    
    var matchingChildren = [];
    for (var i = 0; i < children.length; i++) {
        if (children[i].name === name) {
            matchingChildren.push(children[i]);
        }
    }
    
    return matchingChildren;
};

Utils.getDateString = function () {

    var d = new Date();
    
    // based on the code from the json2 file
    // http://www.json.org/json2.js
    
    function f(n) {
        return n < 10 ? '0' + n : n;
    }
    
    return d.getUTCFullYear()   + '-' +
         f(d.getUTCMonth() + 1) + '-' +
         f(d.getUTCDate())      + 'T' +
         f(d.getUTCHours())     + ':' +
         f(d.getUTCMinutes())   + ':' +
         f(d.getUTCSeconds())   + 'Z';
};

Utils.getTimeString = function () {

    var d = new Date();
    
    // based on the code from the json2 file
    // http://www.json.org/json2.js
    
    function f(n) {
        return n < 10 ? '0' + n : n;
    }
    
    return f(d.getUTCHours())     + ':' +
         f(d.getUTCMinutes())   + ':' +
         f(d.getUTCSeconds())   + '.' +
         d.getMilliseconds();
    
};

Utils.getObjString = function (obj) {
    var str = "{";
    
    for (var p in obj) {
        str += "'" + p + "':" + obj[p] + ",";
    }
    
    return str;
    
};

Utils.buildObjectList = function (Klass, objList) {
    var retList = [];
    
    if (objList !== null) {
        for (var i = 0; i < objList.length; i++) {
            retList.push(new Klass(objList[i]));
        }
    }
    
    return retList;
};

Utils.hasAttr = function (obj, attr) {
    
    for (var p in obj) {
        if (p === attr) {
            return true;
        }
    }
    
    return false;
};
