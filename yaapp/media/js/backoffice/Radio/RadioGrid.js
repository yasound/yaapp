//------------------------------------------
// Datastore
//------------------------------------------

Yasound.Backoffice.Data.RadioStore = function(url) {
	var fields = ['id', 'name', 'creator', 'creator_id', 'creator_profile_id', 'creator_profile'];
	return new Yasound.Utils.SimpleStore(url, fields);
};

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Backoffice.UI.RadioColumnModel = function(sm) {
	var cm = [{
        header: gettext('Id'),
        dataIndex: 'id',
        sortable: true,
        width: 10,
        filterable: true,
        filter: {
            xtype: "numberfield",
            filterName: "id"
        }        	
        
    }, {
        header: gettext('Name'),
        dataIndex: 'name',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "name"
        }        	
    }, {
        header: gettext('Owner'),
        dataIndex: 'creator_profile',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "creator_profile"
        }        	
    }];
	
	if (sm) {
		cm.splice(0, 0, sm); 
	}
	
    return cm;
};

Yasound.Backoffice.UI.RadioFilters = function(){
    return new Ext.ux.grid.GridFilters({
        encode: false,
        local: true,
        filters: [{
            type: 'string',
            dataIndex: 'name'
        }]
    });
};


Yasound.Backoffice.UI.RadioGrid = Ext.extend(Ext.grid.GridPanel, {
	singleSelect: true,
	checkboxSelect: true,
	tbar: [],
	url: '/yabackoffice/radios',
	enablePagination: true,
	
    initComponent: function() {
        this.addEvents('selected', 'deselected');
        this.pageSize = 25;
        this.store = Yasound.Backoffice.Data.RadioStore(this.url);
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
            loadMask: false,
            sm: sm,
            cm: new Ext.grid.ColumnModel(Yasound.Backoffice.UI.RadioColumnModel(this.checkboxSelect ? sm : null)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                autoFill: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
        	plugins: [Yasound.Backoffice.UI.RadioFilters(), new Ext.ux.grid.GridHeaderFilters()],
        	listeners: {
        		show: function(component) {
        			component.calculatePageSize();
        		},
        		resize: function(component) {
        			component.calculatePageSize();
        		}
        	}
        }; // eo config object
        
        if (this.enablePagination) {
        	Ext.apply(config, {
                bbar: new Ext.PagingToolbar({
                    pageSize: this.pageSize,
                    store: this.store,
                    displayInfo: true,
                    displayMsg: gettext('Displaying {0} - {1} of {2}'),
                    emptyMsg: gettext("Nothing to display")
                })            
        	});
        }
        
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Backoffice.UI.RadioGrid.superclass.initComponent.apply(this, arguments);
    },
    calculatePageSize: function() {
		var bodyHeight = this.getHeight();
		var heightOther = this.getTopToolbar().getHeight() + this.getBottomToolbar().getHeight() + 50;
		var rowHeight = 21;
		var gridRows = parseInt( ( bodyHeight - heightOther ) / rowHeight );

		this.getBottomToolbar().pageSize = gridRows;
		
		if (this.enablePagination) {
			this.getStore().reload({ params:{ start:0, limit:gridRows } });
		}
    }
    
});
Ext.reg('radiogrid', Yasound.Backoffice.UI.RadioGrid);
