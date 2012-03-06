//------------------------------------------
// Datastore
//------------------------------------------

Yasound.Users.Data.UserStore = function() {
	var fields = ['id', 
	              'name', 
	              'account_type',
	              'facebook_uid', {
					name: 'last_authentication_date',
					type: 'date',
					dateFormat: 'Y-m-d H:i:s'
	              },
	              'is_superuser'];
	var url = '/yabackoffice/users';
	return new Yasound.Utils.SimpleStore(url, fields);
};

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Users.UI.UserColumnModel = function(sm) {
	var cm = [{
        header: gettext('Name'),
        dataIndex: 'name',
        sortable: true,
        width: 100,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "name"
        }        	
    }, {
        header: gettext('Facebook UID'),
        dataIndex: 'facebook_uid',
        sortable: true,
        width: 40,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "facebook_uid"
        }        	
    }, {
        header: gettext('Last authentication'),
        dataIndex: 'last_authentication_date',
        xtype: 'datecolumn',
        format: 'd/m/Y H:i:s',
        sortable: true,
        width: 50
    }, new Ext.grid.CheckColumn({
        header: gettext('Superuser?'),
        dataIndex: 'is_superuser',
        sortable: true,
        width: 30
    })];
	
	if (sm) {
		cm.splice(0, 0, sm); 
	}
	
    return cm;
};

Yasound.Users.UI.UserFilters = function(){
    return new Ext.ux.grid.GridFilters({
        encode: false,
        local: true,
        filters: [{
            type: 'string',
            dataIndex: 'name'
        }]
    });
};


Yasound.Users.UI.UserGrid = Ext.extend(Ext.grid.GridPanel, {
	singleSelect: true,
	checkboxSelect: true,
	tbar: [],
    initComponent: function() {
        this.addEvents('selected', 'deselected');
        this.pageSize = 25;
        this.store = Yasound.Users.Data.UserStore();
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
            cm: new Ext.grid.ColumnModel(Yasound.Users.UI.UserColumnModel(this.checkboxSelect ? sm : null)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
        	plugins: [Yasound.Users.UI.UserFilters(), new Ext.ux.grid.GridHeaderFilters()],
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
        Yasound.Users.UI.UserGrid.superclass.initComponent.apply(this, arguments);
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
Ext.reg('usergrid', Yasound.Users.UI.UserGrid);
