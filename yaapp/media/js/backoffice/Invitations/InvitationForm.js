Yasound.Invitations.UI.InvitationForm = Ext.extend(Ext.form.FormPanel, {
    initComponent: function() {
//        this.addEvents('uploadSuccess', 'uploadFailure', 'uploadStarted');
        var fp = this;
        var those = this;
        var config = {
    		border : false,
    		frame : true,
    		layout : 'form',
    		fileUpload: true,
    		autoHeight : true,
    		bodyStyle : 'padding: 10px 10px 0 10px;',
    		labelWidth : 100,
    		defaults : {
    			anchor : '95%',
    			allowBlank : false
    		},
    		items : [ {
    			hidden : true,
    			contentEl : Ext.get('hidden-csrf').dom.cloneNode(true)
    		}, {
    			xtype: 'hidden',
    			name: 'id'
    		}, {
    			xtype : 'textfield',
    			name: 'fullname',
    			emptyText : gettext('Enter name of VIP'),
    			fieldLabel : 'Recipient name'
    		}, {
    			xtype: 'textfield',
    			name: 'email',
    			fieldLabel: 'Email',
    			emptyText: gettext('Enter mail of VIP'),
    			vtype: 'email'
    		}, {
    			xtype: 'radiofield',
    			fieldLabel: 'Radio',
    			name: 'radio_name',
    			hiddenName: 'radio_id',
    			emptyText: gettext('Please choose a radio')
    		}],
    		buttonAlign : 'left',
    		buttons : [{
				text : gettext('Save'),
				handler : function(btn, event) {
					if (fp.getForm().isValid()) {
						those.fireEvent('uploadStarted', fp);
						fp.getForm().submit({
							url : '/yabackoffice/invitations/save/',
							method: 'POST',
							timeout: 1000 * 60 * 5,
							waitMsg : gettext('Sending informations...'),
							success : function(fp, o) {
								if (o.response) {
									var data = Ext.decode(o.response.responseText);
									those.fireEvent('uploadSuccess', fp, data.message);
								} else {
									those.fireEvent('uploadSuccess', fp, 'Success');
								}
							},
							failure : function(fp, o) {
								if (o.response) {
									var data = Ext.decode(o.response.responseText);
									those.fireEvent('uploadFailure', fp, data.message);
								} else {
									those.fireEvent('uploadFailure', fp, 'Transmission error');
								}
							},
							params : {}
						});
					}
				}}, {
					text: gettext('Cancel'),
					handler: function(b, e) {
						fp.getForm().reset();
						fp.fillInFromRecord();
					}
				}, {
					text: 'Send invitation'
				}
				]
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Invitations.UI.InvitationForm.superclass.initComponent.apply(this, arguments);
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
    	this.getForm().findField('id').setValue(this.record.data.id);
    	this.getForm().findField('fullname').setValue(this.record.data.fullname);
    	this.getForm().findField('email').setValue(this.record.data.email);
    	this.getForm().findField('radio_id').setValue(this.record.data.radio_id, this.record.data.radio_name);
    }
    
});
Ext.reg('invitationform', Yasound.Invitations.UI.InvitationForm);