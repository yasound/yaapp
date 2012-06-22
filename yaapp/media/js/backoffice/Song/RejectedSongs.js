//------------------------------------------
//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------

Yasound.Backoffice.UI.RejectedSongsPanel = function() {
    return {
        xtype: 'panel',
        layout: 'border',
        id: 'rejected-songs-panel',
        title: gettext('Rejected songs'),
        items: [ {
            xtype: 'rejectedsonggrid',
            region: 'center',
            title: gettext('Rejected songs'),
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

