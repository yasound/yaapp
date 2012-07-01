Yasound.Users.Data.HistoryStore = function(url) {
    var fields = [ 'username', 'radio', 'date', 'type', 'message', 'song', 'share_type' ];
    return new Yasound.Utils.SimpleStore(url, fields);
};

Yasound.Users.UI.HistoryColumnModel = function() {
    return ([ {
        header: gettext('Date'),
        dataIndex: 'date',
        xtype: 'datecolumn',
        format: 'd/m/Y H:i:s',
        sortable: false,
        width: 30
    }, {
        header: gettext('Type'),
        dataIndex: 'type',
        sortable: false,
        width: 30
    }, {
        header: gettext('Username'),
        dataIndex: 'username',
        sortable: false,
        width: 30,
    }, {
        header: gettext('Radio'),
        dataIndex: 'radio',
        sortable: false,
        width: 30
    }, {
        header: gettext('Message'),
        dataIndex: 'message',
        sortable: false,
        width: 60
    }, {
        header: gettext('Song'),
        dataIndex: 'song',
        sortable: false,
        width: 60
    }, {
        header: gettext('Share type'),
        dataIndex: 'share_type',
        sortable: false,
        width: 60
    } ]);
};


Yasound.Users.UI.HistoryGrid = Ext.extend(Ext.grid.GridPanel, {
    singleSelected: false,
    url: '/yabackoffice/users/history/',
    tbar: [],
    initComponent: function() {
        this.addEvents('selected', 'unselected');
        this.pageSize = 25;
        this.store = Yasound.Users.Data.HistoryStore(this.url);
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
            cm: new Ext.grid.ColumnModel(Yasound.Users.UI.HistoryColumnModel()),
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
        Yasound.Users.UI.HistoryGrid.superclass.initComponent.apply(this, arguments);
    },
    calculatePageSize: function() {
        var bodyHeight = this.getHeight();
        var heightOther = 120+30;
        var rowHeight = 20;
        var gridRows = parseInt( ( bodyHeight - heightOther ) / rowHeight );

        this.getBottomToolbar().pageSize = gridRows;
        this.getStore().reload({ params:{ start:0, limit:gridRows } });
    },
    setParams: function (additionalParams) {
        this.getStore().additionalParams = additionalParams;
    },
    reload: function () {
        this.getStore().reload();
    }
});
Ext.reg('userhistorygrid', Yasound.Users.UI.HistoryGrid);
