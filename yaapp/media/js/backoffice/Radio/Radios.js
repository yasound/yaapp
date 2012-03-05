//------------------------------------------
// Datastore
//------------------------------------------

Yasound.Backoffice.Data.RadioStore = function() {
	var fields = ['id', 'name'];
	var url = '/yabackoffice/radios/';
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
        header: gettext('Name'),
        dataIndex: 'name',
        sortable: true,
        width: 60,
        filterable: true
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
	
    initComponent: function() {
        this.addEvents('radioselected');
        this.pageSize = 25;
        this.store = Yasound.Backoffice.Data.RadioStore();
        this.store.pageSize = this.pageSize;
        
    	var sm = new Ext.grid.CheckboxSelectionModel({
            singleSelect: this.multipleSelection,
            listeners: {
                selectionchange: function(sm){
					Ext.each(sm.getSelections(), function(record) {
                        this.grid.fireEvent('radioselected', this, record.data.id, record);							
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
            cm: new Ext.grid.ColumnModel(Yasound.Backoffice.UI.RadioColumnModel(this.checkboxSelect ? sm : null)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
        	plugins: [Yasound.Backoffice.UI.RadioFilters()]
        
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Backoffice.UI.RadioGrid.superclass.initComponent.apply(this, arguments);
    }
});
Ext.reg('radiogrid', Yasound.Backoffice.UI.RadioGrid);
