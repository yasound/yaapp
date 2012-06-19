//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------
Yasound.Moderation.UI.AbusePanel = function () {
    return {
        xtype: 'panel',
        title: gettext('Abuse notifications'),
        id: 'abuse-panel',
        layout: 'border',
        items: [ {
            xtype: 'abusegrid',
            title: gettext('Abuse notifications'),
            checkboxSelect: false,
            region: 'center'
        }],
        updateData: function (component) {
        }
    };
};