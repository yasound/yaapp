Yasound.Backoffice.Data.MissingSongMetadataStore = function(url) {
    var fields = [ 'id', 'name', 'artist_name', 'album_name', 'songinstance__count' ];
    return new Yasound.Utils.SimpleStore(url, fields);
};

Yasound.Backoffice.UI.MissingSongMetadataColumnModel = function() {
    return ([ {
        header: gettext('Track'),
        dataIndex: 'name',
        sortable: false,
        width: 60
    }, {
        header: gettext('Album'),
        dataIndex: 'album_name',
        sortable: false,
        width: 60
    }, {
        header: gettext('Artist'),
        dataIndex: 'artist_name',
        sortable: false,
        width: 60,
    }, {
        header: gettext('Count'),
        dataIndex: 'songinstance__count',
        sortable: false,
        width: 20
    } ]);
};


Yasound.Backoffice.UI.MissingSongMetadataGrid = Ext.extend(Ext.grid.GridPanel, {
    singleSelected: false,
    url: '/yabackoffice/songmetadata/top_missing/',
    tbar: [],
    initComponent: function() {
        this.addEvents('selected', 'unselected');
        this.store = Yasound.Backoffice.Data.MissingSongMetadataStore(this.url);

        var sm = new Ext.grid.RowSelectionModel({
            singleSelect: this.singleSelect,
            listeners: {
                selectionchange: function(sm) {
                    Ext.each(sm.getSelections(), function(record) {
                        this.grid.fireEvent('selected', this.grid, record.data.id, record);
                    }, this);
                    if (!sm.hasSelection()) {
                        this.grid.fireEvent('deselected', this.grid);
                    }
                }
            }
        });

        var config = {
            tbar: this.tbar,
            loadMask: true,
            sm: sm,
            cm: new Ext.grid.ColumnModel(Yasound.Backoffice.UI.MissingSongMetadataColumnModel()),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})'),
            })
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Backoffice.UI.MissingSongMetadataGrid.superclass.initComponent.apply(this, arguments);
    }
});
Ext.reg('missingsongmetadatagrid', Yasound.Backoffice.UI.MissingSongMetadataGrid);
