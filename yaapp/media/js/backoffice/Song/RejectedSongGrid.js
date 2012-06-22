Yasound.Backoffice.Data.RejectedSongStore = function(url) {
	var fields = ['id', 'name', 'artist_name', 'album_name', 'reject_count'];
	return new Yasound.Utils.SimpleStore(url, fields);
};


Yasound.Backoffice.UI.RejectedSongColumnModel = function(sm){
    return ([sm, {
        header: gettext('Id'),
        dataIndex: 'id',
        sortable: true,
        width: 20,
        filterable: true,
        filter: {
            xtype: "numberfield",
            filterName: "id"
        }        	
    }, {
        header: gettext('Track'),
        dataIndex: 'name',
        sortable: true,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "name"
        }        	
    }, {
        header: gettext('Album'),
        dataIndex: 'album_name',
        sortable: true,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "album_name"
        }        	
    }, {
        header: gettext('Artist'),
        dataIndex: 'artist_name',
        sortable: true,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "artist_name"
        }        	
    }, {
        header: gettext('Reject count'),
        dataIndex: 'reject_count',
        sortable: true,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "reject_count"
        }           
    }]);
};


Yasound.Backoffice.UI.RejectedSongGrid = Ext.extend(Ext.grid.GridPanel, {
	singleSelected: false,
	url: '/yabackoffice/rejected_songs',
    tbar: [],
    initComponent: function(){
        this.addEvents('selected', 'unselected');
        this.pageSize = 25;
        this.store = Yasound.Backoffice.Data.RejectedSongStore(this.url);
        this.store.pageSize = this.pageSize;
        
    	var sm = new Ext.grid.CheckboxSelectionModel({
            singleSelect: this.singleSelect,
            listeners: {
                selectionchange: function(sm){
					Ext.each(sm.getSelections(), function(record) {
                        this.grid.fireEvent('selected', this.grid, record.data.id, record);							
					}, this);
					if (!sm.hasSelection()) {
                        this.grid.fireEvent('deselected', this.grid);							
					}
                }
            }
        });

        var config = {
            tbar: this.tbar,
            bbar: new Ext.PagingToolbar({
                pageSize: this.pageSize,
                store: this.store,
                displayInfo: true,
                displayMsg: gettext('Displaying {0} - {1} of {2}'),
                emptyMsg: gettext("Nothing to display")
            }),            
            loadMask: false,
            sm: sm,
            cm: new Ext.grid.ColumnModel(Yasound.Backoffice.UI.RejectedSongColumnModel(sm)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                autoFill: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
            plugins: [new Ext.ux.grid.GridHeaderFilters()],
        	listeners: {
        		show: function(component) {
        			component.calculatePageSize();
        		},
        		resize: function(component) {
        			component.calculatePageSize();
        		}
        	}
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Backoffice.UI.RejectedSongGrid.superclass.initComponent.apply(this, arguments);
    },
    calculatePageSize: function() {
		var bodyHeight = this.getHeight();
		var heightOther = 120+30;
		var rowHeight = 20;
		var gridRows = parseInt( ( bodyHeight - heightOther ) / rowHeight );

		this.getBottomToolbar().pageSize = gridRows;
		this.getStore().reload({ params:{ start:0, limit:gridRows } });
    }
});
Ext.reg('rejectedsonggrid', Yasound.Backoffice.UI.RejectedSongGrid);
