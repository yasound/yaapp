
Yasound.Utils.SimpleStore = function (url, fields, sortInfo, idField) {
    if (!sortInfo) {
        sortInfo = {
            field: 'id',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        };
    }
    if (!idField) {
    	idField = 'id';
    }
    return new Ext.data.GroupingStore({
        reader: new Ext.data.JsonReader({
            idProperty: idField,
            fields: fields,
            root: 'data',
            totalProperty: 'results'
        }),
        writer: new Ext.data.JsonWriter({
            encode: true,
            writeAllFields: true
        }),
        sortInfo: sortInfo,
        autoLoad: false,
        remoteSort: true,
        restful: true,
        proxy: new Ext.data.HttpProxy({
            url: url,
            method: 'GET'
        }),
        additionalParams: {},
        listeners: {
            beforewrite: function (store, action, records, options, arg) {
            },
            beforeLoad: function (store, options) {
                if (!options.params.start) {
                    store.baseParams.start = 0;
                }
                if (!options.params.limit) {
                    store.baseParams.limit = store.pageSize;
                }

                Ext.apply(store.baseParams, store.additionalParams);
            }
        }
    });
}
