//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Users.UI.UsersPanel = function () {
    return {
        xtype: 'panel',
        title: gettext('Users'),
        id: 'users-panel',
        layout: 'border',
        items: [ {
            xtype: 'usergrid',
            region: 'center'
        } ],
        updateData: function (component) {
        }
    };
};