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
		title: gettext('Not sent'),
        flex:1,
		xtype:'invitationgrid',
		listeners: {
			selected: function(grid, id, record) {
				invitationForm.updateForm(record);
			}
		}
	});

	var pendingInvitationGrid = Ext.ComponentMgr.create({
		title: gettext('Pending'),
        hideColumnSent: false,
		xtype:'invitationgrid',
		listeners: {
			selected: function(grid, id, record) {
				invitationForm.updateForm(record);
			}
		}
	});

	var sentInvitations = Ext.ComponentMgr.create({
		title: gettext('Sent'),
        hideColumnUser: false,
        hideColumnSent: false,
		xtype:'invitationgrid',
		listeners: {
			selected: function(grid, id, record) {
				invitationForm.updateForm(record);
			}
		}
	});
	
	var invitationsPanel = {
		region: 'west',
		title: gettext('Invitations'),
		width: 800,
		split: true,
        layout: { 
        	type: 'accordion',
        	animate: true
        },
		items:[invitationGrid, pendingInvitationGrid, sentInvitations]
	}

	return {
		xtype : 'panel',
		title : gettext('Invitations management'),
		id : 'invitations-panel',
		layout: 'border',
		items:[invitationsPanel, invitationForm],
		updateData : function(component) {
        	invitationGrid.store.reload();
		}
	};	
}