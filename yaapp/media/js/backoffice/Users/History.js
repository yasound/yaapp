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
            xtype: 'usergrid',
            region:'west',
            width:400,
            title: gettext('Users'),
            split: true,
            listeners: {
                'selected': function (grid, id, record) {
                    var historyGrid = grid.nextSibling();
                    historyGrid.setParams({
                        'user_id': record.data.user_id
                    })
                    historyGrid.reload();
                },
                'deselected': function (grid, id, record) {
                    var historyGrid = grid.nextSibling();
                    historyGrid.setParams({
                        'user_id': 0
                    })
                    historyGrid.reload();
                }
                
            }
            
        }, {
            xtype: 'userhistorygrid',
            region: 'center',
            title: gettext('History')
        } ],
        updateData: function (component) {
        }
    };
};