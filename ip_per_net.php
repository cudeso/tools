<?php
/**
 *
 * Parse a log file and group by entries from another file
 *
 * This script reads a log file and then groups the entries
 * according to keys found in an iplist
 *
 * This script is useful if you want to group log file entries
 * based on AS number or network name.
 *
 * 		Koen Van Impe				cudeso.be
 *		20100525
 *
 **/

// Configuration array
$config = array(	// file containing the IPs
					"iplist" => "BE.txt",
					// logfile with the individual entries
					"logfile" => "Log_BE.txt",
					// what field to use as a separator in iplist
					"separator" => "|",
					// position of the IP (0-based)
					"ippos" => 1,
					// position of the groupby field (0-based)
					"groupby" => 0,
					// newline after a logfile
					"newline" => false
				);

// Array for the resultset
$result = array();
$matchcount = 0;

// walk through the IP list
if (file_exists($config["iplist"])) {
	$file_handle = fopen($config["iplist"], "r");
	while (!feof($file_handle)) {
		$fields = explode("|", fgets($file_handle));
		$key = (string) trim($fields[$config["groupby"]]);
		if (strlen($key) > 0) {
			$data = trim($fields[$config["ippos"]]);
			$result[$key][] =  $data;
		}
	}
	fclose($file_handle);

	// read the log file
	if ((file_exists($config["logfile"])) && count($result) > 0) {
		$logfile = file($config["logfile"]);

		echo "Parsing ".$config["logfile"]."\n".
				"for matches in ".$config["iplist"]."\n".
				"on field pos #".$config["ippos"]."\n".
				"group by field pos #".$config["groupby"]."\n\n\n";
		// walk through the resultset; scan the
		// log file for every entry
		// three foreachs ... optimization
		foreach ($result as $key => $value) {
			echo "\n******************\n$keyn******************\n";
			foreach ($logfile as $line) {
				foreach ($value as $match) {
					// is position 0 and is not BOOLEAN
					if ((strpos($line, $match) === 0) or
					// position bigger than 0
						(strpos($line, $match) > 0)) {

							// we have a match
							echo "$line";
							if ($config["newline"]) echo "\n";
							$matchcount++;
					}
					else $misscount++;
				}
			}
			echo "\n\n\n\n";
		}

		echo "\n\n$matchcount relevant entries found in ".$config["logfile"];
	}
}

?>

