//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------

Yasound.Premium.UI.PermanentPromocodesUsagePanel = function() {
    return {
        xtype : 'panel',
        title : gettext('Permanent codes usage'),
        id : 'unique-promocodes-usage-panel',
        layout:'border',
        items:[{
            xtype: 'promocodegrid',
            title: gettext('Promocodes'),
            singleSelect: true,
            url: '/yabackoffice/premium/non_unique_promocodes/',
            region: 'west',
            width:500,
            split: true,
            tbar: [],
            listeners: {
                'selected': function (grid, id, record) {
                    var usersGrid = grid.nextSibling();
                    usersGrid.setParams({
                        'promocode_id': id
                    });
                    usersGrid.reload();
                }
            }
        }, {
            xtype: 'usergrid',
            title: gettext('Users'),
            singleSelect: false,
            url: '/yabackoffice/premium/promocodes/users/',
            region: 'center'
        }],
        updateData : function(component) {
        }
    };
};
