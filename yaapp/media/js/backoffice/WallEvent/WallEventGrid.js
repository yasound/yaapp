//------------------------------------------
// Datastore
//------------------------------------------

Yasound.WallEvents.Data.WallEventStore = function () {
    var fields = [ 'id', {
        name: 'start_date',
        type: 'date',
        dateFormat: 'Y-m-d H:i:s'
    }, 'radio', 'type', 'user_name', 'text' ];
    var url = '/yabackoffice/wall_events';
    var sortInfo = {
        field: 'start_date',
        direction: 'DESC'
    };
    return new Yasound.Utils.SimpleStore(url, fields, sortInfo);
};

// ------------------------------------------
// Handlers
// ------------------------------------------

// ------------------------------------------
// UI
// ------------------------------------------
Yasound.WallEvents.UI.WallEventColumnModel = function (expander) {
    var cm = [ expander, {
        header: gettext('Date'),
        dataIndex: 'start_date',
        xtype: 'datecolumn',
        format: 'd/m/Y H:i:s',
        sortable: true,
        width: 70
    }, {
        header: gettext('Radio'),
        dataIndex: 'radio',
        sortable: true,
        width: 50,
        filterable: true,
        filter: {
            xtype: "textfield",
            filterName: "radio"
        }
    }, {
        header: gettext('User'),
        dataIndex: 'user_name',
        sortable: true,
        filterable: true,
        width: 50,
        filter: {
            xtype: "textfield",
            filterName: "user_name"
        }
    }, {
        header: gettext('Text'),
        dataIndex: 'text',
        sortable: true,
        filterable: true,
        width: 150,
        filter: {
            xtype: "textfield",
            filterName: "text"
        }
    } ];
    return cm;
};

Yasound.WallEvents.UI.WallEventGrid = Ext.extend(Ext.grid.GridPanel, {
    singleSelect: true,
    checkboxSelect: false,
    tbar: [],
    initComponent: function () {
        this.addEvents('selected', 'deselected');
        this.pageSize = 25;
        this.store = Yasound.WallEvents.Data.WallEventStore();
        this.store.pageSize = this.pageSize;

        var expander = new Ext.ux.grid.RowExpander({
            tpl: new Ext.Template('<p><b>{text}</b></p>')
        });
        this.expander = expander;

        var sm = new Ext.grid.CheckboxSelectionModel({
            singleSelect: this.singleSelect,
            listeners: {
                selectionchange: function (sm) {
                    Ext.each(sm.getSelections(), function (record) {
                        this.grid.fireEvent('selected', this.grid, record.data.id, record);
                    }, this);
                    if (!sm.hasSelection()) {
                        this.grid.fireEvent('deselected', this.grid);
                    }
                }
            }
        });
        
        var that = this;
        this.store.on('load', function() {
            that.expandAllRows();
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
            loadMask: false,
            sm: sm,
            cm: new Ext.grid.ColumnModel(Yasound.WallEvents.UI.WallEventColumnModel(expander)),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
            plugins: [ expander, new Ext.ux.grid.GridHeaderFilters()],
            listeners: {
                show: function (component) {
                    component.calculatePageSize();
                },
                resize: function (component) {
                    component.calculatePageSize();
                }
            }
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.WallEvents.UI.WallEventGrid.superclass.initComponent.apply(this, arguments);
    },
    calculatePageSize: function () {
        if (!this.isVisible()) {
            return;
        }
        var bodyHeight = this.getHeight();
        var heightOther = this.getTopToolbar().getHeight() + this.getBottomToolbar().getHeight() + 50 + 20;
        var rowHeight = 21;
        var gridRows = parseInt((bodyHeight - heightOther) / rowHeight);

        this.getBottomToolbar().pageSize = gridRows;
        this.getStore().reload({
            params: {
                start: 0,
                limit: gridRows
            }
        });
    },
    setParams: function (additionalParams) {
        this.getStore().additionalParams = additionalParams;
    },
    reload: function () {
        this.getStore().reload();
    },
    expandAllRows: function () {
        var store = this.getStore();
        var expander = this.expander;
        var grid = this;
        nRows = store.getCount();
        for (i = 0; i < nRows; i++)
            expander.expandRow(grid.view.getRow(i));
    }

});
Ext.reg('walleventgrid', Yasound.WallEvents.UI.WallEventGrid);
