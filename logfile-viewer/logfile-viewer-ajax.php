<?php

// PHP Script that returns the logfile
// With 'action=update' you can execute an action ; fe. exec()
//

$action = $_GET["action"];
$logfile = "file.log";

if ($action == "update") {
	// Execute update action
	// Sleep function to mimic the time it takes to complete an action
	echo "Action ...";
	sleep(5);
}
else {
	if (file_exists($logfile)) {
		echo nl2br(file_get_contents($logfile));
	}
	else echo "Unable to read logfile $logfile";
}

?>
