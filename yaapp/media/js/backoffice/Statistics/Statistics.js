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
		xtype : 'panel',
		title : gettext('Statistics'),
		id : 'statistics-panel',
		layout: 'border',
		items:[{
			xtype:'panel',
			region:'west',
			width:200,
			split:true,
		}, {
			xtype: 'panel',
			region:'center',
			html:'hello, world'
		}],
		updateData : function(component) {
		}
	};	
}