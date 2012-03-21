//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------


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
                	enablePagination: false,
                	enableFilters: false,
                	autoHeight: true
                }]
            },{
                title: 'Another Panel 1',
                html: 'hi'
            }]
        },{
            columnWidth:.50,
            style:'padding:10px 0 10px 10px',
            items:[{
                title: 'New radios for the day',
                layout:'fit',
                items:[{
	                xtype: 'chartpanel',
		            height:300
                }]
            },{
                title: 'New radios for the week',
                layout:'fit',
                items:[{
	                xtype: 'chartpanel',
	    	        height:300
                }]
            }, {
                title: 'New radios for the month',
                layout:'fit',
                items:[{
                	xtype: 'chartpanel',
                	height:300
                }]
            }]
        }],
        updateData : function(component) {
        	Ext.getCmp('stats-latest-radios').getStore().reload();
		}
	};	
}