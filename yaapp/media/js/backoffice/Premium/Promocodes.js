//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Premium.Handler.GenerateUniqueCodes = function (success) {
    var form = Ext.ComponentMgr.create(Yasound.Premium.UI.UniquePromocodesForm());
    var win = new Ext.Window({
        title: gettext('Promocode generator'),
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
                    url: String.format('/yabackoffice/premium/unique_promocodes/'),
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

Yasound.Premium.Handler.CreateNonUniqueCode = function (success) {
    var form = Ext.ComponentMgr.create(Yasound.Premium.UI.NonUniquePromocodeForm());
    var win = new Ext.Window({
        title: gettext('Promocode generator'),
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
                    url: String.format('/yabackoffice/premium/non_unique_promocodes/'),
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


Yasound.Premium.Handler.EditPromocode = function (record, success) {
    var form = Ext.ComponentMgr.create(Yasound.Premium.UI.EditPromocodeForm(record));
    var win = new Ext.Window({
        title: gettext('Promocode'),
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
                    url: String.format('/yabackoffice/premium/promocodes/{0}/', record.data.id),
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

Yasound.Premium.Handler.DeletePromocode = function(records, success) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to delete the code(s) ?'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
                ids = [];
                Ext.each(records, function(record) {
                    ids.push(record.data.id);
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/premium/promocodes/'),
                    success: function(result, request){
                        success();
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        promocode_id: ids,
                        'action': 'delete'
                    }
                });
            }
        }
   });
};


Yasound.Premium.Handler.ExportPromocode = function(records, success) {
    ids = [];
    Ext.each(records, function(record) {
        ids.push(record.data.id);
    });
    var maskingAjax = new Ext.data.Connection({});

    maskingAjax.request({
        disableCaching: true,
        url: String.format('/yabackoffice/premium/promocodes/'),
        form: Ext.fly('frmDummy'),
        params: {
            promocode_id: ids,
            'action': 'export'
        },
        method: 'POST',
        timeout: 1000 * 60 * 5,
        isUpload: true
    });
};

//------------------------------------------
// UI
//------------------------------------------
Yasound.Premium.UI.ServiceCombo = function (value) {
    return {
        xtype: 'combo',
        allowBlank:false,
        fieldLabel: 'Service',
        hiddenName:'service_id',
        store: new Ext.data.ArrayStore({
            fields: ['id', 'label'],
            data : [[1, 'HD']]
        }),
        valueField:'id',
        displayField:'label',
        value: value,
        typeAhead: true,
        mode: 'local',
        triggerAction: 'all',
        emptyText: gettext('Select a service...'),
        selectOnFocus:true
    };
};

Yasound.Premium.UI.UniquePromocodesForm = function() {
    return {
        xtype: 'form',
        bodyStyle:'padding:5px 5px 0',
        items: [Yasound.Premium.UI.ServiceCombo(), {
                fieldLabel: gettext('Service duration (months)'),
                xtype: 'numberfield',
                name: 'duration',
                value: 1
        }, {
                fieldLabel: gettext('Prefix'),
                xtype: 'textfield',
                name: 'prefix',
                value: 'YA-',
                allowBlank:false
            },{
                fieldLabel: gettext('Quantity'),
                xtype: 'numberfield',
                name: 'count',
                value: 50
            }
        ]
    };
};
Yasound.Premium.UI.NonUniquePromocodeForm = function() {
    return {
        xtype: 'form',
        bodyStyle:'padding:5px 5px 0',
        items: [Yasound.Premium.UI.ServiceCombo(), {
                fieldLabel: gettext('Service Duration (months)'),
                xtype: 'numberfield',
                name: 'duration',
                allowBlank:false,
                value: 1
        }, {
                fieldLabel: gettext('Code'),
                xtype: 'textfield',
                name: 'code',
                allowBlank:false
            }
        ]
    };
};

Yasound.Premium.UI.EditPromocodeForm = function(record) {
    return {
        xtype: 'form',
        bodyStyle:'padding:5px 5px 0',
        items: [Yasound.Premium.UI.ServiceCombo(record.data.service_id), {
                fieldLabel: gettext('Service duration (months)'),
                xtype: 'numberfield',
                name: 'duration',
                value: record.data.duration
        }, {
                fieldLabel: gettext('Code'),
                xtype: 'textfield',
                name: 'code',
                value: record.data.code,
                allowBlank:false
            }, {
                fieldLabel: gettext('Enabled'),
                xtype: 'checkbox',
                name: 'enabled',
                checked: record.data.enabled
            }
        ]
    };
};
Yasound.Premium.UI.PromocodesPanel = function() {
    return {
        xtype : 'panel',
        title : gettext('Promocodes'),
        id : 'promocodes-panel',
        layout:'border',
        items:[{
            xtype: 'promocodegrid',
            title: gettext('Permanent codes'),
            singleSelect: false,
            url: '/yabackoffice/premium/non_unique_promocodes/',
            region: 'center',
            tbar: [{
                text: gettext('Create code'),
                iconCls: 'silk-table-add',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    Yasound.Premium.Handler.CreateNonUniqueCode(function () {
                        grid.getStore().reload();
                    });
                }
            }, {
                text: gettext('Edit'),
                iconCls: 'silk-table-edit',
                ref: '../editButton',
                disabled: true,
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelected();

                    Yasound.Premium.Handler.EditPromocode(selection, function () {
                        grid.getStore().reload();
                    });
                }
            }, {
                text: gettext('Delete'),
                iconCls: 'silk-table-delete',
                ref: '../deleteButton',
                disabled: true,
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();

                    Yasound.Premium.Handler.DeletePromocode(selection, function () {
                        grid.getStore().reload();
                    });
                }
            }, '-', {
                text: gettext('Export'),
                iconCls: 'silk-page-excel',
                ref: '../exportButton',
                disabled: true,
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();

                    Yasound.Premium.Handler.ExportPromocode(selection, function () {
                        grid.getStore().reload();
                    });
                }
            }],
            listeners: {
                'selected': function (grid, id, record) {
                    grid.editButton.setDisabled(false);
                    grid.deleteButton.setDisabled(false);
                    grid.exportButton.setDisabled(false);
                },
                'unselected': function (grid) {
                    grid.editButton.setDisabled(true);
                    grid.deleteButton.setDisabled(true);
                    grid.exportButton.setDisabled(true);
                }
            }
        }, {
            xtype: 'promocodegrid',
            title: gettext('Unique usage codes'),
            singleSelect: false,
            url: '/yabackoffice/premium/unique_promocodes/',
            region: 'west',
            width: 400,
            split: true,
            tbar: [{
                text: gettext('Generate codes'),
                iconCls: 'silk-table-add',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    Yasound.Premium.Handler.GenerateUniqueCodes(function () {
                        grid.getStore().reload();
                    });
                }
            }, {
                text: gettext('Edit'),
                iconCls: 'silk-table-edit',
                ref: '../editButton',
                disabled: true,
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();

                    Yasound.Premium.Handler.EditPromocode(selection, function () {
                        grid.getStore().reload();
                    });
                }
            }, {
                text: gettext('Delete'),
                iconCls: 'silk-table-delete',
                ref: '../deleteButton',
                disabled: true,
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();

                    Yasound.Premium.Handler.DeletePromocode(selection, function () {
                        grid.getStore().reload();
                    });
                }
            }, '-', {
                text: gettext('Export'),
                iconCls: 'silk-page-excel',
                ref: '../exportButton',
                disabled: true,
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();

                    Yasound.Premium.Handler.ExportPromocode(selection, function () {
                        grid.getStore().reload();
                    });
                }
            }],
            listeners: {
                'selected': function (grid, id, record) {
                    grid.editButton.setDisabled(false);
                    grid.deleteButton.setDisabled(false);
                    grid.exportButton.setDisabled(false);
                },
                'unselected': function (grid) {
                    grid.editButton.setDisabled(true);
                    grid.deleteButton.setDisabled(true);
                    grid.exportButton.setDisabled(true);
                }
            }
        }],
        updateData : function(component) {
        }
    };
};
