<?php
	$file = $_GET["f"]; 
	$filesize = @filesize($file); 
    header("Content-Disposition: attachment; filename=".$file); 
    header("Content-Type: application/octet-stream" ); 
    header("Content-Type: application/force-download" ); 
    header("Content-Type: application/download" ); 
    header("Content-Transfer-Encoding: binary" ); 
    header("Pragma:no-cache" ); 
    header("Expires:0" ); 
    @set_time_limit(600); 
    readfile($file); 
?>