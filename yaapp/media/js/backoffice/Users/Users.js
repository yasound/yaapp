//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Users.Handler.DisableUsers = function (selected) {
    Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to disable the selected user(s)'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function (b, text) {
            if (b == 'yes') {
                ids = [];
                Ext.each(selected, function (record) {
                    ids.push(record.data.id);
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/users/'),
                    success: function (result, request) {
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('users-usergrid').getStore().reload();
                    },
                    failure: function (result, request) {
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        users_id: ids,
                        'action': 'disable'
                    }
                });
            }
        }
    });
};

Yasound.Users.Handler.FakeUsers = function (selected) {
    Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to mark the user(s) as fake ?'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function (b, text) {
            if (b == 'yes') {
                ids = [];
                Ext.each(selected, function (record) {
                    ids.push(record.data.id);
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/users/'),
                    success: function (result, request) {
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('users-usergrid').getStore().reload();
                    },
                    failure: function (result, request) {
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        users_id: ids,
                        'action': 'fake'
                    }
                });
            }
        }
    });
};

Yasound.Users.Handler.ExportUsers = function (selected) {
    ids = [];
    Ext.each(selected, function (record) {
        ids.push(record.data.id);
    });
    var maskingAjax = new Ext.data.Connection({});

    maskingAjax.request({
        disableCaching: true,
        url: String.format('/yabackoffice/users/'),
        form: Ext.fly('frmDummy'),
        params: {
            users_id: ids,
            'action': 'export'
        },
        method: 'POST',
        timeout: 1000 * 60 * 5,
        isUpload: true
    });
};

Yasound.Users.Handler.EnableHD = function (selected, enable_hd) {
    ids = [];
    Ext.each(selected, function (record) {
        ids.push(record.data.id);
    });
    if (enable_hd) {
        action = 'enable_hd';
    } else {
        action = 'disable_hd';
    }
    Ext.Ajax.request({
        url: String.format('/yabackoffice/users/'),
        success: function (result, request) {
            var data = result.responseText;
            var json = Ext.decode(data);
            Ext.getCmp('users-usergrid').getStore().reload();
        },
        failure: function (result, request) {
        },
        method: 'POST',
        timeout: 1000 * 60 * 5,
        params: {
            users_id: ids,
            'action': action
        }
    });

};

Yasound.Users.Handler.EnableUsers = function (selected) {
    Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to enable the selected user(s)'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function (b, text) {
            if (b == 'yes') {
                ids = [];
                Ext.each(selected, function (record) {
                    ids.push(record.data.id);
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/users/'),
                    success: function (result, request) {
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('users-usergrid').getStore().reload();
                    },
                    failure: function (result, request) {
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        users_id: ids,
                        'action': 'enable'
                    }
                });
            }
        }
    });
};
// ------------------------------------------
// UI
// ------------------------------------------
Yasound.Users.UI.UsersPanel = function () {
    return {
        xtype: 'panel',
        title: gettext('Users'),
        id: 'users-users-panel',
        layout: 'border',
        items: [ {
            xtype: 'usergrid',
            id: 'users-usergrid',
            singleSelect: false,
            title: gettext('Users'),
            checkboxSelect: false,
            region: 'center',
            tbar: [ {
                text: gettext('Enable'),
                disabled: true,
                ref: '../enableButton',
                iconCls: 'silk-accept',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Users.Handler.EnableUsers(selection);
                }
            }, {
                text: gettext('Disable'),
                disabled: true,
                ref: '../disableButton',
                iconCls: 'silk-delete',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Users.Handler.DisableUsers(selection);
                }
            }, {
                text: gettext('Report as fake user'),
                disabled: true,
                ref: '../fakeButton',
                iconCls: 'silk-delete',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Users.Handler.FakeUsers(selection);
                }
            }, '-', {
                text: gettext('Enable HD'),
                ref: '../enableHD',
                disabled: true,
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Users.Handler.EnableHD(selection, true);
                }
            }, {
                text: gettext('Disable HD'),
                ref: '../disableHD',
                disabled: true,
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Users.Handler.EnableHD(selection, false);
                }
            },'-', {
                text: gettext('Export selected users'),
                ref: '../exportSelectedButton',
                disabled: true,
                iconCls: 'silk-page-excel',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Users.Handler.ExportUsers(selection);
                }
            }, {
                text: gettext('Export all users'),
                ref: '../exportButton',
                iconCls: 'silk-page-copy',
                handler: function (b, e) {
                    Yasound.Users.Handler.ExportUsers([]);
                }
            } ],
            listeners: {
                'selected': function (grid, id, record) {
                    grid.disableButton.setDisabled(false);
                    grid.enableButton.setDisabled(false);
                    grid.fakeButton.setDisabled(false);
                    grid.exportSelectedButton.setDisabled(false);
                    grid.enableHD.setDisabled(false);
                    grid.disableHD.setDisabled(false);
                },
                'unselected': function (grid) {
                    grid.disableButton.setDisabled(true);
                    grid.enableButton.setDisabled(true);
                    grid.fakeButton.setDisabled(true);
                    grid.exportSelectedButton.setDisabled(true);
                    grid.enableHD.setDisabled(true);
                    grid.disableHD.setDisabled(true);
                }
            }
        } ],
        updateData: function (component) {
        }
    };
};