
//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Radios.Handler.RemoveSong = function(radioId, selected) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to remove songs from radio'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
                ids = [];
                Ext.each(selected, function(record) {
                    ids.push(record.data.id);
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/radios/{0}/remove_songs/', radioId),
                    success: function(result, request){
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('radios-songgrid').getStore().reload();
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        song_instance_id: ids
                    }
                });
            }
        }
   });
};

Yasound.Radios.Handler.DuplicateRadio = function(radioId) {
    Ext.Msg.show({
         title: gettext('Confirmation'),
         msg: gettext('Do you want to duplicate this radio ?'),
         buttons: Ext.Msg.YESNOCANCEL,
         fn: function(b, text){
             if (b == 'yes') {
                 ids = [];
                 Ext.Ajax.request({
                     url: String.format('/yabackoffice/radios/{0}/duplicate/', radioId),
                     success: function(result, request){
                         Ext.getCmp('radios-radiogrid').getStore().reload();
                     },
                     failure: function(result, request){
                     },
                     method: 'POST',
                     timeout: 1000 * 60 * 5
                 });
             }
         }
    });
 };

Yasound.Radios.Handler.BlacklistRadio = function(radioId) {
    Ext.Ajax.request({
        url: String.format('/yabackoffice/radios/{0}/blacklist/', radioId),
        success: function(result, request){
            Ext.getCmp('radios-radiogrid').getStore().reload();
        },
        failure: function(result, request){
        },
        method: 'POST',
        timeout: 1000 * 60 * 5
    });
};

Yasound.Radios.Handler.UnblacklistRadio = function(radioId) {
    Ext.Ajax.request({
        url: String.format('/yabackoffice/radios/{0}/unblacklist/', radioId),
        success: function(result, request){
            Ext.getCmp('radios-radiogrid').getStore().reload();
        },
        failure: function(result, request){
        },
        method: 'POST',
        timeout: 1000 * 60 * 5
    });
};

Yasound.Radios.Handler.RemoveAllSongs = function(radioId) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to remove all songs from radio'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/radios/{0}/remove_all_songs/', radioId),
                    success: function(result, request){
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('radios-songgrid').getStore().reload();
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5
                });
            }
        }
   });
};

Yasound.Radios.Handler.RemoveDuplicateSongs = function(radioId) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to find and remove duplicates from radio'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/radios/{0}/remove_duplicate_songs/', radioId),
                    success: function(result, request){
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('radios-songgrid').getStore().reload();
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5
                });
            }
        }
   });
};

Yasound.Radios.Handler.AddToRadio = function(radioId, selected) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to add songs to radio'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
                ids = [];
                Ext.each(selected, function(record) {
                    ids.push(record.data.id);
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/radios/{0}/add_songs/', radioId),
                    success: function(result, request){
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('radios-songgrid').getStore().reload();
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    timeout: 1000 * 60 * 5,
                    params: {
                        yasound_song_id: ids
                    }
                });
            }
        }
   });
};

Yasound.Radios.Handler.FindMetadata = function(selected) {
    ids = [];
    Ext.each(selected, function(record) {
        ids.push(record.data.id);
    });

    var acceptMetadatas = function(ids) {
        Ext.Ajax.request({
            url: String.format('/yabackoffice/yasound_songs/replace_metadata/'),
            method: 'POST',
            timeout: 1000 * 60 * 5,
            params: {
                yasound_song_id: ids
            }
        });
    };

    Ext.Ajax.request({
        url: String.format('/yabackoffice/yasound_songs/find_metadata/'),
        success: function(result, request){
            var data = result.responseText;
            var json = Ext.decode(data);
            var metadatas = json.data;
            Ext.Msg.show({
                title: gettext('The following metadata have been found, use it ?'),
                msg: gettext(metadatas),
                buttons: Ext.Msg.YESNOCANCEL,
                fn: function(b, text){
                    acceptMetadatas(ids);
                }
            });
        },
        failure: function(result, request){
        },
        method: 'POST',
        timeout: 1000 * 60 * 5,
        params: {
            yasound_song_id: ids
        }
    });
};

