//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Backoffice.Handler.ShowUploadWindow = function(songMetadataId) {
    var win = new Ext.Window({
        title: 'Résultats',
        width: 500,
        autoHeight: true,
        autoScroll: true,
        modal: true,
        preventBodyReset: true,
        items:[{
            xtype: 'uploadform',
            songMetadataId:songMetadataId,
            listeners: {
                uploadSuccess: function() {
                    win.close(this);
                },
                uploadFailure: function(fp, message) {
                    Yasound.Utils.DisplayLogWindow(message)
                },
            }
        }],
        draggable: true
    });
    win.on('show', function(){
        win.center();
    });
    win.show(this);
}

//------------------------------------------
// UI
//------------------------------------------

Yasound.Backoffice.UI.MissingSongsPanel = function() {
    return {
        xtype: 'panel',
        layout: 'border',
        id: 'missing-songs-panel',
        title: gettext('Missing songs'),
        items: [ {
            xtype: 'missingsongmetadatagrid',
            region: 'center',
            title: gettext('Most missing songs'),
            listeners: {
                selected: function(grid) {
                    grid.btnAdd.setDisabled(false);
                },
                unselected: function(grid) {
                    grid.btnAdd.setDisabled(true);
                }
            },
            tbar: [ {
                iconCls: 'silk-arrow-refresh',
                text: gettext('Refresh'),
                handler: function(btn, e) {
                    var grid = btn.ownerCt.ownerCt;
                    grid.getStore().reload();                    
                }
            }, {
                iconCls: 'silk-add',
                disabled: true,
                ref: '../btnAdd',
                text: gettext('Upload file'),
                handler: function(btn, e) {
                    var grid = btn.ownerCt.ownerCt;
                    var selected = grid.getSelectionModel().getSelected();
                    if (selected) {
                        var id = selected.data.id;
                        Yasound.Backoffice.Handler.ShowUploadWindow(id);
                    }
                }
            } ]
        } ],
        updateData: function(component) {
        }
    };
};
