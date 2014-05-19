"use strict";

/**
 * Top-level definitions of the Javascript WMS client library.
 *
 * Define a namespace for the package.
 */

// allowing access to console directly here as any exception raised will be caught
/*global console:false */

var WMSC = {};

WMSC.DEBUG = true;

WMSC.log = function (msg) {
    
    if (!WMSC.DEBUG) {
        return;
    }
    
    try 
    {
		/* If Firebug (and Mozilla?) */
		console.log(msg);
    }
    catch (err) 
    {	
  		//give up

		//Debug.write(msg);
    }
};
