<?php
session_start();

$misp_key = "<yourkey>";
$misp_server = "<misp_server>";
$misp_verify_cert = False;
$sightings_url = $misp_server . "/sightings/add";
$source = "";
$sighting_type = 0;
$selector = "";
$value = "";

// We are either called by attribute_id, attribute_uuid or by value
if (isset($_REQUEST["attribute_id"])) {
    $value = $_REQUEST["attribute_id"];
    $selector = "id";
}
elseif (isset($_REQUEST["attribute_uuid"])) {
    $value = $_REQUEST["attribute_uuid"];
    $selector = "uuid";
}
elseif (isset($_REQUEST["indicator"])) {
    $value = $_REQUEST["indicator"];
    $selector = "value";
}

if (isset($value)) {
    if (isset($_REQUEST["source"])) {
    	$source = filter_var($_REQUEST["source"], FILTER_SANITIZE_STRING);
    }

    if (isset($_REQUEST["sighting_type"])) {
	    $sighting_type = abs(filter_var($_REQUEST["sighting_type"], FILTER_SANITIZE_NUMBER_INT));
        if ($sighting_type > 2) $sighting_type = False;  // 0: sighting ; 1: false positive ; 2: expiration
    }

    $ch = curl_init($sightings_url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, $misp_verify_cert);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, $misp_verify_cert);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array("Accept: application/json","Content-Type: application/json","Authorization: ".$misp_key)); 

    $jsonData = array(
        "$selector" => $value,
        "source" => $source,
        "type" => $sighting_type 
    );

    $jsonDataEncoded = json_encode($jsonData);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonDataEncoded);
    $result = curl_exec($ch);

    ?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>Report Sighting</title>
</head>
<body><h3>Sighting sent to <?php echo $misp_server; ?></h3>
</body>
</html>
<?php  
}
else {
    echo "<h3>Sighting not sent, invalid parameters supplied.</h3>";
}
?>
