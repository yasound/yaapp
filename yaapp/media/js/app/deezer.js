/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
Namespace('Yasound.Deezer');

Yasound.Deezer.LikeOperations = function () {
    var mgr = {
        yasoundSong: undefined,
        deezerPlaylistId: 0,

        YASOUND_PLAYLIST_TITLE: gettext('Yasound Playlist'),

        scanPlaylists: function () {
            DZ.api('user/me/playlists', 'GET', function(response) {
                if (response.total === 0) {
                    mgr.createYasoundPlaylist();
                } else {
                    _.each(response.data, function(playlist) {
                        if (playlist.title == mgr.YASOUND_PLAYLIST_TITLE) {
                            mgr.deezerPlaylistId = playlist.id;
                        }
                    });
                    if (mgr.deezerPlaylistId === 0) {
                        mgr.createYasoundPlaylist();
                    }
                }
            });
        },

        createYasoundPlaylist: function () {
            DZ.api('user/me/playlists', 'POST', {title: mgr.YASOUND_PLAYLIST_TITLE}, function (response) {
                mgr.deezerPLaylistId = response.id;
            });
        },

        onLike: function (event, song) {
            mgr.yasoundSong = song;
            var title = song.rawTitleWithoutAlbum();
            var query = '/search?q=' + title + '&order=RANKING';
            DZ.api(query, mgr.searchCallback);
        },

        searchCallback: function (response) {
            var total = response.total;
            if (total > 0) {
                var item = response.data[0];
                var deezerId = item.id;
                mgr.onSongFound(deezerId);
            } else {
                mgr.onSongNotFound();
            }
        },

        onSongFound: function (deezerId) {
            if (mgr.deezerPlaylistId === 0) {
                return;
            }
            var url = 'playlist/' + mgr.deezerPlaylistId + '/tracks';
            var params = {songs: "" + deezerId + ','};
            DZ.api(url, 'POST', params, function (response) {
            });
        },

        onSongNotFound: function () {
        }

    };
    $.subscribe('/song/like', mgr.onLike);
    mgr.scanPlaylists();
    return mgr;
};

Yasound.Deezer.ExportOperations = function () {
    var mgr = {
        yasoundSong: undefined,
        deezerPlaylistId: 0,

        YASOUND_PLAYLIST_TITLE: gettext('Yasound Import'),

        scanPlaylists: function () {
            DZ.api('user/me/playlists', 'GET', function(response) {
                if (response.total === 0) {
                    mgr.createYasoundPlaylist();
                } else {
                    _.each(response.data, function(playlist) {
                        if (playlist.title == mgr.YASOUND_PLAYLIST_TITLE) {
                            mgr.deezerPlaylistId = playlist.id;
                        }
                    });
                    if (mgr.deezerPlaylistId === 0) {
                        mgr.createYasoundPlaylist();
                    }
                }
            });
        },

        createYasoundPlaylist: function () {
            DZ.api('user/me/playlists', 'POST', {title: mgr.YASOUND_PLAYLIST_TITLE}, function (response) {
                mgr.deezerPLaylistId = response.id;
            });
        },

        onImport: function (event, song) {
            mgr.yasoundSong = song;
            var title = song.rawTitleWithoutAlbum();
            var query = '/search?q=' + title + '&order=RANKING';
            DZ.api(query, mgr.searchCallback);
        },

        searchCallback: function (response) {
            var total = response.total;
            if (total > 0) {
                var item = response.data[0];
                var deezerId = item.id;
                mgr.onSongFound(deezerId);
            } else {
                mgr.onSongNotFound();
            }
        },

        onSongFound: function (deezerId) {
            if (mgr.deezerPlaylistId === 0) {
                return;
            }
            var url = 'playlist/' + mgr.deezerPlaylistId + '/tracks';
            var params = {songs: "" + deezerId + ','};
            DZ.api(url, 'POST', params, function (response) {
            });
        },

        onSongNotFound: function () {
        }

    };
    $.subscribe('/radio/import/add_from_server', mgr.onImport);
    mgr.scanPlaylists();
    return mgr;
};
