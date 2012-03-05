
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
		title: gettext('Songs assigned to radio'),
		tbar:[{
			text: gettext('Remove from radio'),
		    disabled: true,
		    iconCls: 'silk-delete',
		    ref:'../removeButton',
			handler: function(b, e) {
				var grid = b.ownerCt.ownerCt;
				var selected = grid.getSelectionModel().getSelections();
				Yasound.Radios.Handler.RemoveSong(grid.radioId, selected);
			}
		}
		], 
		listeners: {
			'selected': function(grid, id, record) {
				grid.removeButton.setDisabled(false);
			},
			'deselected': function(grid) {
				grid.removeButton.setDisabled(true);
			} 
		}
	});

	var radioForm = Ext.ComponentMgr.create({
		xtype:'radioform',
		region:'south',
		disabled: true,
		split: true,
		width:350,
		height:300,
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
    	region: 'center',
    	width: 350,
    	tbar:[{
    		text: gettext('Create new radio'),
    		iconCls: 'silk-add',
    		handler: function(b, e) {
                var grid = b.ownerCt.ownerCt;
                var store = grid.getStore();
                var u = new store.recordType({
                    name: gettext('New radio')
                });
                grid.store.insert(0, u);
    		}
    	}],
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
		items : [ {
			layout: 'border',
			region: 'west',
			width: 350,
			split: true,
			items:[radioGrid, radioForm]
		}, songGrid],
		updateData : function(component) {
			radioGrid.getStore().reload();
		}
	};
};