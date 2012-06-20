//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------

Yasound.Backoffice.UI.MostPopularSongsPanel = function() {
    return {
        xtype: 'panel',
        layout: 'border',
        id: 'most-popular-songs-panel',
        title: gettext('Most popular songs'),
        items: [ {
            xtype: 'mostpopularsongmetadatagrid',
            region: 'center',
            title: gettext('Most popular songs'),
            tbar: [ {
                iconCls: 'silk-arrow-refresh',
                text: gettext('Refresh'),
                handler: function(btn, e) {
                    var grid = btn.ownerCt.ownerCt;
                    grid.getStore().reload();                    
                }
            }]
        } ],
        updateData: function(component) {
        }
    };
};
