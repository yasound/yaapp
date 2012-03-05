//------------------------------------------
// Datastore
//------------------------------------------
Yasound.Invitations.Data.InvitationStore = function() {
	var fields = ['id', 'fullname'];
	var url = '/yabackoffice/invitations/';
	return new Yasound.Utils.SimpleStore(url, fields);
};

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Invitations.UI.InvitationColumnModel = function(sm) {
	var cm = [{
        header: gettext('Name'),
        dataIndex: 'fullname',
        sortable: true,
        width: 60,
        filterable: true
    }];
	
	if (sm) {
		cm.splice(0, 0, sm); 
	}
	
    return cm;
};

Yasound.Invitations.UI.InvitationFilters = function(){
    return new Ext.ux.grid.GridFilters({
        encode: false,
        local: true,
        filters: [{
            type: 'string',
            dataIndex: 'fullname'
        }]
    });
};


Yasound.Invitations.UI.InvitationGrid = Ext.extend(Ext.grid.GridPanel, {
	singleSelect: true,
	checkboxSelect: true,
	
    initComponent: function() {
        this.addEvents('invitationselected');
        this.pageSize = 25;
        this.store = Yasound.Invitations.Data.InvitationStore();
        this.store.pageSize = this.pageSize;
        
    	var sm = new Ext.grid.CheckboxSelectionModel({
            singleSelect: this.multipleSelection,
            listeners: {
                selectionchange: function(sm){
					Ext.each(sm.getSelections(), function(record) {
                        this.grid.fireEvent('invitationselected', this, record.data.id, record.data);							
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
            cm: new Ext.grid.ColumnModel(Yasound.Invitations.UI.InvitationColumnModel(this.checkboxSelect ? sm : null)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
        	plugins: [Yasound.Invitations.UI.InvitationFilters()]
        
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Invitations.UI.InvitationGrid.superclass.initComponent.apply(this, arguments);
    }
});
Ext.reg('invitationgrid', Yasound.Invitations.UI.InvitationGrid);
