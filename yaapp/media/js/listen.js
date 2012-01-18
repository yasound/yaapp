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
	    stream: true,
	    onplay: function() {
	    	$('#play').text(lbl_stop);
	    },
	    onstop: function() {
	    	$('#play').text(lbl_play);
	    }
	  });
	  $('#play').click();
	});

	soundManager.ontimeout(function(){
		alert('Error, cannot load stream, please reload page');
	});

	$('#play').click(function() {
	  if (mySound.playState == 1) {
		  mySound.stop();
	  } else {
		  mySound.play();
	  }
	});
	
	$('#mute').click(function() {
		mySound.toggleMute();
		if (mySound.muted) {
			$('#mute').text(lbl_unmute);
		} else {
			$('#mute').text(lbl_mute);
		}
	})
	
	$('#inc').click(function() {
		if (mySound.volume <= 90) {
			mySound.setVolume(mySound.volume+10);
		}	
	})
	$('#dec').click(function() {
		if (mySound.volume >= 10) {
			mySound.setVolume(mySound.volume-10);
		}
	})
	
});
