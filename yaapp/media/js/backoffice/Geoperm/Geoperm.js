//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Geoperm.Handler.AddCountry = function (success) {
    var form = Ext.ComponentMgr.create(Yasound.Geoperm.UI.CountryForm());
    var win = new Ext.Window({
        title: gettext('Create a country'),
        width: 380,
        autoHeight: true,
        layout: 'form',
        autoScroll: true,
        modal: true,
        preventBodyReset: true,
        items: [form],
        draggable: true,
        buttonAlign: 'center',
        buttons: [{
            text: gettext('Submit'),
            handler: function(){
                if (!form.getForm().isValid()) {
                    return;
                }
                var values = form.getForm().getFieldValues();
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/geoperm/countries/'),
                    success: function(result, request){
                        var res = Ext.decode(result.responseText);
                        if (res.success) {
                            success();
                            win.close();
                        } else {
                            alert(res.message);
                        }
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    params: values
                });
            }
        }]

    });
    win.on('show', function(){
        win.center();
    });
    win.show(this);
};

Yasound.Geoperm.Handler.EditCountry = function (record, success) {
    var form = Ext.ComponentMgr.create(Yasound.Geoperm.UI.CountryForm(record));
    var win = new Ext.Window({
        title: gettext('Edit country'),
        width: 380,
        autoHeight: true,
        layout: 'form',
        autoScroll: true,
        modal: true,
        preventBodyReset: true,
        items: [form],
        draggable: true,
        buttonAlign: 'center',
        buttons: [{
            text: gettext('Submit'),
            handler: function(){
                if (!form.getForm().isValid()) {
                    return;
                }
                var values = form.getForm().getFieldValues();
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/geoperm/countries/{0}/', record.data.id),
                    success: function(result, request){
                        var res = Ext.decode(result.responseText);
                        if (res.success) {
                            success();
                            win.close();
                        } else {
                            alert(res.message);
                        }
                    },
                    failure: function(result, request){
                    },
                    method: 'PUT',
                    params: values
                });
            }
        }]

    });
    win.on('show', function(){
        win.center();
    });
    win.show(this);
};

Yasound.Geoperm.Handler.DeleteCountry = function(records, success) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to delete the country ?'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
                ids = [];
                Ext.each(records, function(record) {
                    ids.push(record.data.id);
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/geoperm/countries/'),
                    success: function(result, request){
                        var res = Ext.decode(result.responseText);
                        if (res.success) {
                            success();
                        } else {
                            alert(res.message);
                        }
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        country_id: ids,
                        'action': 'delete'
                    }
                });
            }
        }
   });
};


Yasound.Geoperm.Handler.AddFeature = function (country_id, success) {
    var form = Ext.ComponentMgr.create(Yasound.Geoperm.UI.FeatureForm());
    var win = new Ext.Window({
        title: gettext('Add a feature'),
        width: 380,
        autoHeight: true,
        layout: 'form',
        autoScroll: true,
        modal: true,
        preventBodyReset: true,
        items: [form],
        draggable: true,
        buttonAlign: 'center',
        buttons: [{
            text: gettext('Submit'),
            handler: function(){
                if (!form.getForm().isValid()) {
                    return;
                }
                var values = form.getForm().getFieldValues();
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/geoperm/countries/{0}/features/', country_id),
                    success: function(result, request){
                        var res = Ext.decode(result.responseText);
                        if (res.success) {
                            success();
                            win.close();
                        } else {
                            alert(res.message);
                        }
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    params: values
                });
            }
        }]

    });
    win.on('show', function(){
        win.center();
    });
    win.show(this);
};

Yasound.Geoperm.Handler.EditFeature = function (record, success) {
    var form = Ext.ComponentMgr.create(Yasound.Geoperm.UI.FeatureForm(record));
    var win = new Ext.Window({
        title: gettext('Edit feature'),
        width: 380,
        autoHeight: true,
        layout: 'form',
        autoScroll: true,
        modal: true,
        preventBodyReset: true,
        items: [form],
        draggable: true,
        buttonAlign: 'center',
        buttons: [{
            text: gettext('Submit'),
            handler: function(){
                if (!form.getForm().isValid()) {
                    return;
                }
                var values = form.getForm().getFieldValues();
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/geoperm/countries/{0}/features/{1}/', record.data.country_id, record.data.id),
                    success: function(result, request){
                        var res = Ext.decode(result.responseText);
                        if (res.success) {
                            success();
                            win.close();
                        } else {
                            alert(res.message);
                        }
                    },
                    failure: function(result, request){
                    },
                    method: 'PUT',
                    params: values
                });
            }
        }]

    });
    win.on('show', function(){
        win.center();
    });
    win.show(this);
};

