//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
//Yasound.Invitations.Handler.GenerateMessage = function(form, invitationId) {
//   Ext.Msg.show({
//        title: gettext('Confirmation'),
//        msg: gettext('Do you want to generate invitation message ?'),
//        buttons: Ext.Msg.YESNOCANCEL,
//        fn: function(b, text){
//            if (b == 'yes') {
//                Ext.Ajax.request({
//                    url: String.format('/yabackoffice/invitations/{0}/generate_message/', invitationId),
//                    success: function(result, request){
//                        var data = result.responseText;
//                        var json = Ext.decode(data);
//                        form.getForm().findField('message').setValue(json.data.message);
//                        form.getForm().findField('subject').setValue(json.data.subject);
//            		},
//                    failure: function(result, request){
//                    },
//                    method: 'POST',
//                    timeout: 1000 * 60 * 5
//                });
//            }
//        }
//   });
//};
//
//Yasound.Invitations.Handler.SendInvitation = function(form, invitationId) {
//   Ext.Msg.show({
//        title: gettext('Confirmation'),
//        msg: gettext('Do you want to send invitation ?'),
//        buttons: Ext.Msg.YESNOCANCEL,
//        fn: function(b, text){
//            if (b == 'yes') {
//                Ext.Ajax.request({
//                    url: String.format('/yabackoffice/invitations/{0}/send/', invitationId),
//                    success: function(result, request){
//        				Ext.getCmp('invitations-pendinginvitationgrid').getStore().reload();
//            		},
//                    failure: function(result, request){
//                    },
//                    method: 'POST',
//                    timeout: 1000 * 60 * 5
//                });
//            }
//        }
//   });
//};
//------------------------------------------
// UI
//------------------------------------------


Yasound.Menus.UI.Panel = function() {
	
//	var menuForm = Ext.ComponentMgr.create({
//		xtype:'menuform',
//		region:'south',
//		disabled: true,
//		id: 'menus-menuform',
//		split: true,
//		tbar: [{
//			text: gettext('Generate message'),
//			handler: function(b, e) {
//		    	var menuId = menuForm.getForm().findField('id').getValue();
//		    	Yasound.Invitations.Handler.GenerateMessage(invitationForm, invitationId)
//			}
//		}, {
//			text: gettext('Send invitation'),
//			handler: function(b, e) {
//		    	var invitationId = invitationForm.getForm().findField('id').getValue();
//		    	Yasound.Invitations.Handler.SendInvitation(invitationForm, invitationId)
//			}
//		}],
//		
//		listeners: {
//			success: function(fp, message) {
//				Ext.getCmp('invitations-pendinginvitationgrid').getStore().reload();
//			},
//			failure: function(fp, message) {
//				Yasound.Utils.DisplayLogWindow(message);
//			}
//		}
//		
//	});

//	var pendingInvitationGrid = Ext.ComponentMgr.create({
//		region:'center',
//		id: 'invitations-pendinginvitationgrid',
//		xtype:'invitationgrid',
//		url: '/yabackoffice/invitations/pending',
//		tbar:[{
//    		text: gettext('Create new invitation'),
//    		iconCls: 'silk-add',
//    		handler: function(b, e) {
// 			   Ext.Msg.show({
//			        title: gettext('Confirmation'),
//			        msg: gettext('Do you want to create new invitation ?'),
//			        buttons: Ext.Msg.YESNOCANCEL,
//			        fn: function(bt, text){
//			            if (bt == 'yes') {
//			                var grid = b.ownerCt.ownerCt;
//			                var store = grid.getStore();
//			                var u = new store.recordType({
//			                    fullname: gettext('New VIP')
//			                });
//			                grid.store.insert(0, u);
//			            }
//			        }
//			   });
//    		}
//    	}, {
//    		text: gettext('Delete'),
//    		disabled: true,
//    		ref: '../deleteButton',
//    		iconCls: 'silk-delete',
//    		handler: function(b, e) {
//    			   Ext.Msg.show({
//    			        title: gettext('Confirmation'),
//    			        msg: gettext('Do you want to delete invitation ?'),
//    			        buttons: Ext.Msg.YESNOCANCEL,
//    			        fn: function(bt, text){
//    			            if (bt == 'yes') {
//    			            	var grid = b.ownerCt.ownerCt;
//    			            	selection = grid.getSelectionModel().getSelections();
//    			            	Ext.each(selection, function(record) {
//    			            		grid.store.remove(record);
//    			            	});
//    			            }
//    			        }
//    			   });
//    		}
//    	}],
//		listeners: {
//			selected: function(grid, id, record) {
//				invitationForm.setDisabled(false);
//				grid.deleteButton.setDisabled(false);
//				invitationForm.updateForm(record);
//			},
//			deselected: function(grid) {
//				invitationForm.setDisabled(true);
//				grid.deleteButton.setDisabled(true);
//			}
//		}
//	});
//
//	var sentInvitationGrid = Ext.ComponentMgr.create({
//		url: '/yabackoffice/invitations/sent/',
//		region:'center',
//        hideColumnSent: false,
//		xtype:'invitationgrid',
//		listeners: {
//			selected: function(grid, id, record) {
//				invitationForm.updateForm(record);
//			}
//		}
//	});
//
//	var acceptedInvitationGrid = Ext.ComponentMgr.create({
//		url: '/yabackoffice/invitations/accepted/',
//		region:'center',
//        hideColumnUser: false,
//        hideColumnSent: false,
//		xtype:'invitationgrid',
//		listeners: {
//			selected: function(grid, id, record) {
//				invitationForm.updateForm(record);
//			}
//		}
//	});
	
	return {
		xtype : 'panel',
		title : gettext('Menus management'),
		id : 'menus-panel',
		xtype: 'panel',
		title: gettext('Menus'),
		width: 800,
		split: true,
        defaults: {autoScroll:true},
//        activeItem: 0,
//		items:[{
//				layout:'border',
//				title: gettext('Pending'),
//				items:[pendingInvitationGrid, invitationForm]
//		}, {
//				layout:'border',
//				title: gettext('Sent'),
//				items:[sentInvitationGrid]
//			}, {
//				layout:'border',
//				title: gettext('Accepted'),
//				items:[acceptedInvitationGrid]
//			}
//		],
		updateData : function(component) {
//        	invitationGrid.store.reload();
		}
	};	
}