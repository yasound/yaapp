//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------


Yasound.SearchEngine.UI.Fuzzy = function() {
	return {
		xtype : 'panel',
		title : gettext('Fuzzy song search'),
		id : 'fuzzy-panel',
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