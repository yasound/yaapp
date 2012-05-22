//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

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
            title: gettext('Users'),
            region: 'center',
            listeners: {
                'selected': function (grid, id, record) {
                    var wallEventGrid = grid.nextSibling();
                    wallEventGrid.setParams({
                        'radio_id': id
                    })
                    wallEventGrid.reload();
                }
            }
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
                },
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