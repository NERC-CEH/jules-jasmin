/*
 * From http://www.sencha.com/forum/showthread.php?77722-Grid-CellSelectionModel-and-Drag-amp-Drop-a-workaround
 * - allows drag and drop to work for grids with a cell selection model.
 */
Ext.override(Ext.grid.GridPanel, {
    getDragDropText : function(){
      var count;
      
      var sm = this.selModel;
      
      if (sm instanceof Ext.grid.RowSelectionModel)    
        count = sm.getCount();
      if (sm instanceof Ext.grid.CellSelectionModel)
        count = 1;
      return String.format(this.ddText, count, count == 1 ? '' : 's');
    }
});

Ext.override(Ext.grid.GridDragZone, {

    getDragData : function(e){
        var t = Ext.lib.Event.getTarget(e);
        var rowIndex = this.view.findRowIndex(t);
        var cellIndex = this.view.findCellIndex(t);
        
        if(rowIndex !== false){
            var sm = this.grid.selModel;
            
            // RowSelectionModel
            if (sm instanceof Ext.grid.RowSelectionModel)
            {
              if(!sm.isSelected(rowIndex) || e.hasModifier()){
                  sm.handleMouseDown(this.grid, rowIndex, e);
              }
              return {grid: this.grid, ddel: this.ddel, rowIndex: rowIndex, selections:sm.getSelections()};            
            }
            
            // CellSelectionModel
            if (sm instanceof Ext.grid.CellSelectionModel)
            {
              sel = sm.getSelectedCell();
              
              rowAlreadySelected = sel && sel[0] == rowIndex;

              if(!rowAlreadySelected || e.hasModifier()){
                  sm.handleMouseDown(this.grid, rowIndex, cellIndex, e);
              }
              
              store = this.grid.getStore();
              sel = sm.getSelectedCell();
              if (sel)
                return {grid: this.grid, ddel: this.ddel, rowIndex: rowIndex, selections: [store.getAt(sel[0])]};
              else 
                return {grid: this.grid, ddel: this.ddel, rowIndex: rowIndex, selections: []};              
            }            
        }
        return false;
    }

});
