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
            region: 'center'
        } ],
        updateData: function (component) {
        }
    };
};