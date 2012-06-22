Yasound.Backoffice.Data.MostPopularSongMetadataStore = function(url) {
    var fields = [ 'id', 'name', 'artist_name', 'album_name', 'songinstance__count' ];
    return new Yasound.Utils.SimpleStore(url, fields);
};

Yasound.Backoffice.UI.MostPopularSongMetadataColumnModel = function() {
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


Yasound.Backoffice.UI.MostPopularSongMetadataGrid = Ext.extend(Ext.grid.GridPanel, {
    singleSelected: false,
    url: '/yabackoffice/songmetadata/most_popular/',
    tbar: [],
    initComponent: function() {
        this.addEvents('selected', 'unselected');
        this.pageSize = 25;
        this.store = Yasound.Backoffice.Data.MostPopularSongMetadataStore(this.url);
        this.store.pageSize = this.pageSize;

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
            bbar: new Ext.PagingToolbar({
                pageSize: this.pageSize,
                store: this.store,
                displayInfo: true,
                displayMsg: gettext('Displaying {0} - {1} of {2}'),
                emptyMsg: gettext("Nothing to display")
            }),            
            loadMask: true,
            sm: sm,
            cm: new Ext.grid.ColumnModel(Yasound.Backoffice.UI.MostPopularSongMetadataColumnModel()),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})'),
            }),
            listeners: {
                show: function(component) {
                    component.calculatePageSize();
                },
                resize: function(component) {
                    component.calculatePageSize();
                }
            }
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Backoffice.UI.MostPopularSongMetadataGrid.superclass.initComponent.apply(this, arguments);
    },
    calculatePageSize: function() {
        var bodyHeight = this.getHeight();
        var heightOther = 120+30;
        var rowHeight = 20;
        var gridRows = parseInt( ( bodyHeight - heightOther ) / rowHeight );

        this.getBottomToolbar().pageSize = gridRows;
        this.getStore().reload({ params:{ start:0, limit:gridRows } });
    }
    
});
Ext.reg('mostpopularsongmetadatagrid', Yasound.Backoffice.UI.MostPopularSongMetadataGrid);