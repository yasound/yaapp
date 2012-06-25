// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Backoffice.Handler.ExportMostPopularSongs = function () {
    var maskingAjax = new Ext.data.Connection({});

    maskingAjax.request({
        disableCaching: true,
        url: String.format('/yabackoffice/songmetadata/export_most_popular/'),
        form: Ext.fly('frmDummy'),
        method: 'POST',
        timeout: 1000 * 60 * 5,
        isUpload: true
    });    
};

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
            }, {
                text: gettext('Export'),
                handler: function(b, e) {
                    Yasound.Backoffice.Handler.ExportMostPopularSongs();
                }
            }]
        } ],
        updateData: function(component) {
        }
    };
};