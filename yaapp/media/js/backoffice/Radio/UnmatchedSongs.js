//------------------------------------------
// Datastore
//------------------------------------------


//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------

Yasound.Backoffice.UI.UnmatchedSongsPanel = function(){
	var songGrid = Ext.ComponentMgr.create({
    	xtype:'songinstancegrid',
    	title: gettext('Songs'),
    	region:'center'
	});
	
	var radioGrid = Ext.ComponentMgr.create({
    	xtype:'radiogrid',
    	title: gettext('Radios'),
    	region:'west',
    	split:true,
    	width:200,
    	singleSelect: true,
    	checkboxSelect: false,
    	listeners: {
    		'radioselected': function(grid, id, record) {
    			songGrid.refresh(id)
    		}
    	}		
	});
	
    return {
        xtype: 'panel',
        layout: 'border',
        id: 'contacts-panel',
        title: gettext('Unmatched songs'),
        items: [radioGrid, songGrid],
        updateData: function(component) {
        	radioGrid.store.reload();
        }
    };
};
