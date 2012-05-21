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
            width: 600,
            split: true,
        } ],
        updateData: function (component) {
        }
    };
};