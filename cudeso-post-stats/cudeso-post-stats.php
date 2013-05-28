<?php
/*
Plugin Name: cudeso Post Stats
Description: Display statistics about the number of posts
Version: 1.0
Author: Koen Van Impe
Author URI: http://www.vanimpe.eu/
Plugin URI: http://www.vanimpe.eu/
*/

/*

	Copyright 2013  Koen Van Impe
  http://www.vanimpe.eu/license

  Released under BSD-2 license

*/

/*
  Used resources:
    http://www.presscoders.com/2010/05/wordpress-settings-api-explained/
	
*/

// Set variables for paths
define('CUDESO_POST_STATS_DIR', plugin_dir_path(__FILE__));
define('CUDESO_POST_STATS_URL', plugin_dir_url(__FILE__));
define('CUDESO_POST_STATS_PLUGIN_NAME', 'cudeso Post Stats');
define('CPS_PLUGIN_OPTIONS', 'cps_plugin_options');

// Define the version key and value ; set the value
if (!defined('CUDESO_POST_STATS_VERSION_KEY')) define('CUDESO_POST_STATS_VERSION_KEY', 'cudeso_posts_stats_version');
if (!defined('CUDESO_POST_STATS_VERSION_NUM')) define('CUDESO_POST_STATS_VERSION_NUM', '1.0.0');
add_option(CUDESO_POST_STATS_VERSION_KEY, CUDESO_POST_STATS_VERSION_NUM);

// Include Admin page
require_once( CUDESO_POST_STATS_DIR . "admin.php");

// Add the Google Chart scripts to the head
add_action( 'wp_enqueue_scripts' , 'cps_wp_enqueue_googlechartjs' );
add_action( 'wp_head' , 'cps_add_googlechartjs');


// Setup the admin pages
add_action('admin_menu', 'cps_admin_add_page');
add_action('admin_init', 'cps_plugin_admin_init');

register_activation_hook(__FILE__, 'cps_add_defaults');



/**
 *	Build a google graph javascript string
 *
 *	$charttype				string		Type of the chart
 *	$title						string		Title of the chart
 *	$data							string		Data for the chart, converted from an array
 *	$width						integer		the width of the graph object
 *	$height						integer		the height of the graph object
 *	$color						string		default color to use to stroke the graphs
 *	$backgroundcolor	string		the backgroundcolor for the graph
 *
 *	@return	string or false
 */
function cps_get_googlechart($charttype, $title, $data, $legend, $width = 200 , $height = 200 , $color = '#004411', $backgroundcolor = '#FBF9ED') {

	$js = false;

	if ($title != "" and strlen($data) > 0 and $width > 0 and $height > 0) {
		$title_function = preg_replace(array('/[^[:alnum:]]/', '/(\s+|\-{2,})/'), array('', '-'), $title);

		if ($legend) $js_legend = "";
		else $js_legend = " , legend: {position: 'none'} ";

		$js_color = " 'colors':['" . $color . "'] ,  ";
		if ($charttype == "PieChart") {
			$chart = "new google.visualization.PieChart(document.getElementById('chart_div_" . $title_function . "'));";
			$js_color = "";
		}
		elseif ($charttype == "AreaChart") $chart = "new google.visualization.AreaChart(document.getElementById('chart_div_" . $title_function . "'));";		
		else $chart = "new google.visualization.PieChart(document.getElementById('chart_div_" . $title_function . "'));";
		
		$js = "		
		<script type=\"text/javascript\">
			  function drawChart() {
				  var data = new google.visualization.DataTable();
				  data.addColumn('string', '');
				  data.addColumn('number', 'Posts');
				  data.addRows( [ " . $data . " ]);
				  var options = {'title':'" . $title . "', 'backgroundColor': '" . $backgroundcolor . "', 'width':" . $width . ", " . $js_color . " 'height':" . $height . $js_legend . " };
				  var chart = " . $chart . "
				  chart.draw(data, options);
				}
			google.setOnLoadCallback(drawChart);				
			</script>
		  
			<div id=\"chart_div_" . $title_function . "\"></div>
		";
	}
	return $js;
}



/**
 *	Load the number of posts per weekday and build a Google Chart
 *
 *	@return	string or false
 */
function cps_get_googlechart_per_weekday() {
	
	// First get the database values
	$posts_per_weekday = cps_get_posts_per_weekday();
	
	if ($posts_per_weekday) {
		
		// Build the javascript datarow
		$js_posts_per_weekday = "";
		foreach ($posts_per_weekday as $el) {
			if (strlen($js_posts_per_weekday) > 0) $js_posts_per_weekday .= " , ";
			$js_posts_per_weekday .= " [ '$el->dayname', $el->qt ] ";
		}
		
		if (strlen($js_posts_per_weekday) > 0) {
			$options = get_option(CPS_PLUGIN_OPTIONS);
			
			$width = $options["cps_weekday_width"];
			$height= $options["cps_weekday_height"];
			$title = $options["cps_weekday_title"];
			$legend = $options["cps_weekday_legend"];
			$color = $options["cps_weekday_color"];
			$backgroundcolor = $options["cps_weekday_backgroundcolor"];
			$charttype = $options["cps_weekday_charttype"];
			
			return cps_get_googlechart($charttype, $title, $js_posts_per_weekday, $legend, $width, $height, $color, $backgroundcolor);			
		}
		else return false;
	}
	else return false;
}



