//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

// ------------------------------------------
// UI
// ------------------------------------------
Yasound.Users.UI.HistoryPanel = function () {
    return {
        xtype: 'panel',
        title: gettext('History'),
        id: 'users-history-panel',
        layout: 'border',
        items: [ {
            xtype: 'userhistorygrid',
            region: 'center',
        } ],
        updateData: function (component) {
        }
    };
};