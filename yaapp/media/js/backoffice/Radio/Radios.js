

Yasound.Radios.UI.RadiosPanel = function() {
	var songGrid = Ext.ComponentMgr.create({
		xtype: 'songinstancegrid',
		region: 'center',
		title: gettext('Songs')
	});

	var radioForm = Ext.ComponentMgr.create({
		xtype:'radioform',
		region:'west',
		split: true,
		width:350
	})

	var radioGrid = Ext.ComponentMgr.create({
    	xtype:'radiogrid',
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