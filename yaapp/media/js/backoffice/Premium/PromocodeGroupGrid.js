//------------------------------------------
// Datastore
//------------------------------------------

Yasound.Premium.Data.PromocodeGroupStore = function (url) {
    var fields = [ 'id', 'name', 'used_codes_count', 'available_codes_count', {
        name:'created',
        type: 'date',
        dateFormat: 'Y-m-d H:i:s'
    }, {
        name:'updated',
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
Yasound.Premium.UI.PromocodeGroupColumnModel = function () {
    var cm = [{
        header: gettext('Created'),
        dataIndex: 'created',
        xtype: 'datecolumn',
        format: 'd/m/Y H:i:s',
        sortable: true,
        width: 70
    }, {
        header: gettext('Name'),
        dataIndex: 'name',
        sortable: true,
        width: 70
    }, {
        header: gettext('Used codes'),
        dataIndex: 'used_codes_count',
        sortable: true,
        width: 70
    }, {
        header: gettext('Available codes'),
        dataIndex: 'available_codes_count',
        sortable: true,
        width: 70
    }];
    return cm;
};

Yasound.Premium.UI.PromocodeGroupGrid = Ext.extend(Ext.grid.GridPanel, {
    singleSelect: true,
    checkboxSelect: false,
    tbar: [],
    url: '/yabackoffice/premium/promocodes/group/',

    initComponent: function () {
        this.addEvents('selected', 'deselected');
        this.pageSize = 25;
        this.store = Yasound.Premium.Data.PromocodeGroupStore(this.url);
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
            cm: new Ext.grid.ColumnModel(Yasound.Premium.UI.PromocodeGroupColumnModel()),
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
        Yasound.Premium.UI.PromocodeGroupGrid.superclass.initComponent.apply(this, arguments);
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
Ext.reg('promocodegroupgrid', Yasound.Premium.UI.PromocodeGroupGrid);
