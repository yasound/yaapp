//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------


Yasound.Invitations.UI.Panel = function() {
	var invitationGrid = Ext.ComponentMgr.create({
		title: gettext('Invitations'),
		xtype:'invitationgrid',
		region:'west',
		width:400,
		split:true
	})
	return {
		xtype : 'panel',
		title : gettext('Invitations management'),
		id : 'invitations-panel',
		layout: 'border',
		items:[invitationGrid, {
			xtype: 'panel',
			region:'center',
			html:'hello, world'
		}],
		tbar:[{
			text: gettext('New invitation'),
            iconCls: 'silk-add'
		}],
		updateData : function(component) {
        	invitationGrid.store.reload();
		}
	};	
}