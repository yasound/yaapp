//------------------------------------------
// Datastore
//------------------------------------------

Yasound.Backoffice.Data.SongInstanceStore = function() {
	var fields = ['id', 'name', 'artist_name', 'album_name'];
	var url = '/yabackoffice/radio/0/unmatched/';
	return new Yasound.Utils.SimpleStore(url, fields);
};

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Backoffice.UI.SongInstanceColumnModel = function(sm){
    return ([sm, {
        header: gettext('Track'),
        dataIndex: 'name',
        sortable: true,
        width: 60,
        filterable: true
    }, {
        header: gettext('Album'),
        dataIndex: 'album_name',
        sortable: true,
        width: 60,
        filterable: true
    }, {
        header: gettext('Artist'),
        dataIndex: 'artist_name',
        sortable: true,
        width: 60,
        filterable: true
    }]);
};

Yasound.Backoffice.UI.SongInstanceGrid = Ext.extend(Ext.grid.GridPanel, {
    initComponent: function(){
        this.pageSize = 25;
        this.store = Yasound.Backoffice.Data.SongInstanceStore();
        this.store.pageSize = this.pageSize;
        
    	var sm = new Ext.grid.CheckboxSelectionModel({
            singleSelect: true,
            listeners: {
                selectionchange: function(sm){
					Ext.each(sm.getSelections(), function(record) {
                        this.grid.fireEvent('staffselected', this, record.data.id, record.data.lastname);							
					}, this);
                }
            }
        });

        var config = {
            tbar: [{
                text: gettext('Refresh'),
                iconCls: 'silk-arrow-refresh',
                tooltip: gettext('Refresh'),
                handler: function(btn, e){
                    var grid = btn.ownerCt.ownerCt;
                    grid.getStore().reload();
                }
            }],
            bbar: new Ext.PagingToolbar({
                pageSize: this.pageSize,
                store: this.store,
                displayInfo: true,
                displayMsg: gettext('Displaying {0} - {1} of {2}'),
                emptyMsg: gettext("Nothing to display")
            }),            
            loadMask: false,
            sm: sm,
            cm: new Ext.grid.ColumnModel(Yasound.Backoffice.UI.SongInstanceColumnModel(sm)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            })
        
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Backoffice.UI.SongInstanceGrid.superclass.initComponent.apply(this, arguments);
    },
    refresh: function(radioId) {
    	var url = String.format('/yabackoffice/radio/{0}/unmatched/', radioId);
    	this.store.proxy.setUrl(url, true);
    	this.store.reload();
    }
});
Ext.reg('songinstancegrid', Yasound.Backoffice.UI.SongInstanceGrid);

Yasound.Backoffice.UI.UnmatchedSongsPanel = function(){
	var songGrid = Ext.ComponentMgr.create({
    	xtype:'songinstancegrid',
    	title: gettext('Tracks'),
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
