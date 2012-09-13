//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------

Yasound.Geoperm.UI.Panel = function() {
    return {
        xtype : 'panel',
        title : gettext('Geo permissions'),
        id : 'geoperm-panel',
        layout:'border',
        items:[{
            xtype: 'countrygrid',
            title: gettext('Countries'),
            region: 'center'
        }, {
            xtype: 'geofeaturegrid',
            title: gettext('Features'),
            region: 'east',
            split: true,
            width:400
        }],
        updateData : function(component) {
        }
    };
};