Yasound.Geoperm.Handler.DeleteFeature = function(records, success) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to delete the feature ?'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
                ids = [];
                var country_id;
                Ext.each(records, function(record) {
                    ids.push(record.data.id);
                    country_id = record.data.country_id;
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/geoperm/countries/{0}/features/', country_id),
                    success: function(result, request){
                        var res = Ext.decode(result.responseText);
                        if (res.success) {
                            success();
                        } else {
                            alert(res.message);
                        }
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        geofeature_id: ids,
                        country_id: country_id,
                        'action': 'delete'
                    }
                });
            }
        }
   });
};
//------------------------------------------
// UI
//------------------------------------------
Yasound.Geoperm.UI.CountryForm = function(record) {
    if (!record) {
        record = {
            data: {
                name: '',
                code: ''
            }
        };
    }
    return {
        xtype: 'form',
        bodyStyle:'padding:5px 5px 0',
        items: [{
                fieldLabel: gettext('Code'),
                xtype: 'textfield',
                name: 'code',
                value: record.data.code,
                allowBlank:false
        }, {
                fieldLabel: gettext('Name'),
                xtype: 'textfield',
                name: 'name',
                value: record.data.name,
                allowBlank:false
        }]
    };
};


Yasound.Geoperm.UI.FeatureForm = function(record) {
    if (!record) {
        record = {
            data: {
                feature: 0
            }
        };
    }
    return {
        xtype: 'form',
        bodyStyle:'padding:5px 5px 0',
        items: [{
            xtype: 'combo',
            allowBlank:false,
            fieldLabel: gettext('Feature'),
            hiddenName:'feature',
            store: new Ext.data.ArrayStore({
                fields: ['id', 'label'],
                data : [
                    [0, gettext('Login')],
                    [1, gettext('Create radio')]
                ]
            }),
            valueField:'id',
            displayField:'label',
            value: record.data.feature,
            typeAhead: true,
            mode: 'local',
            triggerAction: 'all',
            emptyText: gettext('Select a feature...'),
            selectOnFocus:true
        }]
    };
};

Yasound.Geoperm.UI.Panel = function() {
    var countryGrid = Ext.ComponentMgr.create({
        xtype: 'countrygrid',
        title: gettext('Countries'),
        region: 'center',
        tbar: [{
            iconCls: 'silk-add',
            text: gettext('Create new country'),
            handler: function (b, e) {
                var grid = b.ownerCt.ownerCt;
                Yasound.Geoperm.Handler.AddCountry(function () {
                    grid.getStore().reload();
                });
            }
        }, {
            iconCls: 'silk-application-edit',
            text: gettext('Edit'),
            ref: '../editButton',
            disabled: true,
            handler: function (b, e) {
                var grid = b.ownerCt.ownerCt;
                selection = grid.getSelectionModel().getSelected();
                Yasound.Geoperm.Handler.EditCountry(selection, function () {
                    grid.getStore().reload();
                });
            }
        }, {
            text: gettext('Delete'),
            iconCls: 'silk-application-delete',
            ref: '../deleteButton',
            disabled: true,
            handler: function (b, e) {
                var grid = b.ownerCt.ownerCt;
                selection = grid.getSelectionModel().getSelections();

                Yasound.Geoperm.Handler.DeleteCountry(selection, function () {
                    grid.getStore().reload();
                });
            }
        }],
        listeners: {
            'selected': function (grid, id, record) {
                grid.editButton.setDisabled(false);
                grid.deleteButton.setDisabled(false);
            },
            'unselected': function (grid) {
                grid.editButton.setDisabled(true);
                grid.deleteButton.setDisabled(true);
            }
        }
    });

    var featureGrid = Ext.ComponentMgr.create({
        xtype: 'geofeaturegrid',
        disabled: true,
        title: gettext('Features'),
        region: 'east',
        split: true,
        width:600,
        tbar: [{
            iconCls: 'silk-add',
            text: gettext('Add feature'),
            handler: function (b, e) {
                var grid = b.ownerCt.ownerCt;
                Yasound.Geoperm.Handler.AddFeature(grid.countryId, function () {
                    grid.getStore().reload();
                });
            }
        }, {
            iconCls: 'silk-application-edit',
            text: gettext('Edit'),
            ref: '../editButton',
            disabled: true,
            handler: function (b, e) {
                var grid = b.ownerCt.ownerCt;
                selection = grid.getSelectionModel().getSelected();
                Yasound.Geoperm.Handler.EditFeature(selection, function () {
                    grid.getStore().reload();
                });
            }
        }, {
            text: gettext('Delete'),
            iconCls: 'silk-application-delete',
            ref: '../deleteButton',
            disabled: true,
            handler: function (b, e) {
                var grid = b.ownerCt.ownerCt;
                selection = grid.getSelectionModel().getSelections();

                Yasound.Geoperm.Handler.DeleteFeature(selection, function () {
                    grid.getStore().reload();
                });
            }
        }],
        listeners: {
            'selected': function (grid, id, record) {
                grid.editButton.setDisabled(false);
                grid.deleteButton.setDisabled(false);
            },
            'unselected': function (grid) {
                grid.editButton.setDisabled(true);
                grid.deleteButton.setDisabled(true);
            }
        },
        updateData: function(grid, countryId) {
            grid.setDisabled(false);
            grid.setCountryId(countryId);
        }
    });

    countryGrid.on('selected', function (grid, id, record) {
        featureGrid.updateData(featureGrid, id);
    });

    return {
        xtype : 'panel',
        title : gettext('Geo permissions'),
        id : 'geoperm-panel',
        layout:'border',
        items:[countryGrid, featureGrid],
        updateData : function(component) {
        }
    };
};
