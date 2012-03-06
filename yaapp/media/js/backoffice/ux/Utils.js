

Yasound.Utils.SimpleStore = function(url, fields) {
    return new Ext.data.GroupingStore({
        reader: new Ext.data.JsonReader({
            idProperty: 'id',
            fields: fields,
            root: 'data',
            totalProperty: 'results'
        }),
        writer: new Ext.data.JsonWriter({
            encode: true,
            writeAllFields: true
        }),
        sortInfo: {
            field: 'id',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        },
        autoLoad: false,
        remoteSort: true,
        restful: true,
        proxy: new Ext.data.HttpProxy({
            url: url,
            method: 'GET'
        }),
        listeners: {
            beforewrite: function(store, action, records, options, arg){
            },
            beforeLoad: function(store, options){
				if (!options.params.start) {
					store.baseParams.start = 0;
				}
                if (!options.params.limit) {
                    store.baseParams.limit = store.pageSize;
                }
            }
        }
    });	
}
