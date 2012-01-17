$(document).ready(function() {
	soundManager.url = '/media/js/sm/swf/'; // directory where SM2 .SWFs live
	soundManager.preferFlash = false;
	soundManager.useHTML5Audio = true;
	soundManager.debugMode = true;
	var mySound = undefined;
	soundManager.onready(function(){
	  mySound = soundManager.createSound({
	    id: 'soundManagerObject1',
	    url: g_radio_url,
	    stream: true
	  });
	  $('#play').click();
	});

	soundManager.ontimeout(function(){
		alert('Error, cannot load stream, please reload page');
	});

	$('#play').click(function() {
	  mySound.play();
	})
	
});
