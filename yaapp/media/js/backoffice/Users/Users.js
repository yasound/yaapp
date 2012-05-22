//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Users.Handler.DisableUsers = function(selected) {
   Ext.Msg.show({
        title: gettext('Confirmation'),
        msg: gettext('Do you want to disable the selected user(s)'),
        buttons: Ext.Msg.YESNOCANCEL,
        fn: function(b, text){
            if (b == 'yes') {
                ids = [];
                Ext.each(selected, function(record) {
                    ids.push(record.data.id);
                });
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/users/'),
                    success: function(result, request){
                        var data = result.responseText;
                        var json = Ext.decode(data);
                        Ext.getCmp('users-usergrid').getStore().reload();
                    },
                    failure: function(result, request){
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

Yasound.Users.Handler.FakeUsers = function(selected) {
    Ext.Msg.show({
         title: gettext('Confirmation'),
         msg: gettext('Do you want to mark the user(s) as fake ?'),
         buttons: Ext.Msg.YESNOCANCEL,
         fn: function(b, text){
             if (b == 'yes') {
                 ids = [];
                 Ext.each(selected, function(record) {
                     ids.push(record.data.id);
                 });
                 Ext.Ajax.request({
                     url: String.format('/yabackoffice/users/'),
                     success: function(result, request){
                         var data = result.responseText;
                         var json = Ext.decode(data);
                         Ext.getCmp('users-usergrid').getStore().reload();
                     },
                     failure: function(result, request){
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
Yasound.Users.Handler.EnableUsers = function(selected) {
    Ext.Msg.show({
         title: gettext('Confirmation'),
         msg: gettext('Do you want to enable the selected user(s)'),
         buttons: Ext.Msg.YESNOCANCEL,
         fn: function(b, text){
             if (b == 'yes') {
                 ids = [];
                 Ext.each(selected, function(record) {
                     ids.push(record.data.id);
                 });
                 Ext.Ajax.request({
                     url: String.format('/yabackoffice/users/'),
                     success: function(result, request){
                         var data = result.responseText;
                         var json = Ext.decode(data);
                         Ext.getCmp('users-usergrid').getStore().reload();
                     },
                     failure: function(result, request){
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
//------------------------------------------
// UI
//------------------------------------------
Yasound.Users.UI.UsersPanel = function () {
    return {
        xtype: 'panel',
        title: gettext('Users'),
        id: 'users-users-panel',
        layout: 'border',
        items: [ {
            xtype: 'usergrid',
            id:'users-usergrid',
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
                    Yasound.Users.Handler.EnableUsers(selection)
                },
            }, {
                text: gettext('Disable'),
                disabled: true,
                ref: '../disableButton',
                iconCls: 'silk-delete',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Users.Handler.DisableUsers(selection)
                },
            }, {
                text: gettext('Report as fake user'),
                disabled: true,
                ref: '../fakeButton',
                iconCls: 'silk-delete',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Yasound.Users.Handler.FakeUsers(selection)
                },
            } ],
            listeners: {
                'selected': function (grid, id, record) {
                    grid.disableButton.setDisabled(false);
                    grid.enableButton.setDisabled(false);
                    grid.fakeButton.setDisabled(false);
                },
                'unselected': function (grid) {
                    grid.disableButton.setDisabled(true);
                    grid.enableButton.setDisabled(true);
                    grid.fakeButton.setDisabled(true);
                }
            }            
        }],
        updateData: function (component) {
        }
    };
};