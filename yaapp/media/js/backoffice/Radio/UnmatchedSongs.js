//------------------------------------------
// Datastore
//------------------------------------------

Yasound.Backoffice.Data.SongInstanceStore = function(){
    return new Ext.data.GroupingStore({
        reader: new Ext.data.JsonReader({
            idProperty: 'id',
            fields: ['id', 'name', 'artist_name', 'album_name'],
            root: 'data',
            totalProperty: 'results'
        }),
        writer: new Ext.data.JsonWriter({
            encode: true,
            writeAllFields: true
        }),
        sortInfo: {
            field: 'id',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        },
        autoLoad: false,
        remoteSort: false,
        restful: true,
        proxy: new Ext.data.HttpProxy({
            url: '/yabackoffice/radio/1/unmatched/',
            method: 'GET'
        }),
        listeners: {
            beforewrite: function(store, action, records, options, arg){
                Ext.apply(store.baseParams, additionalParams);
            },
            beforeLoad: function(store, options){
				if (!options.params.start) {
					store.baseParams.start = 0;
				}
                if (!options.params.limit) {
                    store.baseParams.limit = store.pageSize;
                }
            }
        }
    });
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
        this.pageSize = 10;
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
    }
});
Ext.reg('songinstancegrid', Yasound.Backoffice.UI.SongInstanceGrid);

Yasound.Backoffice.UI.UnmatchedSongsPanel = function(){
    return {
        xtype: 'panel',
        layout: 'border',
        id: 'contacts-panel',
        title: gettext('Unmatched songs'),
        items: [{
        	xtype:'songinstancegrid',
        	region:'center'
        }],
        updateData: function(component){
        }
    };
};
