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
		region:'south',
		split: true
	});

	var pendingInvitationGrid = Ext.ComponentMgr.create({
		region:'center',
		xtype:'invitationgrid',
		url: '/yabackoffice/invitations/pending/',
		listeners: {
			selected: function(grid, id, record) {
				invitationForm.updateForm(record);
			}
		}
	});

	var sentInvitationGrid = Ext.ComponentMgr.create({
		url: '/yabackoffice/invitations/sent/',
		region:'center',
        hideColumnSent: false,
		xtype:'invitationgrid',
		listeners: {
			selected: function(grid, id, record) {
				invitationForm.updateForm(record);
			}
		}
	});

	var acceptedInvitationGrid = Ext.ComponentMgr.create({
		url: '/yabackoffice/invitations/accepted/',
		region:'center',
        hideColumnUser: false,
        hideColumnSent: false,
		xtype:'invitationgrid',
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
		xtype: 'tabpanel',
		title: gettext('Invitations'),
		width: 800,
		split: true,
        defaults: {autoScroll:true},
        activeItem: 0,
		items:[{
				layout:'border',
				title: gettext('Pending'),
				items:[pendingInvitationGrid, invitationForm]
		}, {
				layout:'border',
				title: gettext('Sent'),
				items:[sentInvitationGrid]
			}, {
				layout:'border',
				title: gettext('Accepted'),
				items:[acceptedInvitationGrid]
			}
		],
		updateData : function(component) {
//        	invitationGrid.store.reload();
		}
	};	
}