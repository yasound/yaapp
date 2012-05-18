//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------

//------------------------------------------
// UI
//------------------------------------------

Yasound.Statistics.UI.ChartPanel = Ext.extend(Ext.Panel, {
    url: '',
    fields: [ 'timestamp', 'created_radios' ],
    xField: 'timestamp',
    yField: 'created_radios',

    initComponent: function () {
        this.store = new Ext.data.JsonStore({
            url: this.url,
            root: 'data',
            idProperty: 'timestamp',
            fields: this.fields
        });

        var config = {
            items: [ {
                xtype: 'linechart',
                store: this.store,
                xField: this.xField,
                yField: this.yField,
                listeners: {
                    itemclick: function (o) {
                        var rec = store.getAt(o.index);
                        Ext.example.msg('Item Selected', 'You chose {0}.', rec.get('name'));
                    }
                }
            } ]
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Statistics.UI.ChartPanel.superclass.initComponent.apply(this, arguments);
    },
    updateData: function () {
        this.store.load();
    },
    reload: function(component) {
        component.store.load();
    }
});
Ext.reg('chartpanel', Yasound.Statistics.UI.ChartPanel);