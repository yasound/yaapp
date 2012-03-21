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
            columnWidth:.33,
            style:'padding:10px 0 10px 10px',
            items:[{
                title: gettext('Latests radios'),
                layout:'fit',
                items: [{
                	xtype: 'radiogrid',
                	height:400
                }]
            },{
                title: 'Another Panel 1',
                html: 'hi'
            }]
        },{
            columnWidth:.33,
            style:'padding:10px 0 10px 10px',
            items:[{
                title: 'Panel 2',
                html: 'hi'
            },{
                title: 'Another Panel 2',
                html: 'hi'
            }]
        },{
            columnWidth:.33,
            style:'padding:10px',
            items:[{
                title: 'Panel 3',
                html: 'hi'
            },{
                title: 'Another Panel 3',
                html: 'hi'
            }]
        }],
        updateData : function(component) {
		}
	};	
}