//------------------------------------------
// Datastore
//------------------------------------------
Yasound.Settings.Data.SettingsStore = function(url) {
	var fields = [
	  '_id', 
	  'name', 
	  'value'
	];
	var sortInfo = {
            field: 'name',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
    };

	return new Yasound.Utils.SimpleStore(url, fields, sortInfo, '_id');
};

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Settings.UI.SettingsColumnModel = function() {
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
        header: gettext('Value'),
        dataIndex: 'value',
        sortable: true,
        width: 60,
        filterable: true,
        filter: {
            xtype: 'textfield',
            filterName: 'value'
        }   ,
    	editable: true,
    	editor: new Ext.form.NumberField({
    										allowBlank: false,
    										allowDecimals: false,
    										allowNegative: false
    										})
    }];
    return cm;
};


Yasound.Settings.UI.SettingsGrid = Ext.extend(Ext.grid.EditorGridPanel, {
	url: '/yabackoffice/invitations/',
	tbar:[],
	
    initComponent: function() {
        this.store = Yasound.Settings.Data.SettingsStore(this.url);
        
    	var sm = new Ext.grid.RowSelectionModel({
            singleSelect: true
        });

        var config = {
            tbar:this.tbar,
            loadMask: true,
            sm: sm,
            cm: new Ext.grid.ColumnModel(Yasound.Settings.UI.SettingsColumnModel()),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
        	plugins: [new Ext.ux.grid.GridHeaderFilters()]
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Settings.UI.SettingsGrid.superclass.initComponent.apply(this, arguments);
    }
});
Ext.reg('settingsgrid', Yasound.Settings.UI.SettingsGrid);
