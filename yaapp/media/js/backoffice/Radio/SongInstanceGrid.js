Yasound.Backoffice.Data.SongInstanceStore = function(url) {
	var fields = ['id', 'name', 'artist_name', 'album_name'];
	return new Yasound.Utils.SimpleStore(url, fields);
};


Yasound.Backoffice.UI.SongInstanceColumnModel = function(sm){
    return ([sm, {
        header: gettext('Track'),
        dataIndex: 'name',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "name"
        }        	
    }, {
        header: gettext('Album'),
        dataIndex: 'album_name',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "album_name"
        }        	
    }, {
        header: gettext('Artist'),
        dataIndex: 'artist_name',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "artist_name"
        }        	
    }]);
};

Yasound.Backoffice.UI.SongInstanceFilters = function(){
    return new Ext.ux.grid.GridFilters({
        encode: false,
        local: true,
        filters: [{
            type: 'string',
            dataIndex: 'name'
        }, {
            type: 'string',
            dataIndex: 'album_name'
        }, {
            type: 'string',
            dataIndex: 'artist_name'
        }]
    });
};

Yasound.Backoffice.UI.SongInstanceGrid = Ext.extend(Ext.grid.GridPanel, {
	singleSelected: false,
	url: '/yabackoffice/radios/{0}/unmatched/',
    tbar: [],
    initComponent: function(){
        this.addEvents('selected', 'unselected');
        this.pageSize = 25;
        this.store = Yasound.Backoffice.Data.SongInstanceStore(this.url);
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
            cm: new Ext.grid.ColumnModel(Yasound.Backoffice.UI.SongInstanceColumnModel(sm)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
            plugins: [Yasound.Backoffice.UI.SongInstanceFilters(), new Ext.ux.grid.GridHeaderFilters()],
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
        Yasound.Backoffice.UI.SongInstanceGrid.superclass.initComponent.apply(this, arguments);
    },
    refresh: function(radioId) {
    	this.radioId = radioId;
    	var url = String.format(this.url, radioId);
    	this.store.proxy.setUrl(url, true);
    	this.calculatePageSize();
    },
    calculatePageSize: function() {
		var bodyHeight = Ext.getBody().getHeight();
		var heightOther = 120+50;
		var rowHeight = 20;
		var gridRows = parseInt( ( bodyHeight - heightOther ) / rowHeight );

		this.getBottomToolbar().pageSize = gridRows;
		this.getStore().reload({ params:{ start:0, limit:gridRows } });
    }
});
Ext.reg('songinstancegrid', Yasound.Backoffice.UI.SongInstanceGrid);
