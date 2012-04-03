//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Statistics.UI.Metrics = function() {
    return {
        title: gettext('Key figures'),
        layout:'fit',
        id:'stats-metrics',
        reload: function(panel) {
            panel.load({
                url: '/yabackoffice/keyfigures/',
                text: gettext('Loading...')
            });
        },
        tools:[{
            id: 'refresh',
            handler: function(event, toolEl, panel) {
                panel.reload(panel);
            }
        }]
    };
};

Yasound.Statistics.UI.Panel = function() {
    return {
		xtype : 'portal',
		title : gettext('Statistics'),
		id : 'statistics-panel',
        items:[{
            columnWidth:.50,
            style:'padding:10px 0 10px 10px',
            items:[{
                title: gettext('Latests radios'),
                layout:'fit',
            	tools:[{
            		id: 'refresh',
            		handler: function(event, toolEl, panel) {
                    	Ext.getCmp('stats-latest-radios').getStore().reload();
            		}
            	}],
                items: [{
                	xtype: 'radiogrid',
                	url: '/yabackoffice/radios?rtype=latest',
                	id:'stats-latest-radios',
                	enablePagination: true,
                	enableFilters: false,
                	height: 400
                }]
            },{
                title: gettext('Biggest radios'),
                layout:'fit',
            	tools:[{
            		id: 'refresh',
            		handler: function(event, toolEl, panel) {
                    	Ext.getCmp('stats-biggest-radios').getStore().reload();
            		}
            	}],
                items: [{
                	xtype: 'radiogrid',
                	url: '/yabackoffice/radios?rtype=biggest',
                	id:'stats-biggest-radios',
                	enablePagination: true,
                	enableFilters: false,
                	height: 400
                }]
            }]
        },{
            columnWidth:.50,
            style:'padding:10px 0 10px 10px',
            items:[{
                title: gettext('Key figures'),
                layout:'fit',
                id:'stats-keyfigures',
                reload: function(panel) {
                	panel.load({
                		url: '/yabackoffice/keyfigures/',
                		text: gettext('Loading...')
                	});
                },
            	tools:[{
            		id: 'refresh',
            		handler: function(event, toolEl, panel) {
            			panel.reload(panel);
            		}
            	}],
            }, Yasound.Statistics.UI.Metrics()]
        }],
        updateData : function(component) {
        	Ext.getCmp('stats-latest-radios').getStore().reload();
        	Ext.getCmp('stats-biggest-radios').getStore().reload();
        	
        	var keyfigures = Ext.getCmp('stats-keyfigures'); 
        	keyfigures.reload(keyfigures);
        	
		}
	};	
}