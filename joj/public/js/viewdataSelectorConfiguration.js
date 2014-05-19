/** 
 * Creates and manages selectors for dimensions.
 * @class
 *
 * @author R. Wilkinson
 */

/**
 * Creates and manages selectors for dimension data.
 * @constructor
 * @param panel - panel to which selectors should be added
*/
function ViewdataSelectorConfiguration(panel) {
    this.panel = panel;
    this.selectors = [];
    this.stores = [];
    this.disabled = false;

    /**
     * Initialises the data to be displayed on each selector.
     *
     * @param dimensionData - data defining the dimension values to display and how to display them
     */
    this.intialise = function(dimensionData) {
        this.dimensionData = dimensionData;

        var dimensionValues = this.dimensionData.dimensionValues;
        if (this.dimensionData.displayValues) {
            this.displayValues = this.dimensionData.displayValues;
        } else {
            this.displayValues = [dimensionValues];
        }
        this.numSelectors = this.displayValues.length;

        if (typeof(this.dimensionData.displayValueMap) === 'undefined') {

            // Find the distinct set of values for each selector and construct maps from selector
            // value to full dimension value and dimension value to value index.
            var valueMap = {};
            var displayValueMap = {};
            var selectorDisplayValues = [];
            var selectorDisplayValuesFound = [];
            for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
                selectorDisplayValues[selIdx] = [];
                selectorDisplayValuesFound[selIdx] = {};
            }

            for (var stepIdx = 0; stepIdx < dimensionValues.length; ++stepIdx) {
                var stepDisplayValues = [];
                for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
                    var dispVal = this.displayValues[selIdx][stepIdx]
                    stepDisplayValues[selIdx] = dispVal;
                    if (!selectorDisplayValuesFound[selIdx][dispVal]) {
                        selectorDisplayValues[selIdx].push(dispVal);
                        selectorDisplayValuesFound[selIdx][dispVal] = true;
                    }
                }
                displayValueMap[this.makeDisplayValueMapKey(stepDisplayValues)] = dimensionValues[stepIdx];
                valueMap[dimensionValues[stepIdx]] = stepIdx;
            }

            // If necessary, rotate the list of selector values to start at the required value.
            if (this.dimensionData.startValues) {
                for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
                    if (this.dimensionData.startValues[selIdx]) {
                        selectorDisplayValues[selIdx] =
                            this.rotateToStartValue(selectorDisplayValues[selIdx], this.dimensionData.startValues[selIdx]);
                    }
                }
            }
            // Store contructed data in the dimensionData object so that it can be shared between
            // all selectors for that dimension.
            this.dimensionData.valueMap = valueMap;
            this.dimensionData.displayValueMap = displayValueMap;
            this.dimensionData.selectorDisplayValues = selectorDisplayValues;
        }
    };

    /**
     * Creates and configures selectors
     *
     * @param dimensionData - data defining the dimension values to display and how to display them
     * @param idPrefix - prefix for component IDs
     * @param selectHandler - handler for select events
     * @param scope - scope in which to call select event handler
     */
    this.configureSelectors = function(dimensionData, idPrefix, selectHandler, scope) {

        // Initialise the data to be displayed.
        this.intialise(dimensionData);
        this.selectorLastValues = [];

        // Create ComboBox selectors.
        for (var selIdx = this.selectors.length; selIdx < this.numSelectors; ++selIdx) {
            this.createSelector(selIdx, idPrefix, selectHandler, scope);
        }

        // Reset selectors.
        for (var selIdx = 0; selIdx < this.selectors.length; ++selIdx) {
            this.selectors[selIdx].setDisabled(true);
            var valueStore = this.selectors[selIdx].getStore();
            valueStore.removeAll(true);
            this.selectors[selIdx].setValue('');
        }

        // Set the data for the selectors.
        for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
            var selectorValues = this.dimensionData.selectorDisplayValues[selIdx];

            var multiValued = (selectorValues.length > 1);
            var data = [];
            for (var i = 0; i < selectorValues.length; ++i) {
                data.push([selectorValues[i], selectorValues[i]]);
            }

            var valueStore = this.selectors[selIdx].getStore();
            if (data.length > 0) {
                valueStore.loadData(data);
                this.selectors[selIdx].setReadOnly(!multiValued);
                this.selectors[selIdx].setValue(data[0][0]);
            }
        }

        // Make the required number of selectors visible and enabled.
        for (var selIdx = 0; selIdx < this.selectors.length; ++selIdx) {
            var active = (selIdx < this.numSelectors);
            this.selectors[selIdx].setDisabled(!active);
            this.selectors[selIdx].setVisible(active);
        }
    };

    /**
     * Creates a selector.
     *
     * @param selIdx - index of selector to create
     * @param idPrefix - prefix for component IDs
     * @param selectHandler - handler for select events
     * @param scope - scope in which to call select event handler
     */
    this.createSelector = function(selIdx, idPrefix, selectHandler, scope) {
        var valueData = [];
        var valueStore = new Ext.data.ArrayStore({
            id: idPrefix + '_store_' + this.dimensionData.name + '_' + selIdx,
            fields: ['value', 'display'],
            data: valueData
        });
        this.selectors[selIdx] = new Ext.form.ComboBox({
            id: idPrefix + '-select_' + this.dimensionData.name + '_' + selIdx,
            flex: 1,
            editable: false,
            forceSelection: true,
            triggerAction: 'all',
            allowBlank: false,
            mode: 'local',
            store: valueStore,
            valueField: 'value',
            displayField: 'display',
            disabled: true,
            submitValue: false,
            validator: this.validate.bind(this),
            listeners: {
                select: selectHandler,
                scope: scope
            }
        });
        this.panel.add(this.selectors[selIdx]);
    };

    /**
     * Validates the set of values on the selectors for a dimension.
     *
     * @param value - new selector value
     * @return true if values are valid, otherwise an error message
     */
    this.validate = function(value) {
        var val = this.getValue();
        if (val) {
            for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
                this.selectors[selIdx].clearInvalid();
            }
            return true;
        } else {
            return 'This combination of selections does not correspond to a dimension value.';
        }
    };

    /**
     * Rotates the value array for a selector so that the start value is the first value (or last
     * value for reversed ordering).
     *
     * @param values - array of selector values
     * @param startValue - start value prefixed by '+' or '-' indicating that the value order is
     *         forward or reverse respectively
     */
    this.rotateToStartValue = function(values, startValue) {
        var direction = startValue.substr(0, 1);
        var startString = startValue.substr(1);
        var startIndex = null;
        for (var i = 0; i < values.length; ++i) {
            if (values[i] == startString) {
                startIndex = i;
                break;
            }
        }
        if (!startIndex) {
            return values;
        }

        if (direction == '-') {
            var endIndex = (startIndex + 1) % values.length;
            return values.slice(endIndex, values.length).concat(values.slice(0, endIndex));
        } else {
            return values.slice(startIndex, values.length).concat(values.slice(0, startIndex));
        }
    };

    /**
     * Constructs a map key string from the set of values from the selectors.
     *
     * @param values - array of selector values
     * @return key string
     */
    this.makeDisplayValueMapKey = function(values) {
        return values.join("|");
    };

    /**
     * Determines whether there is more than one dimension value to display on the selectors.
     *
     * @return true if multivalued, otherwise false
     */
    this.isMultiValued = function() {
        return (this.dimensionData.dimensionValues.length > 1);
    };

    /**
     * Returns the dimension value corresponding to the current selections.
     *
     * @return dimension value
     */
    this.getValue = function() {
        var values = [];
        for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
            values[selIdx] = this.selectors[selIdx].getValue();
        }
        return this.dimensionData.displayValueMap[this.makeDisplayValueMapKey(values)];
    };

    /**
     * Returns the index of the dimension value corresponding to the current selections.
     *
     * @return dimension index value
     */
    this.getValueByIndex = function() {
        var value = this.getValue();
        return this.findValueIndex(value);
    };

    /**
     * Sets the selectors to the values corresponding to a dimension value.
     *
     * @param value - dimension value
     */
    this.setValue = function(value) {
        // Find the index of this value in the set of full dimension values.
        if (value == null) {
            value = this.dimensionData['default'];
        }
        var valueIdx = this.findValueIndex(value);
        if (valueIdx == null) {
            valueIdx = 0;
        }

        // Set the corresponding display value on each of the selectors.
        for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
            this.selectors[selIdx].setValue(this.displayValues[selIdx][valueIdx]);
            this.selectorLastValues[selIdx] = this.displayValues[selIdx][valueIdx];
        }
    };

    /**
     * Sets the selectors to the values corresponding to a dimension value index.
     *
     * @param valueIndex - the index of a dimension value
     */
    this.setValueByIndex = function(valueIndex) {
        // Set the corresponding display value on each of the selectors.
        for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
            this.selectors[selIdx].setValue(this.displayValues[selIdx][valueIndex]);
            this.selectorLastValues[selIdx] = this.displayValues[selIdx][valueIndex];
        }
    };

    /**
     * Finds the index of a dimension value.
     *
     * @param value - dimension value
     * @return value index
     */
    this.findValueIndex = function(value) {
        var valueIdx = null;
        if (typeof(this.dimensionData.valueMap[value] !== "undefined")) {
            valueIdx = this.dimensionData.valueMap[value];
        }
        return valueIdx;
    };

    /**
     * Resets the selectors to the last valid values to which they were set.
     */
    this.resetToLastValue = function() {
        for (var selIdx = 0; selIdx < this.numSelectors; ++selIdx) {
            this.selectors[selIdx].setValue(this.selectorLastValues[selIdx]);
        }
    };

    /**
     * Marks the selectors as enabled or disabled.
     *
     * @param disabled - disabled status to set for selectors
     */
    this.setDisabled = function(disabled) {
        // The selectors are configured with submitValue=false, so this is just a marker.
        this.disabled = disabled;
    };
}
