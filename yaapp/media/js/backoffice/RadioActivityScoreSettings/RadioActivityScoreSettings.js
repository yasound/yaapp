//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------


Yasound.RadioActivityScoreSettings.UI.ActivityFactors = function () {
    return {
    	xtype: 'settingsgrid',
        title: gettext('Radio activity score factors'),
        layout: 'fit',
        url: '/yabackoffice/radio_activity_score_factors',
        id: 'activity-factors',
        tools: [ {
            id: 'refresh',
            handler: function (event, toolEl, panel) {
                panel.getStore().reload();
            }
        } ]
    }
};


Yasound.RadioActivityScoreSettings.UI.Panel = function () {
    return {
        xtype: 'panel',
        layout:'fit',
        title: gettext('Radio activity score'),
        id: 'radio-activity-score-panel',
        items:[Yasound.RadioActivityScoreSettings.UI.ActivityFactors()],
        updateData: function (component) {
        	Ext.getCmp('activity-factors').getStore().reload();
        }
    };
}