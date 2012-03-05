
Yasound.Upload.UI.FilePanel = Ext.extend(Ext.form.FormPanel, {
    initComponent: function() {
        this.addEvents('uploadSuccess', 'uploadFailure', 'uploadStarted');
        var fp = this;
        var those = this;
        var config = {
    		border : false,
    		frame : false,
    		layout : 'form',
    		fileUpload : true,
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
    			xtype : 'fileuploadfield',
    			emptyText : gettext('Select a file'),
    			fieldLabel : 'Document',
    			name : 'file',
    			buttonText : '',
    			buttonCfg : {
    				iconCls : 'silk-page-save'
    			}
    		} ],
    		buttonAlign : 'center',
    		buttons : [{
				text : gettext('Import'),
				handler : function(btn, event) {
					if (fp.getForm().isValid()) {
						those.fireEvent('uploadStarted', fp);
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
				}}]
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Upload.UI.FilePanel.superclass.initComponent.apply(this, arguments);
    }	
});
Ext.reg('uploadform', Yasound.Upload.UI.FilePanel);
	
Yasound.Upload.UI.LogPanel = Ext.extend(Ext.Panel, {
    initComponent: function() {
    	this.logContainer = new Ext.ComponentMgr.create({'xtype': 'panel', 'autoscroll': true});
        var config = {
        	items:[this.logContainer]
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Upload.UI.LogPanel.superclass.initComponent.apply(this, arguments);
    },
    addLog: function(log) {
    	this.logContainer.update('<pre>' + log + '</pre>');
    }
});
Ext.reg('logpanel', Yasound.Upload.UI.LogPanel);


Yasound.Upload.UI.UploadSongsPanel = function() {
	var logPanel = new Yasound.Upload.UI.LogPanel({
		title: gettext('Import results'),
		autoScroll: true,
		region : 'center'
	});
	
	return {
		xtype : 'panel',
		title : gettext('Upload songs'),
		id : 'upload-songs-panel',
		layout : 'border',
		items : [ {
			xtype: 'uploadform',
    		split: true,
    		region:'north',
    		height:200,
			listeners: {
				'uploadSuccess': function(component, log) {
					logPanel.addLog(log);
				},
				'uploadFailure': function(component, log) {
					logPanel.addLog(log);
				},
				'uploadStarted': function(component) {
					logPanel.addLog(gettext("Upload started\n"));
				}
			}
		}, logPanel],
		updateData : function(component) {
		}
	};
};