//------------------------------------------
// Datastore
//------------------------------------------
Yasound.Invitations.Data.InvitationStore = function(url) {
	var fields = [
	  'id', 
	  'fullname', 
	  'email', 
	  'radio_id', 
	  'radio', {
		name: 'sent',
		type: 'date',
		dateFormat: 'Y-m-d H:i:s'
	  }, 
	  'user_profile',
	  'message',
	  'subject'
	];
	return new Yasound.Utils.SimpleStore(url, fields);
};

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Invitations.UI.InvitationColumnModel = function(sm, hideUser, hideSent) {
	var cm = [{
        header: gettext('Name'),
        dataIndex: 'fullname',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: 'textfield',
            filterName: 'fullname'
        }        	
    }, {
        header: gettext('Email'),
        dataIndex: 'email',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: 'textfield',
            filterName: 'email'
        }        	
    }, {
        header: gettext('Radio'),
        dataIndex: 'radio',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: 'textfield',
            filterName: 'radio'
        }        	
    }, {
        header: gettext('Associated user'),
        dataIndex: 'user_profile',
        hidden: hideUser,
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: 'textfield',
            filterName: 'user_profile'
        }        	
    }, {
        header: gettext('Sent at'),
        dataIndex: 'sent',
        hidden: hideSent,
        xtype: 'datecolumn',
        format: 'd/m/Y H:i:s',
        sortable: true,
        width: 50
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
	hideColumnUser: true,
	hideColumnSent: true,
	url: '/yabackoffice/invitations/',
	tbar:[],
	
    initComponent: function() {
        this.addEvents('selected');
        this.pageSize = 25;
        this.store = Yasound.Invitations.Data.InvitationStore(this.url);
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
            cm: new Ext.grid.ColumnModel(Yasound.Invitations.UI.InvitationColumnModel(this.checkboxSelect ? sm : null,
            		this.hideColumnUser, this.hideColumnSent)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
        	plugins: [Yasound.Invitations.UI.InvitationFilters(), new Ext.ux.grid.GridHeaderFilters()],
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
        Yasound.Invitations.UI.InvitationGrid.superclass.initComponent.apply(this, arguments);
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
Ext.reg('invitationgrid', Yasound.Invitations.UI.InvitationGrid);