/**
 *	Load the number of posts per year and build a Google Chart
 *
 *	@return	string or false
 */
function cps_get_googlechart_per_year() {
	
	// First get the database values
	$posts_per_year = cps_get_posts_per_year();
	
	if ($posts_per_year) {
		
		// Build the javascript datarow
		$js_posts_per_year = "";
		foreach ($posts_per_year as $el) {
			if (strlen($js_posts_per_year) > 0) $js_posts_per_year .= " , ";
			$js_posts_per_year .= " [ '$el->year', $el->qt ] ";
		}
		
		if (strlen($js_posts_per_year) > 0) {
			$options = get_option(CPS_PLUGIN_OPTIONS);
			
			$width = $options["cps_year_width"];
			$height= $options["cps_year_height"];
			$title = $options["cps_year_title"];
			$legend = $options["cps_year_legend"];
			$color = $options["cps_year_color"];
			$backgroundcolor = $options["cps_year_backgroundcolor"];
			$charttype = $options["cps_year_charttype"];

			return cps_get_googlechart($charttype, $title, $js_posts_per_year, $legend, $width, $height, $color, $backgroundcolor);			
		}
		else return false;
	}
	else return false;
}



/**
 *	Load the number of posts per month and build a Google Chart
 *
 *	@return	string or false
 */
function cps_get_googlechart_per_month() {
	
	// First get the database values
	$posts_per_month = cps_get_posts_per_month();
	
	if ($posts_per_month) {
		
		// Build the javascript datarow
		$js_posts_per_month = "";
		foreach ($posts_per_month as $el) {
			if (strlen($js_posts_per_month) > 0) $js_posts_per_month .= " , ";
			$e = date('M', mktime(0, 0, 0, $el->month));
			$js_posts_per_month .= " [ '$e', $el->qt ] ";
		}
		
		if (strlen($js_posts_per_month) > 0) {
			$options = get_option(CPS_PLUGIN_OPTIONS);
			
			$width = $options["cps_month_width"];
			$height= $options["cps_month_height"];
			$title = $options["cps_month_title"];
			$legend = $options["cps_month_legend"];
			$color = $options["cps_month_color"];
			$backgroundcolor = $options["cps_month_backgroundcolor"];
			$charttype = $options["cps_month_charttype"];

			return cps_get_googlechart($charttype, $title, $js_posts_per_month, $legend, $width, $height, $color, $backgroundcolor);			
		}
		else return false;
	}
	else return false;
}



/**
 * Get the number of posts per weekday
 *
 *	@return	array or false
 */
function cps_get_posts_per_weekday() {
	global $wpdb;
	
	$posts_per_dayname = $wpdb->get_results("SELECT DAYNAME(post_date) AS dayname, DAYOFWEEK(post_date) as dayofweek, COUNT(*) AS qt FROM $wpdb->posts WHERE post_type = 'post' GROUP BY dayname,dayofweek ORDER BY dayofweek ASC;", 0);

	if (is_array($posts_per_dayname) and count($posts_per_dayname) > 0) return $posts_per_dayname;
	else return false;
}



/**
 * Get the number of posts per month
 *
 *	@return	array or false
 */
function cps_get_posts_per_month() {
	global $wpdb;
	
	$posts_per_month = $wpdb->get_results("SELECT MONTH(post_date) AS month, COUNT(*) AS qt FROM $wpdb->posts WHERE post_type = 'post' GROUP BY month;", 0);

	if (is_array($posts_per_month) and count($posts_per_month) > 0) return $posts_per_month;
	else return false;
}



/**
 * Get the number of posts per year
 *
 *	@return	array or false
 */
function cps_get_posts_per_year() {
	global $wpdb;
	
	$posts_per_year = $wpdb->get_results("SELECT YEAR(post_date) AS year, COUNT(*) AS qt FROM $wpdb->posts WHERE post_type = 'post' GROUP BY year;", 0);

	if (is_array($posts_per_year) and count($posts_per_year) > 0) return $posts_per_year;
	else return false;
}



/**
 *	Add the external Google Chart Javascript file
 *		called in wp_enqueue_scripts
 *
 */
function cps_wp_enqueue_googlechartjs() {
	wp_register_script('googlechartapi', 'https://www.google.com/jsapi');
	wp_enqueue_script('googlechartapi');	
}



/**
 *	Add the Google Chart API to the head
 *		called in wp_head
 *
 */
function cps_add_googlechartjs() {
	?>
	<!-- Load the Google Chart API -- cudeso Post Stats / wordpress module -->
	<script type="text/javascript">
		google.load('visualization', '1.0', {'packages':['corechart']});
	</script>
	<?php
}
?>