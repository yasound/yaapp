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
                        success();
                        win.close();
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
                        success();
                        win.close();
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
                        success();
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


Yasound.Geoperm.UI.Panel = function() {
    return {
        xtype : 'panel',
        title : gettext('Geo permissions'),
        id : 'geoperm-panel',
        layout:'border',
        items:[{
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

        }, {
            xtype: 'geofeaturegrid',
            title: gettext('Features'),
            region: 'east',
            split: true,
            width:400
        }],
        updateData : function(component) {
        }
    };
};
