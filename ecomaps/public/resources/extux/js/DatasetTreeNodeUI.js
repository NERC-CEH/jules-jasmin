Ext.namespace('Ext.ux.tree');

/*
 * Extends the standard tree node to add:
 *   an optional information link that opens a URL in a new window - rendered if the node has a metadataURL property
 *   an remove button rendered if the node has property removable = true
 * This version is based on Ext 3.3.0.
 */
Ext.ux.tree.DatasetTreeNodeUI = Ext.extend(Ext.tree.TreeNodeUI, {
    // private
    renderElements : function(n, a, targetNode, bulkRender){
        // add some indent caching, this helps performance when rendering a large tree
        this.indentMarkup = n.parentNode ? n.parentNode.ui.getChildIndent() : '';

        infoLink = Ext.isString(a.metadataURL);
        if (infoLink) {
            var infoIconLinkHtml = '<a href="' + a.metadataURL + '" onclick="window.open(\'' + a.metadataURL
                + '\'); return false;"><img alt="" src="' + this.emptyIcon + '" class="vd-metadata-link" /></a>';
        } else {
            var infoIconLinkHtml = '';
        }
        var removeButtonHtml = '<img ext:qtip="Remove" class="vd-tree-remove-icon" src="' + this.emptyIcon + '" alt="">';
        var cb = Ext.isBoolean(a.checked),
            removable = Ext.isBoolean(a.removable),
            nel,
            href = this.getHref(a.href),
            buf = ['<li class="x-tree-node"><div ext:tree-node-id="',n.id,'" class="x-tree-node-el x-tree-node-leaf x-unselectable ', a.cls,'" unselectable="on">',
            '<span class="x-tree-node-indent">',this.indentMarkup,"</span>",
            '<img alt="" src="', this.emptyIcon, '" class="x-tree-ec-icon x-tree-elbow" />',
            '<img alt="" src="', a.icon || this.emptyIcon, '" class="x-tree-node-icon',(a.icon ? " x-tree-node-inline-icon" : ""),(a.iconCls ? " "+a.iconCls : ""),'" unselectable="on" />',
            cb ? ('<input class="x-tree-node-cb" type="checkbox" ' + (a.checked ? 'checked="checked" />' : '/>')) : '',
            infoIconLinkHtml,
            removable ? removeButtonHtml : '',
            '<a hidefocus="on" class="x-tree-node-anchor" href="',href,'" tabIndex="1" ',
             a.hrefTarget ? ' target="'+a.hrefTarget+'"' : "", '><span unselectable="on">',n.text,"</span></a></div>",
            '<ul class="x-tree-node-ct" style="display:none;"></ul>',
            "</li>"].join('');

        if(bulkRender !== true && n.nextSibling && (nel = n.nextSibling.ui.getEl())){
            this.wrap = Ext.DomHelper.insertHtml("beforeBegin", nel, buf);
        }else{
            this.wrap = Ext.DomHelper.insertHtml("beforeEnd", targetNode, buf);
        }

        this.elNode = this.wrap.childNodes[0];
        this.ctNode = this.wrap.childNodes[1];
        var cs = this.elNode.childNodes;
        this.indentNode = cs[0];
        this.ecNode = cs[1];
        this.iconNode = cs[2];
        var index = 3;
        if (cb) {
            this.checkbox = cs[3];
            // fix for IE6
            this.checkbox.defaultChecked = this.checkbox.checked;
            index++;
        }
        if (infoLink) {
            index++;
        }
        if (removable) {
            this.removeButton = cs[index];
            index++;
            this.node.addEvents('removeclicked');
        }
        this.anchor = cs[index];
        this.textNode = cs[index].firstChild;
    },

    // private
    onClick : function(e){
        if (e.target == this.removeButton) {
            this.fireEvent('removeclicked', this.node, e);
        } else {
            Ext.tree.TreeNodeUI.prototype.onClick.apply(this, [e]);
        }
    }
});
