//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Moderation.UI.UsersPanel = function () {
    return {
        xtype: 'panel',
        title: gettext('Users'),
        id: 'moderation-users-panel',
        layout: 'border',
        items: [ {
            xtype: 'usergrid',
            region: 'center'
        } ],
        updateData: function (component) {
        }
    };
};