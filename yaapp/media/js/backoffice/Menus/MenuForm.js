Yasound.Menus.UI.MenuForm = Ext.extend(Ext.form.FormPanel, {
    initComponent: function() {
        this.addEvents('success', 'failure', 'started');
        var fp = this;
        var those = this;
        var config = {
    		border : false,
    		frame : true,
    		layout : 'form',
    		fileUpload: true,
    		autoHeight : true,
    		autoScroll: true,
    		bodyStyle : 'padding: 10px 10px 0 10px;',
    		labelWidth : 100,
    		defaults : {
    			anchor : '95%',
    			allowBlank : false
    		},
//    		items : [ {
//    			hidden : true,
//    			contentEl : Ext.get('hidden-csrf').dom.cloneNode(true)
//    		}, {
//    			xtype: 'hidden',
//    			name: 'id'
//    		}, {
//    			xtype : 'textfield',
//    			name: 'fullname',
//    			emptyText : gettext('Enter name of VIP'),
//    			fieldLabel : 'Recipient name'
//    		}, {
//    			xtype: 'textfield',
//    			name: 'email',
//    			fieldLabel: 'Email',
//    			emptyText: gettext('Enter mail of VIP'),
//    			vtype: 'email'
//    		}, {
//    			xtype: 'radiofield',
//    			fieldLabel: 'Radio',
//    			name: 'radio_name',
//    			hiddenName: 'radio_id',
//    			emptyText: gettext('Please choose a radio')
//    		}, {
//    			xtype: 'textfield',
//    			fieldLabel: gettext('Subject'),
//    			emptyText: gettext('Enter subject of invitation'),
//    			name: 'subject'
//    		}, {
//    			xtype: 'textarea',
//    			fieldLabel: gettext('Message'),
//    			height:300,
//    			name: 'message'
//    		}],
    		buttonAlign : 'center'//,
//    		buttons : [{
//				text : gettext('Save'),
//				handler : function(btn, event) {
//					if (fp.getForm().isValid()) {
//						those.fireEvent('started', fp);
//						fp.getForm().submit({
//							url : '/yabackoffice/invitations/save/',
//							method: 'POST',
//							timeout: 1000 * 60 * 5,
//							waitMsg : gettext('Sending informations...'),
//							success : function(fp, o) {
//								if (o.response) {
//									var data = Ext.decode(o.response.responseText);
//									those.fireEvent('success', fp, data.message);
//								} else {
//									those.fireEvent('success', fp, 'Success');
//								}
//							},
//							failure : function(fp, o) {
//								if (o.response) {
//									var data = Ext.decode(o.response.responseText);
//									those.fireEvent('failure', fp, data.message);
//								} else {
//									those.fireEvent('failure', fp, 'Transmission error');
//								}
//							},
//							params : {}
//						});
//					}
//				}}, {
//					text: gettext('Cancel'),
//					handler: function(b, e) {
//						fp.getForm().reset();
//						fp.fillInFromRecord();
//					}
//				}]
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Menus.UI.Menu.superclass.initComponent.apply(this, arguments);
    },
    updateForm: function(record) {
    	this.getForm().reset();
    	this.record = record;
    	this.fillInFromRecord();
    },
    fillInFromRecord: function() {
    	if (!this.record) {
    		return;
    	}
    	this.getForm().findField('_id').setValue(this.record.data._id);
    	this.getForm().findField('name').setValue(this.record.data.name);
    	this.getForm().findField('language').setValue(this.record.data.language);
    	this.getForm().findField('groups').setValue(this.record.data.radio_id, this.record.data.groups);
    }
    
});
Ext.reg('menuform', Yasound.Menus.UI.MenuForm);