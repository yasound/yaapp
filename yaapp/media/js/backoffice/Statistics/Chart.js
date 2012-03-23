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
    initComponent: function() {
        this.store = new Ext.data.JsonStore({
            url: '/yabackoffice/radios/stats/created/',
            root: 'data',
            idProperty: 'timestamp',
            fields: ['timestamp', 'created_radios']
        });
        
    	var config = {
	       items: [{
	            xtype: 'linechart',
	            store: this.store,
	            xField: 'timestamp',
	            yField: 'created_radios',
				listeners: {
					itemclick: function(o){
						var rec = store.getAt(o.index);
						Ext.example.msg('Item Selected', 'You chose {0}.', rec.get('name'));
					}
				}
	        }]
        		
        }; // eo config object
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Yasound.Statistics.UI.ChartPanel.superclass.initComponent.apply(this, arguments);
    },
    updateData: function() {
        this.store.load();
    }
});
Ext.reg('chartpanel', Yasound.Statistics.UI.ChartPanel);