<?php
/**
 *	Get list of .be defacements from Zone-H
 *
 *	@version 20100801
 * 	@author Koen Van Impe <koen.vanimpe@cudeso.be>
 *	@license New BSD : http://www.vanimpe.eu/license
 *
 */

// configs
$date_prefix = "201";
$notifier_prefix = "/archive/notifier";

$sapi_type = php_sapi_name();
if (substr($sapi_type, 0, 3) == 'cli')	$breakline = "";
else                               		$breakline = "<br />";

// load the HTML file
$html =	file_get_contents("zoneh.html");
//$html =	file_get_contents("http://www.zone-h.org/archive/filter=1/domain=be/page=1/filter_date_select=today");
//$html =	file_get_contents("http://www.zone-h.org/archive/filter=1/domain=be/page=1");

// remove multibyte stuff
$html = @mb_convert_encoding($html, 'HTML-ENTITIES', 'utf-8');

// get the start and end position of the defacement table
$startpos = strpos($html, "<table id=\"ldeface\">");
$endpos = strpos(substr($html, $startpos), "</table");
$defacedhtml = substr($html, $startpos, $endpos);

// convert the rows to an array
$rows = explode("<tr",$defacedhtml);

$ignore = 0;
foreach($rows as $row) {
	
	// init
	$print_results = false;
	
	// ignore headers
	if ($ignore < 2) $ignore++;
	else {
		// convert the rows to entries in the array
		$columns = explode("<td>", $row);

		// init
		$counter = 0;
		$defacement_date = "";
		$defacement_notifier = "";
		$defacement_site = "";
		$defacement_platform = "";
		
		// walk through all the columns
		foreach ($columns as $col) {
			// ignore </td>
			$col = trim($col);
			$col = str_replace("</td>","",$col);
			
			// skip over ignores and empty ones
//			if ($continue) continue;
			if (!(strlen($col)) > 0) continue;
			if ($col == "H") continue;
			if (substr($col, 0, strlen("onMouseOver")) == "onMouseOver") continue;
			if (substr($col, 0, strlen("<img ")) == "<img ") continue;
			if (strpos($col, "/archive/ip=") > 0) continue;
			if (strpos($col, "/archive/domain=") > 0) continue;
			if (strpos($col, "<td colspan") > 0) continue;
										
			// the date
			if (substr($col, 0, strlen($date_prefix)) == $date_prefix) 	{
					$defacement_date = $col;
					continue;
			}
			
			// the notifier
			if (strpos($col, $notifier_prefix) > 0) {
					$defacement_notifier = $col;
					continue;
			}
			
			// the first column is the site
			if ($counter == 0) $defacement_site = trim($col);
			// and then the platform
			if ($counter == 1) $defacement_platform = trim($col);
			
			// increase the position counter
			$counter++;
		}
	}
	
	// only print if there's a site
	if (strlen($defacement_site) > 0) {
		$today_t = time();
		$yesterday_t = $today_t - 24*60*60;
		$today = date("Y/m/d", $today_t);
		$yesterday = date("Y/m/d", $yesterday_t);

		if (($today == $defacement_date) or ($yesterday == $defacement_date)) {
			
			echo "\nDate: $defacement_date $breakline";
			// don't print on CLI because it contains a wrapped <a
			//echo "\nNotifier: $defacement_notifier";
			echo "\nSite: $defacement_site $breakline";
			echo "\nPlatform: $defacement_platform\n\n $breakline $breakline";			
		}
	}
}

?>
