<?php
/**
 *	Parse NMAP XML output
 *
 *	@version 20100303
 * 	@author Koen Van Impe <koen.vanimpe@cudeso.be>
 *	@license New BSD : http://www.vanimpe.eu/license
 *
 */
?>
<html>
<head><title>nmap xml file to html</title></head>
<body>
	<form method="POST" enctype="multipart/form-data" action="<?php echo $_SERVER["PHP_SELF"]; ?>">
		XML file: <input type="file" name="xmlfile"	<br />
		<input type="checkbox" checked name="open"> Open <br />
		<input type="checkbox"  name="closed"> Closed <br />
		<input type="checkbox"  name="filtered"> Filtered <br />
		<input type="submit" value="Press"> to upload the file!
	</form>
<?php

if(isset($_FILES['xmlfile'])) {

	// init
	if (trim($_POST["open"]) == "on") 	$printOpen = true;
	else   								$printOpen = false;
	if (trim($_POST["closed"]) == "on") 	$printClosed = true;
	else   								$printClosed = false;
	if (trim($_POST["filtered"]) == "on") 	$printFiltered = true;
	else   								$printFiltered = false;
	$xmlObject = simplexml_load_file($_FILES['xmlfile']['tmp_name']);

	// output the header
	echo "<h1>".(string)$xmlObject["args"]."</h1>";
	echo "<h2>Hosts up: ".(string) $xmlObject->runstats->hosts["up"]." / Hosts down: ".
			(string) $xmlObject->runstats->hosts["down"]. " / Hosts total: ".(string) $xmlObject->runstats->hosts["total"]."</h2>";

	// run through the xml and print hostinfo
	foreach($xmlObject as $host => $value) {

		// Only grab the data if it's host related info
		if ((string) $host == "host") {

			// declare portsarray
			$nmap["ports"] = array();
		
			// get the hostinfo
			echo "<h2>".(string) $value->hostnames->hostname["name"].
						" (".(string) $value->address["addr"]." / ".(string) $value->address["addrtype"].")</h2>";
			echo "<table>";
		
			// put the discovered ports in an array
			foreach ($value->ports->port as $port) {

				if (  ( ((string) $port->state["state"] == "filtered")	and	($printFiltered)) or
					  ( ((string) $port->state["state"] == "closed")	and	($printClosed)) or
					  ( ((string) $port->state["state"] == "open")	and	($printOpen)) 
					) {
					echo "<tr><td>".(string)$port["portid"]."/".(string)$port["protocol"]."</td><td>".
							(string)$port->state["state"]."(".(string)$port->state["reason"].")</td>
							<td>".$port->service["name"]."(".(string)$port->service["product"].")
								</tr>";
				}			
			}
			echo "</table>";
		}
	}

}
?>
</body>
</html>