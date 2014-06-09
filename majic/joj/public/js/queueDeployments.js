// This javascript uses the yahoo queue library function to allow sequential,
// incremental loading of the deployments data - so this can be loaded after
// the rest of the atom data is displayed
YUI({combine: true, timeout: 10000}).use("anim", "queue",function (Y) {

var MyApp = {
    NAME : 'Loading deployments info...',
	
    q : new Y.Queue(),

    nodes : {
        root    : null,
        status  : null,
        content : null,
        foot    : null
    },

    render : function (container) {
        if (MyApp.nodes.root) {
            MyApp.q.stop();

            MyApp.q.add(
                MyApp.destroy
            );
        }

        // artificial delays have been inserted to simulate _renderNav or
        // _renderContent being process intensive and taking a while to complete
        MyApp.q.add(
            // pass the container param to the callback using Y.bind
            Y.bind(MyApp._renderFramework, MyApp, container),
            MyApp._loadDeployments).run();
    },

    destroy : function () {
        var root = MyApp.nodes.root;

        if (root) {
            Y.Event.purgeElement(root,true);
            root.set('innerHTML','');
        }
    },

    setStatus : function (message,working) 
    {
        MyApp.nodes.status.set('innerHTML',message);
        MyApp.nodes.foot[working?'addClass':'removeClass']('working');
    },

    _renderFramework : function (container) {
        var root = MyApp.nodes.root = Y.get(container);

        root.set('innerHTML',
        '<div class="yui-module">'+
            '<div class="linehead">'+
                '<h4>'+MyApp.NAME+'</h4>'+
            '</div>'+
            '<div class="yui-bd">'+
                '<div class="yui-content"></div>'+
            '</div>'+
            '<div class="yui-ft">'+
                '<p class="yui-status"></p>'+
            '</div>'+
        '</div>');

        MyApp.nodes.status  = root.query('p.yui-status');
        MyApp.nodes.content = root.query('.yui-content');
        MyApp.nodes.foot    = root.query('.yui-ft');

        MyApp.nodes.content.setStyle('opacity',0);
        MyApp.setStatus('Loading...',true);
    },

	_loadDeployments : function ()
	{
		var setContent = function (xhr) 
		{
		/**
		NB, could set the content here, but we want to replace the whole div element
		to load the new header titles
        var content = MyApp.nodes.content;
        content.appendChild(Y.Node.create(xhr.responseText));
		MyApp.nodes.root.set('innerHTML','');

        new Y.Anim({
            node : content,
            to :   { opacity : 1 },
            duration : .8
        }).run();
        */
	    	$('deploymentsPlaceholder').innerHTML = '';
			var deploymentsHTML = xhr.responseText;
			if (deploymentsHTML)
				$('deploymentsPlaceholder').innerHTML = deploymentsHTML;
		};
	   	var id = $('datasetID').value;
		new Ajax.Request('/viewDeployments/' + id, 
			{parameters: {},
	    	method: "get",
	    	onSuccess: setContent.bindAsEventListener(this)
			});
	}
};

window.onload = function (e) {
    e.preventDefault();
    MyApp.render('#deploymentsPlaceholder');
};

// expose the example structure
YUI.example = { MyApp : MyApp };

});
