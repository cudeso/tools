<?php
/**
 *	Convert an IP list to a Google Map
 *
 *	Build on original code from @xme , twitter.com/#!/xme
 *
 *	@version 20130702
 * 	@author Koen Van Impe <koen.vanimpe@cudeso.be>
 * 	
 * TODO: 
 *	- Extend with Bootstrip for pretty URL
 *	- AJAX form submits (jquery form upload)
 * 	- execute nc to enrich with whois data
 *	- textual summaries (for reporting)
 * 	- develop options in formset that are currently disabled
 *
 * Requires PEAR GeoIP & IPv4
 * GeoLiteCity.dat needs to be in path
 *
 */
if (isset($_FILES["datafile"])) {
	$datafile = $_FILES["datafile"]["tmp_name"];

	require_once "Net/GeoIP.php";
	require_once 'Net/IPv4.php';

	$geoip = Net_GeoIP::getInstance("GeoLiteCity.dat");

	$iplist = array();
	$json = "";

	$file_handle = fopen($datafile, "r");
	while (!feof($file_handle)) {
	   $line = fgets($file_handle);
	 if (Net_IPv4::validateIP ( trim($line) )) array_push($iplist, trim($line));
	}
	fclose($file_handle);

	if (count($iplist) > 0) {
		$json = "{ 'items': " . count($iplist) . ", 'map_width': 0, 'map_length': 0, 'map_title': 'none', 'markers': [ ";
		$first = true;
		foreach($iplist as $ip) {
			try {
				$data = $geoip->lookupLocation($ip);
				if (!$first) $json .= ", ";
				else $first = false;
				
				$json .= "	{'country_code': '" . $data->countryCode . "', 'country_name': '". $data->countryName . 
														"', 'lng': " . $data->longitude . ", 'lat': " . $data->latitude .
														", 'ip': '" . $ip . "' }";
			} 
			catch (Exception $e) {
			    // Handle exception
			}
		}	
		$json .= "]}";	
	}
	
	if ($json) {
		?>
		<!DOCTYPE html>
		<html>
		  <head>
		    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
		    <style type="text/css">
		      html { height: 100% }
		      body { height: 100%; margin: 0; padding: 0 }
		      #map-canvas { height: 100% }
		    </style>
		    <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key=INSERT_KEY&amp;sensor=false"></script>
		    <script type="text/javascript" src="http://google-maps-utility-library-v3.googlecode.com/svn/trunk/markerclusterer/src/markerclusterer.js"></script>

		    <script type="text/javascript">
		    //  https://developers.google.com/maps/tutorials/visualizing/earthquakes
		      google.maps.visualRefresh = true;

					var data = <?php echo $json; ?>
					
		      function initialize() {
		        var mapOptions = {
		          center: new google.maps.LatLng(50.8333, 4.3333),
		          zoom: 3,
		          mapTypeId: google.maps.MapTypeId.ROADMAP
		        };
		        var markerlist = [];
		        var infowindow = new google.maps.InfoWindow();
		        var map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

		  			for (var i = 0; i < data.markers.length; i++) {
		  			  var datamarker = data.markers[i];
		          var pos = new google.maps.LatLng(datamarker.lat, datamarker.lng);
		          var content = '<div class="map-content"><h3>' + datamarker.country_code + ' - ' + datamarker.country_name + '</h3><h4>' + datamarker.ip + '</h4></div>';
		          var marker = new google.maps.Marker({
		            position: pos,
		            map: map
		          });
		          google.maps.event.addListener(marker, 'click', (function(marker, content) {
		              return function() {
		                  infowindow.setContent(content);
		                  infowindow.open(map, marker);
		              }
		          })(marker, content));

		          markerlist.push(marker);
		    		}
		    		var markerCluster = new MarkerClusterer(map, markerlist);
		  		}

		      google.maps.event.addDomListener(window, 'load', initialize);

		    </script>
		  </head>
		  <body>
				<a href="<?php echo $_SELF; ?>">Inputform</a>
		    <div id="map_canvas" style="width:1024px; height: 400px"></div>
		  </body>
		</html>
		<?php
	}
}
else {
?>
<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8" />
	<title></title>
	<link rel="stylesheet" href="style.css" />
</head>
<body>
	<h1>Build Google Map from IP data</h1>
	<div id="uploadcontainer">
	<form accept-charset="utf-8" method="post" action="index.php" id="dataform" enctype="multipart/form-data">

		<fieldset>
			<legend>Datafile</legend>

			<label>File with IPs (one per line)</label>
			<input id="fileupload" type="file" name="datafile" />
			
		</fieldset>
		
		<fieldset disabled>
			<legend>Options</legend>

			<label>Map title</label><input type="text" size="60" />
								
			<br /><br />
			
			<label>Map size</label><input type="text" size="5" /> x <input type="text" size="5" />
				
			<br /><br />

			<label>Map centerpoint</label>
				<select>
					<option>Brussels</option>
					<option>Paris</option>
					<option>Amsterdam</option>					
				</select>
				
			<br /><br />
			
			<label>Marker types</label>
				<select>
					<option>Markers</option>
					<option>Heatmap</option>
					<option>Circles</option>					
				</select>

			<br /><br />
			
			<label>Map types</label>
				<select>
					<option>Satellite</option>
					<option>Terrain</option>
					<option>Roadmap</option>					
				</select>
							
			<br /><br />
			
			<label>Enrich with whois data (Team Cymru)</label>
					<input type="checkbox">

			<br /><br />

			<label>Include JSON or external file</label>
				<select>
					<option>External (reusable) JSON file</option>				
					<option>Include JSON</option>
					</select>

			<br /><br />

			<label>Include text summary sorted by #/country</label>
				<input type="checkbox">
			
		</fieldset>

		<input type="submit" value="submit" />
		
	</form>
	</div>

</body>
</html>
<?php	
}
?>
