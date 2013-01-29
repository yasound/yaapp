//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------

Yasound.Premium.UI.PromocodesGroupUsagePanel = function() {
    return {
        xtype : 'panel',
        title : gettext('Group usage'),
        id : 'promocodes-group-usage-panel',
        layout:'border',
        items:[{
            xtype: 'promocodegroupgrid',
            title: gettext('Groups'),
            singleSelect: true,
            url: '/yabackoffice/premium/promocodes/group/',
            region: 'west',
            width:500,
            split: true,
            tbar: [],
            listeners: {
                'selected': function (grid, id, record) {
                    var usersGrid = grid.nextSibling();
                    usersGrid.setParams({
                        'group_id': id
                    });
                    usersGrid.reload();
                }
            }
        }, {
            xtype: 'usergrid',
            title: gettext('Users'),
            singleSelect: false,
            url: '/yabackoffice/premium/promocodes/group/users/',
            region: 'center'
        }],
        updateData : function(component) {
        }
    };
};
