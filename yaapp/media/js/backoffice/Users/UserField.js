Yasound.Users.UI.UserField = Ext.extend(Ext.form.TriggerField, {

    triggerClass: 'x-form-arrow-trigger',
    resizable: true,
    
    initComponent: function(){
        this.editable = false;
        Yasound.Users.UI.UserField.superclass.initComponent.call(this);
        this.on('specialkey', function(f, e){
            if (e.getKey() == e.ENTER) {
                this.onTriggerClick();
            }
        }, this);
        this.getGrid();
    },
    
    onTriggerClick: function(){
        this.getGrid().show();
        this.getGrid().getEl().alignTo(this.wrap, 'tl-bl?');
    },
    
    onRender: function(ct, position){
        if (this.hiddenName && !Ext.isDefined(this.submitValue)) {
            this.submitValue = false;
        }
        Yasound.Users.UI.UserField.superclass.onRender.call(this, ct, position);
        
        if (this.hiddenName) {
            this.hiddenField = this.el.insertSibling({
                tag: 'input',
                type: 'hidden',
                name: this.hiddenName,
                id: (this.hiddenId || this.hiddenName)
            }, 'before', true);
            
        }
        if (Ext.isGecko) {
            this.el.dom.setAttribute('autocomplete', 'off');
        }
    },
    
    getGrid: function(){
        if (!this.gridPanel) {
            if (!this.gridWidth) {
                this.gridWidth = Math.max(600, this.width || 600);
            }
            if (!this.gridHeight) {
                this.gridHeight = 370;
            }
            this.gridPanel = Ext.ComponentMgr.create({
            	xtype: 'usergrid',
            	title: gettext('Please select user'),
                renderTo: Ext.getBody(),
                singleSelect: true,
            	checkboxSelect: false,
                floating: true,
                autoScroll: true,
                minWidth: 200,
                minHeight: 400,
                width: this.gridWidth,
                height: this.gridHeight,
                listeners: {
                    hide: this.onGridHide,
                    show: this.onGridShow,
                    selected: this.onUserSelected,
                    deselected: this.onUserDeselected,
                    scope: this
                }
            });
            this.gridPanel.show();
            this.gridPanel.hide();
            //this.relayEvents(this.gridPanel.loader, ['beforeload', 'load', 'loadexception']);
            if (this.resizable) {
                this.resizer = new Ext.Resizable(this.gridPanel.getEl(), {
                    pinned: true,
                    handles: 'se'
                });
                this.mon(this.resizer, 'resize', function(r, w, h){
                    this.gridPanel.setSize(w, h);
                }, this);
            }
        }
        return this.gridPanel;
    },
    
    initValue: function(){
        Yasound.Users.UI.UserField.superclass.initValue.call(this);
        if (this.hiddenField) {
            this.hiddenField.value = Ext.value(Ext.isDefined(this.hiddenValue) ? this.hiddenValue : this.value, '');
        }
    },
    
    onDestroy: function(){
        Ext.destroyMembers(this, 'hiddenField');
        Yasound.Users.UI.UserField.superclass.onDestroy.call(this);
    },
    
    getName: function(){
        var hf = this.hiddenField;
        return hf && hf.name ? hf.name : this.hiddenName || Ext.form.ComboBox.superclass.getName.call(this);
    },
    
    clearValue: function(){
        if (this.hiddenField) {
            this.hiddenField.value = '';
        }
        this.setRawValue('');
        this.lastSelectionText = '';
        this.applyEmptyText();
        this.value = '';
    },
    
    onGridShow: function(){
    	this.gridPanel.getStore().reload();
        Ext.getDoc().on('mousewheel', this.collapseIf, this);
        Ext.getDoc().on('mousedown', this.collapseIf, this);
    },
    
    onGridHide: function(){
        Ext.getDoc().un('mousewheel', this.collapseIf, this);
        Ext.getDoc().un('mousedown', this.collapseIf, this);
    },
    
    collapseIf: function(e){
        if (!e.within(this.wrap) && !e.within(this.getGrid().getEl())) {
            this.collapse();
        }
    },
    
    collapse: function(){
        this.getGrid().hide();
        this.resizer.resizeTo(this.gridWidth, this.gridHeight);
    },
    
    // private
    validateBlur: function(){
        return !this.gridPanel || !this.gridPanel.isVisible();
    },
    
    setValue: function(v, label){
        this.startValue = this.value = v;
        if (this.gridPanel) {
            var n = this.gridPanel.getStore().getById(v);
            if (n) {
                this.setRawValue(n.data.name);
                if (this.hiddenField) {
                    this.hiddenField.value = Ext.value(v, '');
                }
            } else {
            	if (label) {
                    this.setRawValue(label);
                    if (this.hiddenField) {
                        this.hiddenField.value = Ext.value(v, '');
                    }
            	} else {
            		this.clearValue();
            	}
            }
        }
    },
    
    getValue: function(){
        return this.value;
    },
    
    onUserSelected: function(grid, id, record){
        this.setRawValue(record.data.name);
        this.value = id;
        this.fireEvent('select', this, record);
        this.collapse();
		this.hiddenField.value = record.data.id;
    },

    onUserDeselected: function(grid){
    	this.clearValue();
    },
});
Ext.reg('userfield', Yasound.Users.UI.UserField);