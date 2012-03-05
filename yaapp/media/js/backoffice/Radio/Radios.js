
//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Radios.Handler.RemoveSong = function(radioId, selected) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to remove songs from radio'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
            	ids = [];
            	Ext.each(selected, function(record) {
            		ids.push(record.data.id);
            	});
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/radios/{0}/remove_songs/', radioId),
                    success: function(result, request){
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('radios-songgrid').getStore().reload();
            		},
                    failure: function(result, request){
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        song_instance_id: ids
                    }
                });
            }
        }
   });
}


Yasound.Radios.UI.RadiosPanel = function() {
	var songGrid = Ext.ComponentMgr.create({
		xtype: 'songinstancegrid',
    	id:'radios-songgrid',
		region: 'center',
		url: '/yabackoffice/radios/{0}/songs/',
		radio_id: 0,
		title: gettext('Songs'),
		tbar:[{
		    text: gettext('Refresh'),
		    iconCls: 'silk-arrow-refresh',
		    tooltip: gettext('Refresh'),
		    handler: function(btn, e){
		        var grid = btn.ownerCt.ownerCt;
		        grid.getStore().reload();
		    }
		}, {
			text: gettext('Remove from radio'),
			handler: function(b, e) {
				var grid = b.ownerCt.ownerCt;
				var selected = grid.getSelectionModel().getSelections();
				Yasound.Radios.Handler.RemoveSong(grid.radioId, selected);
			}
		}
		]
	});

	var radioForm = Ext.ComponentMgr.create({
		xtype:'radioform',
		region:'west',
		disabled: true,
		split: true,
		width:350,
		listeners: {
			uploadSuccess: function() {
				songGrid.getStore().reload();
				Ext.getCmp('radios-radiogrid').getStore().reload();
			}
		}
	})

	var radioGrid = Ext.ComponentMgr.create({
    	xtype:'radiogrid',
    	id:'radios-radiogrid',
    	title: gettext('Radios'),
    	region: 'west',
    	split: true,
    	width: 200,
    	singleSelect: true,
    	checkboxSelect: false,
    	listeners: {
    		'radioselected': function(grid, id, record) {
    			songGrid.refresh(id);
    			radioForm.updateForm(record);
    			radioForm.setDisabled(false);
    		}
    	}		
	});

	
	return {
		xtype : 'panel',
		title : gettext('Radios management'),
		id : 'radios-panel',
		layout : 'border',
		items : [ radioGrid, {
			layout: 'border',
			region: 'center',
			items: [radioForm, songGrid]
		}],
		updateData : function(component) {
			radioGrid.getStore().reload();
		}
	};
};