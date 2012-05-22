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
            checkboxSelect: false,
            region: 'center',
            listeners: {
                'selected': function(grid, id, record) {
                    var wallEventGrid = grid.nextSibling();
                    wallEventGrid.setParams({
                        'user_id': id
                    })
                    wallEventGrid.reload();
                }
            }
        }, {
            xtype: 'walleventgrid',
            region: 'east',
            width: 600,
            split: true,
        } ],
        updateData: function (component) {
        }
    };
};