Yasound.Radios.UI.RadiosPanel = function() {
    var songGrid = Ext.ComponentMgr.create({
        xtype: 'songinstancegrid',
        id:'radios-songgrid',
        region: 'center',
        url: '/yabackoffice/radios/{0}/songs/',
        radio_id: 0,
        title: gettext('Songs assigned to radio'),
        tbar:[{
            text: gettext('Remove from radio'),
            disabled: true,
            iconCls: 'silk-delete',
            ref:'../removeButton',
            handler: function(b, e) {
                var grid = b.ownerCt.ownerCt;
                var selected = grid.getSelectionModel().getSelections();
                Yasound.Radios.Handler.RemoveSong(grid.radioId, selected);
            }
        }, {
            text: gettext('Remove all songs from radio'),
            disabled: false,
            iconCls: 'silk-delete',
            ref:'../removeAllButton',
            handler: function(b, e) {
                var grid = b.ownerCt.ownerCt;
                Yasound.Radios.Handler.RemoveAllSongs(grid.radioId);
            }
        }, {
            text: gettext('Remove duplicate songs from radio'),
            disabled: false,
            iconCls: 'silk-delete',
            ref:'../removeDuplicateButton',
            handler: function(b, e) {
                var grid = b.ownerCt.ownerCt;
                Yasound.Radios.Handler.RemoveDuplicateSongs(grid.radioId);
            }
        }
        ],
        listeners: {
            'selected': function(grid, id, record) {
                grid.removeButton.setDisabled(false);
            },
            'deselected': function(grid) {
                grid.removeButton.setDisabled(true);
            }
        }
    });

    var radioForm = Ext.ComponentMgr.create({
        xtype:'radioform',
        region:'south',
        disabled: true,
        split: true,
        width:350,
        height:300,
        listeners: {
            uploadSuccess: function(fp, message) {
                songGrid.getStore().reload();
                Ext.getCmp('radios-radiogrid').getStore().reload();
                Yasound.Utils.DisplayLogWindow(message);
            },
            uploadFailure: function(fp, message) {
                songGrid.getStore().reload();
                Ext.getCmp('radios-radiogrid').getStore().reload();
                Yasound.Utils.DisplayLogWindow(message);
            }
        }
    });

    var radioGrid = Ext.ComponentMgr.create({
        xtype:'radiogrid',
        id:'radios-radiogrid',
        region: 'center',
        width: 500,
        tbar:[{
            text: gettext('Create new radio'),
            iconCls: 'silk-add',
            handler: function(b, e) {
               Ext.Msg.show({
                    title: gettext('Confirmation'),
                    msg: gettext('Do you want to create new radio ?'),
                    buttons: Ext.Msg.YESNOCANCEL,
                    fn: function(bt, text){
                        if (bt == 'yes') {
                            var grid = b.ownerCt.ownerCt;
                            var store = grid.getStore();
                            var u = new store.recordType({
                                name: gettext('New radio')
                            });
                            grid.store.insert(0, u);
                        }
                    }
               });
            }
        }, {
            text: gettext('Duplicate'),
            disabled: true,
            ref: '../duplicateButton',
            iconCls: 'silk-page-copy',
            handler: function(b, e) {
                var grid = b.ownerCt.ownerCt;
                var record = grid.getSelectionModel().getSelected();
                Yasound.Radios.Handler.DuplicateRadio(record.data.id);
            }
        },{
            text: gettext('Delete'),
            disabled: true,
            ref: '../deleteButton',
            iconCls: 'silk-delete',
            handler: function(b, e) {
                   Ext.Msg.show({
                        title: gettext('Confirmation'),
                        msg: gettext('Do you want to delete radio ?'),
                        buttons: Ext.Msg.YESNOCANCEL,
                        fn: function(bt, text){
                            if (bt == 'yes') {
                                var grid = b.ownerCt.ownerCt;
                                selection = grid.getSelectionModel().getSelections();
                                Ext.each(selection, function(record) {
                                    grid.store.remove(record);
                                });
                            }
                        }
                   });
            }
        }, {
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
                                    Yasound.Radios.Handler.BlacklistRadio(record.data.id);
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
                                    Yasound.Radios.Handler.UnblacklistRadio(record.data.id);
                                });
                            }
                        }
                   });
            }
        }],
        singleSelect: true,
        checkboxSelect: false,
        listeners: {
            'selected': function(grid, id, record) {
                songGrid.refresh(id);
                radioForm.updateForm(record);
                radioForm.setDisabled(false);
                grid.deleteButton.setDisabled(false);
                grid.duplicateButton.setDisabled(false);
                grid.blacklistButton.setDisabled(false);
                grid.unblacklistButton.setDisabled(false);
            },
            'unselected': function(grid) {
                grid.deleteButton.setDisabled(true);
                grid.blacklistButton.setDisabled(true);
                grid.unblacklistButton.setDisabled(true);
                grid.duplicateButton.setDisabled(true);
            }
        }
    });

    var yasoundSongGrid = Ext.ComponentMgr.create({
        xtype: 'yasoundsonggrid',
        region:'north',
        collapsible: true,
        collapsed: false,
        id: 'radios-yasoundsonggrid',
        title: gettext('Available songs'),
        split: true,
        height:350,
        tbar: [{
            text:gettext('Add to radio'),
            disabled: true,
            ref: '../addToRadioButton',
            handler: function(b, e) {
                var radioId = songGrid.radioId;
                var grid = b.ownerCt.ownerCt;
                var selected = grid.getSelectionModel().getSelections();
                Yasound.Radios.Handler.AddToRadio(radioId, selected);
            }
        }, {
            text:gettext('Find metadata'),
            disabled: true,
            ref: '../findMetadataButton',
            handler: function(b, e) {
                var grid = b.ownerCt.ownerCt;
                var selected = grid.getSelectionModel().getSelections();
                Yasound.Radios.Handler.FindMetadata(selected);
            }
        }],
        listeners: {
            'selected': function(grid, id, record) {
                grid.addToRadioButton.setDisabled(false);
                grid.findMetadataButton.setDisabled(false);
            },
            'unselected': function(grid) {
                grid.addToRadioButton.setDisabled(true);
                grid.findMetadataButton.setDisabled(true);
            }
        }
    });


    return {
        xtype : 'panel',
        title : gettext('Programming'),
        id : 'radios-panel',
        layout : 'border',
        items : [ {
            layout: 'border',
            region: 'west',
            collapsible: true,
            title: gettext('Radios'),
            width: 500,
            split: true,
            items:[radioGrid, radioForm]
        }, {
            region: 'center',
            layout: 'border',
            items:[songGrid, yasoundSongGrid]
        }],
        updateData : function(component) {
            radioGrid.getStore().reload();
        }
    };
};