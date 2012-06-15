//------------------------------------------
// Datastore
//------------------------------------------


//------------------------------------------
// Handlers
//------------------------------------------
Yasound.Backoffice.Handler.FindMusicBrainzID = function(selected) {
    ids = [];
    Ext.each(selected, function(record) {
        ids.push(record.data.id);
    });

    Ext.Ajax.request({
        url: String.format('/yabackoffice/find_musicbrainz_id/'),
        success: function(result, request){
        },
        failure: function(result, request){
        },
        params: {
            ids: ids
        },
        method: 'POST',
        timeout: 1000 * 60 * 5
    });
}
//------------------------------------------
// UI
//------------------------------------------

Yasound.Backoffice.UI.AllSongsPanel = function(){
	var songGrid = Ext.ComponentMgr.create({
    	xtype:'yasoundsonggrid',
    	layout: 'fit',
    	title: gettext('Songs'),
    	region:'center',
        tbar:[{
            text: gettext('Find musicbrainz id'),
            disabled: true,
            ref:'../mbidButton',
            handler: function(b, e) {
                var grid = b.ownerCt.ownerCt;
                var selected = grid.getSelectionModel().getSelections();
                Yasound.Backoffice.Handler.FindMusicBrainzID(selected);
            }
        }],
        listeners: {
            'selected': function(grid, id, record) {
                grid.mbidButton.setDisabled(false);
            },
            'deselected': function(grid) {
                grid.mbidButton.setDisabled(true);
            } 
        }
	});
	
    return {
        xtype: 'panel',
        layout: 'fit',
        id: 'all-songs-panel',
        title: gettext('All songs'),
        items: [songGrid],
        updateData: function(component) {
            songGrid.store.reload();
        }
    };
};
