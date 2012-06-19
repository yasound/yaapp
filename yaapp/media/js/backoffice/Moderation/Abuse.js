//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Moderation.Handler.DeleteNotification = function (selected) {
    Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to delete permanently the message ?'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function (b, text) {
            if (b == 'yes') {
                ids = [];
                Ext.each(selected, function (record) {
                    ids.push(record.get('_id'));
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/abuse/delete/'),
                    success: function (result, request) {
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('abuse-grid').getStore().reload();
                    },
                    failure: function (result, request) {
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        notifications: ids,
                    }
                });
            }
        }
    });
};

Yasound.Moderation.Handler.IgnoreNotification = function (selected) {
    Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to ignore permanently the notification ?'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function (b, text) {
            if (b == 'yes') {
                ids = [];
                Ext.each(selected, function (record) {
                    ids.push(record.get('_id'));
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/abuse/ignore/'),
                    success: function (result, request) {
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('abuse-grid').getStore().reload();
                    },
                    failure: function (result, request) {
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        notifications: ids,
                    }
                });
            }
        }
    });
};
//------------------------------------------
// UI
//------------------------------------------
Yasound.Moderation.UI.AbusePanel = function () {
    return {
        xtype: 'panel',
        title: gettext('Abuse notifications'),
        id: 'abuse-panel',
        layout: 'border',
        items: [ {
            xtype: 'abusegrid',
            title: gettext('Abuse notifications'),
            checkboxSelect: false,
            id: 'abuse-grid',
            region: 'center',
            tbar:[{
                text:gettext('Delete notification and message'),
                ref: '../deleteButton',
                iconCls: 'silk-delete',
                disabled: true,
                handler: function(b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Moderation.Handler.DeleteNotification(selection);
                }
            }, {
                text:gettext('Ignore notification'),
                ref: '../ignoreButton',
                iconCls: 'silk-user-comment',
                disabled: true,
                handler: function(b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Moderation.Handler.IgnoreNotification(selection);
                }
            }],
            listeners: {
                'selected': function (grid, id, record) {
                    grid.deleteButton.setDisabled(false);
                    grid.ignoreButton.setDisabled(false);
                },
                'unselected': function (grid) {
                    grid.deleteButton.setDisabled(true);
                    grid.ignoreButton.setDisabled(true);
                }
            }
        }],
        updateData: function (component) {
        }
    };
};