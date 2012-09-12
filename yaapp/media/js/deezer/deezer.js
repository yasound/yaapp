/*jslint nomen: true, vars: true, bitwise: true, browser: true, eqeq: true, evil: true, undef: true, white: true, newcap: true */
/*extern Ext, $ */
$(document).ready(function () {

    $('#test1').on('click', function (e) {
        DZ.player.playTracks([3135556, 1152226], 0, function(response){
        console.log("track list", response.tracks);
        });
    });


    $('#test2').on('click', function (e) {
        DZ.player.playTracks([3135557, 1152227], 0, function(response){
        console.log("track list", response.tracks);
        });
    });
});