Yasound.Radios.UI.RadioForm = Ext.extend(Ext.form.FormPanel, {
    initComponent: function() {
        this.addEvents('uploadSuccess', 'uploadFailure', 'uploadStarted');
        var fp = this;
        var those = this;
        var config = {
    		border : false,
    		frame : true,
    		layout : 'form',
    		fileUpload: true,
    		autoHeight : true,
    		bodyStyle : 'padding: 10px 10px 0 10px;',
    		defaults : {
    			anchor : '95%',
    			allowBlank : false
    		},
    		items : [ {
    			hidden : true,
    			contentEl : Ext.get('hidden-csrf').dom.cloneNode(true)
    		}, {
    			xtype: 'hidden',
    			name: 'radio_id'
    		}, {
    			xtype : 'textfield',
    			name: 'radio_name',
    			emptyText : gettext('Enter radio name'),
    			fieldLabel: gettext('Radio name'),
    			allowBlank: false,
    			anchor: '-20'
    		}, {
    			xtype : 'userfield',
    			name: 'creator',
    			hiddenName: 'creator_profile_id',
    			emptyText : gettext('Choose a user'),
    			fieldLabel: gettext('User'),
    			allowBlank: true,
    			anchor: '-20'
    		}, {
				xtype: 'fileupload5field',
    			id : 'form-file',
    			allowBlank: true,
    			emptyText : gettext('Select files or folder'),
    			fieldLabel : gettext('Upload songs'),
    			name : 'songs',
    			buttonText : '',
    			buttonCfg : {
    				iconCls : 'silk-page-save'
    			}
    		}],
    		buttonAlign : 'center',
    		buttons : [{
				text : gettext('Submit'),
				handler : function(btn, event) {
					if (fp.getForm().isValid()) {
						fp.getForm().submit({
							url : '/api/v1/upload_song_ajax/',
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
				}]
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Radios.UI.RadioForm.superclass.initComponent.apply(this, arguments);
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
    	this.getForm().findField('radio_name').setValue(this.record.data.name);
    	this.getForm().findField('radio_id').setValue(this.record.data.id);
    	this.getForm().findField('creator_profile_id').setValue(this.record.data.creator_profile_id, this.record.data.creator_profile);
    }
});
Ext.reg('radioform', Yasound.Radios.UI.RadioForm);