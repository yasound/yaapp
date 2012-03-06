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
	
	var invitationForm = Ext.ComponentMgr.create({
		xtype:'invitationform',
		region:'center'
	});

	var invitationGrid = Ext.ComponentMgr.create({
		title: gettext('Invitations'),
		xtype:'invitationgrid',
		region:'west',
		width:400,
		split:true,
		listeners: {
			selected: function(grid, id, record) {
				invitationForm.updateForm(record);
			}
		}
	});

	return {
		xtype : 'panel',
		title : gettext('Invitations management'),
		id : 'invitations-panel',
		layout: 'border',
		items:[invitationGrid, invitationForm],
		tbar:[{
			text: gettext('New invitation'),
            iconCls: 'silk-add'
		}],
		updateData : function(component) {
        	invitationGrid.store.reload();
		}
	};	
}