/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Deezer');

Yasound.Deezer.Operations = function () {
    var mgr = {
        yasoundSong: undefined,
        deezerPlaylistId: 0,

        YASOUND_PLAYLIST_TITLE: gettext('Preferred songs on Yasound'),

        scanPlaylists: function () {
            console.log('scanning playlists');
            DZ.api('user/me/playlists', 'GET', function(response) {
                console.log(response);
                if (response.total === 0) {
                    mgr.createYasoundPlaylist();
                } else {
                    _.each(response.data, function(playlist) {
                        if (playlist.title == mgr.YASOUND_PLAYLIST_TITLE) {
                            console.log('found yasound playlist!');
                            mgr.deezerPlaylistId = player.id;
                        }
                    });
                    if (mgr.deezerPlaylistId === 0) {
                        mgr.createYasoundPlaylist();
                    }
                }
            });
        },

        createYasoundPlaylist: function () {
            console.log('creating yasound playlist');
            DZ.api('user/me/playlists', 'POST', {title: mgr.YASOUND_PLAYLIST_TITLE}, function (response) {
                console.log('response is');
                console.log(response);
                mgr.deezerPLaylistId = response.id;
            });
        },

        onLike: function (song) {
            mgr.yasoundSong = song;
            var title = song.rawTitleWithoutAlbum();
            var query = '/search?q=' + title + '&order=RANKING';
            console.log('query is "' + query + '"');
            DZ.api(query, mgr.searchCallback);
        },

        searchCallback: function (response) {
            console.log('response is');
            console.log(response);
            var total = response.total;
            if (total > 0) {
                console.log('found ' + total + ' items');
                var item = response.data[0];
                var deezerId = item.id;
                mgr.onSongFound(deezerId);
            } else {
                mgr.onSongNotFound();
            }
        },

        onSongFound: function (deezerId) {
            if (mgr.deezerPlaylistId === 0) {
                console.log('no playlist id, exiting now');
                return;
            }
            DZ.api('playlist/' + mgr.deezerPlaylistId + '/tracks', 'POST', {songs: [deezerId]}, function (response) {
                console.log(response);
            });
        },

        onSongNotFound: function () {
            console.log('no song found, sorry');
        }

    };
    $.subscribe('/song/like', mgr.onLike);
    console.log('starting Yasound.Deezer.Operations');
    mgr.scanPlaylists();
    return mgr;
};