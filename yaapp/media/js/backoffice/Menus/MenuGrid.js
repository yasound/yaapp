//------------------------------------------
// Datastore
//------------------------------------------
Yasound.Menus.Data.MenuStore = function(url) {
	var fields = [
	  '_id', 
	  'name', 
	  'language', 
	  'groups', 
	  'sections'
	];
	return new Yasound.Utils.SimpleStore(url, fields);
};

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Menus.UI.menuColumnModel = function(sm) {
	var cm = [{
        header: gettext('Name'),
        dataIndex: 'name',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: 'textfield',
            filterName: 'name'
        }        	
    }, {
        header: gettext('Language'),
        dataIndex: 'language',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: 'textfield',
            filterName: 'language'
        }        	
    }, {
        header: gettext('Groups'),
        dataIndex: 'groups',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: 'textfield',
            filterName: 'groups'
        }        	
    }];
	
	if (sm) {
		cm.splice(0, 0, sm); 
	}
	
    return cm;
};

Yasound.Menu.UI.MenuFilters = function(){
    return new Ext.ux.grid.GridFilters({
        encode: false,
        local: true,
        filters: [{
            type: 'string',
            dataIndex: 'name'
        },
        {
            type: 'string',
            dataIndex: 'language'
        }]
    });
};


Yasound.Menus.UI.MenuGrid = Ext.extend(Ext.grid.GridPanel, {
	singleSelect: true,
	checkboxSelect: true,
	hideColumnUser: true,
	hideColumnSent: true,
	url: '/yabackoffice/menus/',
	tbar:[],
	
    initComponent: function() {
        this.addEvents('selected');
        this.pageSize = 25;
        this.store = Yasound.Menus.Data.MenuStore(this.url);
        this.store.pageSize = this.pageSize;
        
    	var sm = new Ext.grid.CheckboxSelectionModel({
            singleSelect: this.multipleSelection,
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
            tbar:this.tbar,
            bbar: new Ext.PagingToolbar({
                pageSize: this.pageSize,
                store: this.store,
                displayInfo: true,
                displayMsg: gettext('Displaying {0} - {1} of {2}'),
                emptyMsg: gettext("Nothing to display")
            }),            
            loadMask: false,
            sm: sm,
            cm: new Ext.grid.ColumnModel(Yasound.Menus.UI.MenuColumnModel(this.checkboxSelect ? sm : null,
            		this.hideColumnUser, this.hideColumnSent)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
        	plugins: [Yasound.Menus.UI.MenuFilters(), new Ext.ux.grid.GridHeaderFilters()],
        	listeners: {
        		resize: function(component) {
        			component.calculatePageSize();
        		},
        		expand: function(component) {
        			component.calculatePageSize();
        		}
        	}
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Menus.UI.MenuGrid.superclass.initComponent.apply(this, arguments);
    },
    calculatePageSize: function() {
		var bodyHeight = this.getHeight();
		var heightOther = this.getTopToolbar().getHeight() + this.getBottomToolbar().getHeight() + 50;
		var rowHeight = 21;
		var pageSize = parseInt( ( bodyHeight - heightOther ) / rowHeight );
		if (this.pageSize != pageSize) {
			this.getBottomToolbar().pageSize = pageSize;
			this.getStore().reload({ params:{ start:0, limit:pageSize } });
			
			this.pageSize = pageSize;
		}
    }
    
});
Ext.reg('menugrid', Yasound.Menus.UI.MenuGrid);
