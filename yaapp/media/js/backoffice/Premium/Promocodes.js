//------------------------------------------
// Datastore
//------------------------------------------

//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Premium.Handler.GenerateUniqueCodes = function (success) {
    var form = Ext.ComponentMgr.create(Yasound.Premium.UI.UniquePromocodesForm());
    var win = new Ext.Window({
        title: gettext('Promocode generator'),
        width: 500,
        autoHeight: true,
        layout: 'form',
        autoScroll: true,
        modal: true,
        preventBodyReset: true,
        items: [form],
        draggable: true,
        buttonAlign: 'center',
        buttons: [{
            text: gettext('Submit'),
            handler: function(){
                var values = form.getForm().getFieldValues();
                Ext.Ajax.request({
                    url: String.format('/yabackoffice/premium/unique_promocodes/'),
                    success: function(result, request){
                        success();
                        win.close();
                    },
                    failure: function(result, request){
                    },
                    method: 'POST',
                    params: values
                });
            }
        }]

    });
    win.on('show', function(){
        win.center();
    });
    win.show(this);



};
//------------------------------------------
// UI
//------------------------------------------
Yasound.Premium.UI.UniquePromocodesForm = function() {
    return {
        xtype: 'form',
        items: [{
            xtype: 'combo',
            fieldLabel: 'Service',
            hiddenName:'service_id',
            store: new Ext.data.ArrayStore({
                fields: ['id', 'label'],
                data : [[1, 'HD']]
            }),
            valueField:'id',
            displayField:'label',
            typeAhead: true,
            mode: 'local',
            triggerAction: 'all',
            emptyText: gettext('Select a service...'),
            selectOnFocus:true,
            width:190
        }, {
                fieldLabel: 'Prefix',
                xtype: 'textfield',
                name: 'prefix',
                value: 'YA-',
                allowBlank:false
            },{
                fieldLabel: 'Count',
                xtype: 'numberfield',
                name: 'count',
                value: 50
            }
        ]
    };
};

Yasound.Premium.UI.PromocodesPanel = function() {
    return {
        xtype : 'panel',
        title : gettext('Promocodes'),
        id : 'promocodes-panel',
        layout:'border',
        items:[{
            xtype: 'promocodegrid',
            title: gettext('Non unique usage codes'),
            url: '/yabackoffice/premium/non_unique_promocodes',
            region: 'center'
        }, {
            xtype: 'promocodegrid',
            title: gettext('Unique usage codes'),
            url: '/yabackoffice/premium/unique_promocodes/',
            region: 'west',
            width: 400,
            split: true,
            tbar: [{
                text: 'Generate 50 codes',
                handler: function (b, e) {
                    var grid = b.ownerCt.ownerCt;
                    Yasound.Premium.Handler.GenerateUniqueCodes(function () {
                        grid.getStore().reload();
                    });
                }
            }]
        }],
        updateData : function(component) {
        }
    };
};
