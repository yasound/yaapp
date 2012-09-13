//------------------------------------------
// Datastore
//------------------------------------------

Yasound.Geoperm.Data.GeoFeatureStore = function (url) {
    var fields = [ 'id', 'country_name', 'feature_display' ];
    var sortInfo = {
        field: 'code',
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
Yasound.Geoperm.UI.GeoFeatureColumnModel = function () {
    var cm = [{
        header: gettext('Feature'),
        dataIndex: 'feature',
        sortable: true,
        width: 30,
        filterable: false
    }
    ];
    return cm;
};

Yasound.Geoperm.UI.GeoFeatureGrid = Ext.extend(Ext.grid.GridPanel, {
    singleSelect: true,
    checkboxSelect: false,
    tbar: [],
    url: '/yabackoffice/geoperm/countries/0/features/',

    initComponent: function () {
        this.addEvents('selected', 'deselected');
        this.pageSize = 25;
        this.store = Yasound.Geoperm.Data.GeoFeatureStore(this.url);
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
            cm: new Ext.grid.ColumnModel(Yasound.Geoperm.UI.GeoFeatureColumnModel()),
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
        Yasound.Geoperm.UI.GeoFeatureGrid.superclass.initComponent.apply(this, arguments);
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
Ext.reg('geofeaturegrid', Yasound.Geoperm.UI.GeoFeatureGrid);
