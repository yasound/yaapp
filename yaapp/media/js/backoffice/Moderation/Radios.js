//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Moderation.Handler.BlacklistRadio = function(radioId) {
    Ext.Ajax.request({
        url: String.format('/yabackoffice/radios/{0}/blacklist/', radioId),
        success: function(result, request){
            Ext.getCmp('moderation-radiogrid').getStore().reload();
        },
        failure: function(result, request){
        },
        method: 'POST',
        timeout: 1000 * 60 * 5
    });
};

Yasound.Moderation.Handler.UnblacklistRadio = function(radioId) {
    Ext.Ajax.request({
        url: String.format('/yabackoffice/radios/{0}/unblacklist/', radioId),
        success: function(result, request){
            Ext.getCmp('moderation-radiogrid').getStore().reload();
        },
        failure: function(result, request){
        },
        method: 'POST',
        timeout: 1000 * 60 * 5
    });
};

//------------------------------------------
// UI
//------------------------------------------

Yasound.Moderation.UI.RadiosPanel = function () {
    return {
        xtype: 'panel',
        title: gettext('Radios'),
        id: 'moderation-radios-panel',
        layout: 'border',
        items: [ {
            xtype: 'radiogrid',
            checkboxSelect: false,
            title: gettext('Radios'),
            id: 'moderation-radiogrid',
            region: 'center',
            listeners: {
                'selected': function (grid, id, record) {
                    var wallEventGrid = grid.nextSibling();
                    wallEventGrid.setParams({
                        'radio_id': id
                    });
                    wallEventGrid.reload();
                    grid.blacklistButton.setDisabled(false);
                    grid.unblacklistButton.setDisabled(false);
                },
                'unselected': function(grid) {
                    grid.blacklistButton.setDisabled(true);
                    grid.unblacklistButton.setDisabled(true);
                }
            },
            tbar: [{
                text: gettext('Blacklist'),
                disabled: true,
                ref: '../blacklistButton',
                iconCls: 'silk-lock',
                handler: function(b, e) {
                       Ext.Msg.show({
                            title: gettext('Confirmation'),
                            msg: gettext('Do you want to blacklist this radio ?'),
                            buttons: Ext.Msg.YESNOCANCEL,
                            fn: function(bt, text){
                                if (bt == 'yes') {
                                    var grid = b.ownerCt.ownerCt;
                                    selection = grid.getSelectionModel().getSelections();
                                    Ext.each(selection, function(record) {
                                        Yasound.Moderation.Handler.BlacklistRadio(record.data.id);
                                    });
                                }
                            }
                       });
                }
            }, {
                text: gettext('Unblacklist'),
                disabled: true,
                ref: '../unblacklistButton',
                iconCls: 'silk-lock-open',
                handler: function(b, e) {
                       Ext.Msg.show({
                            title: gettext('Confirmation'),
                            msg: gettext('Do you want to un-blacklist this radio ?'),
                            buttons: Ext.Msg.YESNOCANCEL,
                            fn: function(bt, text){
                                if (bt == 'yes') {
                                    var grid = b.ownerCt.ownerCt;
                                    selection = grid.getSelectionModel().getSelections();
                                    Ext.each(selection, function(record) {
                                        Yasound.Moderation.Handler.UnblacklistRadio(record.data.id);
                                    });
                                }
                            }
                       });
                }
            }]
        }, {
            xtype: 'walleventgrid',
            region: 'east',
            title: gettext('Comments'),
            width: 600,
            split: true,
            tbar: [ {
                text: gettext('Delete'),
                disabled: true,
                ref: '../deleteButton',
                iconCls: 'silk-delete',
                handler: function (b, e) {
                    Ext.Msg.show({
                        title: gettext('Confirmation'),
                        msg: gettext('Do you want to delete this comment ?'),
                        buttons: Ext.Msg.YESNOCANCEL,
                        fn: function (bt, text) {
                            if (bt == 'yes') {
                                var grid = b.ownerCt.ownerCt;
                                selection = grid.getSelectionModel().getSelections();
                                Ext.each(selection, function (record) {
                                    grid.store.remove(record);
                                });
                            }
                        }
                    });
                }
            } ],
            listeners: {
                'selected': function (grid, id, record) {
                    grid.deleteButton.setDisabled(false);
                },
                'unselected': function (grid) {
                    grid.deleteButton.setDisabled(true);
                }
            }
        } ],
        updateData: function (component) {
        }
    };
};