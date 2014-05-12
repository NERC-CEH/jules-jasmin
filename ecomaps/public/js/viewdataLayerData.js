/** 
 * Holds cached data about layers.
 * @class
 *
 * @author R. Wilkinson
 */

/**
 * Constructor to initialise data store.
 * @constructor
*/
function ViewdataLayerData() {
    this.DIMENSION_PREFIX = 'dimension_';
    this.layerData = {};

    /**
     * Stores a property value for a given layer id.
     * @param id - layer id
     * @param property - name of property
     * @param value - property value
     */
    this.setProperty = function(id, property, value) {
        if (typeof(this.layerData[id]) === 'undefined') {
            this.layerData[id] = {};
        }
        this.layerData[id][property] = value;
    };

    /**
     * Retrieves a property value for a given layer id.
     * @param id - layer id
     * @param property - name of property
     * @return property value
     */
    this.getProperty = function(id, property) {
        if ((typeof(this.layerData[id]) === 'undefined') || (typeof(this.layerData[id][property]) === 'undefined')) {
            return null;
        }
        return this.layerData[id][property];
    };

    /**
     * Stores a dimension value for a given layer id.
     * @param id - layer id
     * @param dimension - name of dimension
     * @param value - dimension value
     */
    this.setDimension = function(id, dimension, value) {
        if (typeof(this.layerData[id]) === 'undefined') {
            this.layerData[id] = {};
        }
        this.layerData[id][this.DIMENSION_PREFIX + dimension] = value;
    };

    /**
     * Retrieves a dimension value for a given layer id.
     * @param id - layer id
     * @param dimension - name of dimension
     * @return dimension value
     */
    this.getDimension = function(id, dimension) {
        var property = this.DIMENSION_PREFIX + dimension;
        if ((typeof(this.layerData[id]) === 'undefined') || (typeof(this.layerData[id][property]) === 'undefined')) {
            return null;
        }
        return this.layerData[id][property];
    };

    /**
     * Deletes the data for a layer.
     * @param id - layer id
     */
    this.deleteLayer = function(id) {
        if (typeof(this.layerData[id]) !== 'undefined') {
            delete this.layerData[id];
        }
    };
}
