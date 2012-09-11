//------------------------------------------
// Datastore
//------------------------------------------

Yasound.Premium.Data.PromocodeStore = function (url) {
    var fields = [ 'id', 'code', 'enabled', 'unique', 'service', {
        name:'created',
        type: 'date',
        dateFormat: 'Y-m-d H:i:s'
    }];
    var sortInfo = {
        field: 'created',
        direction: 'DESC'
    };
    return new Yasound.Utils.SimpleStore(url, fields, sortInfo, 'id');
};
// ------------------------------------------
// Handlers
// ------------------------------------------

// ------------------------------------------
// UI
// ------------------------------------------
Yasound.Premium.UI.PromocodeColumnModel = function () {
    var cm = [{
        header: gettext('Created'),
        dataIndex: 'created',
        xtype: 'datecolumn',
        format: 'd/m/Y H:i:s',
        sortable: true,
        width: 20
    }, {
        header: gettext('Code'),
        dataIndex: 'code',
        sortable: true,
        width: 50,
        filterable: false
    }, {
        header: gettext('Service'),
        dataIndex: 'service',
        sortable: true,
        width: 50,
        filterable: false
    }];
    return cm;
};

Yasound.Premium.UI.PromocodeGrid = Ext.extend(Ext.grid.GridPanel, {
    singleSelect: true,
    checkboxSelect: false,
    tbar: [],
    url: '/yabackoffice/premium/promocodes',

    initComponent: function () {
        this.addEvents('selected', 'deselected');
        this.pageSize = 25;
        this.store = Yasound.Premium.Data.PromocodeStore(this.url);
        this.store.pageSize = this.pageSize;

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
            cm: new Ext.grid.ColumnModel(Yasound.Premium.UI.PromocodeColumnModel()),
            view: new Ext.grid.GroupingView({
                hideGroupedColumn: false,
                forceFit: true,
                groupTextTpl: gettext('{text} ({[values.rs.length]} {[values.rs.length > 1 ? "elements" : "element"]})')
            }),
            plugins: [ new Ext.ux.grid.GridHeaderFilters()],
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
        Yasound.Premium.UI.PromocodeGrid.superclass.initComponent.apply(this, arguments);
    },
    calculatePageSize: function () {
        if (!this.isVisible()) {
            return;
        }
        var bodyHeight = this.getHeight();
        var heightOther = this.getTopToolbar().getHeight() + this.getBottomToolbar().getHeight() + 50 + 20;
        var rowHeight = 21;
        var gridRows = parseInt((bodyHeight - heightOther) / rowHeight, 10);

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
    }
});
Ext.reg('promocodegrid', Yasound.Premium.UI.PromocodeGrid);
