//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Statistics.Handler.ExportRadioStats = function (id) {
    var maskingAjax = new Ext.data.Connection({});

    maskingAjax.request({
        disableCaching: true,
        url: String.format('/yabackoffice/radios/{0}/export_stats/', id),
        form: Ext.fly('frmDummy'),
        method: 'POST',
        timeout: 1000 * 60 * 5,
        isUpload: true
    });
};

//------------------------------------------
// UI
//------------------------------------------

Yasound.Statistics.UI.RadiosPanel = function () {
    return {
        xtype: 'panel',
        title: gettext('Radios'),
        id: 'statistics-radios-panel',
        layout: 'border',
        items: [ {
            xtype: 'radiogrid',
            checkboxSelect: false,
            title: gettext('Radios'),
            id: 'statistics-radiogrid',
            region: 'center',
            listeners: {
                'selected': function (grid, id, record) {
                    grid.exportButton.setDisabled(false);
                },
                'unselected': function(grid) {
                    grid.exportButton.setDisabled(true);
                }
            },
            tbar: [{
                text: gettext('Export data'),
                disabled: true,
                ref: '../exportButton',
                iconCls: 'silk-page-excel',
                handler: function(b, e) {
                    var grid = b.ownerCt.ownerCt;
                    selection = grid.getSelectionModel().getSelections();
                    Ext.each(selection, function(record) {
                        Yasound.Statistics.Handler.ExportRadioStats(record.data.id);
                    });
                }
            }]
        }],
        updateData: function (component) {
        }
    };
};