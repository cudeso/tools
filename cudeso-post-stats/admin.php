<?php
/*

	Admin pages for Cudeso Post Stats Wordpress plugin
	
	 // First go on creating admin pages for a Wordpress plugin
	 // Different functions per field etc. can probably be optimized

*/

/*

	Copyright 2013  Koen Van Impe
  http://www.vanimpe.eu/license

  Released under BSD-2 license

*/




/**
 *	Create the admin hook
 *
 */
function cps_admin_add_page() {	
	add_options_page( CUDESO_POST_STATS_PLUGIN_NAME . ' Settings', 'Cudeso Post Stats', 'manage_options', __FILE__ , 'cps_plugin_options_page');
}



/**
 *	Define default option settings
 *
 */ 
function cps_add_defaults() {
    $arr = array(	'cps_month_title' => 'Posts per month', 
									'cps_year_title' => 'Posts per year',
									'cps_weekday_title' => 'Posts per weekday',
									'cps_month_width' => '210',
									'cps_year_width' => '210',
									'cps_weekday_width' => '225',																		
									'cps_month_height' => '210',
									'cps_year_height' => '210',
									'cps_weekday_height' => '210',
									'cps_year_legend' => false,
									'cps_weekday_legend' => true,
									'cps_month_legend' => false,
									'cps_month_color' => '#2B7692',
									'cps_year_color' => 'red',
									'cps_weekday_color' => '#004411',
									'cps_month_backgroundcolor' => '#FBF9ED',
									'cps_year_backgroundcolor' => '#FBF9ED',
									'cps_weekday_backgroundcolor' => '#FBF9ED',																		
									'cps_month_charttype' => 'AreaChart',
									'cps_year_charttype' => 'AreaChart',
									'cps_weekday_charttype' => 'PieChart',																		
									);
    update_option(CPS_PLUGIN_OPTIONS, $arr);
}



/**
 *	Define admin sections and fields
 *
 */
function cps_plugin_admin_init() {
	register_setting( CPS_PLUGIN_OPTIONS, CPS_PLUGIN_OPTIONS, 'cps_plugin_options_validate' );
	add_settings_section('cps_plugin_month_section', 'Month - Graph Settings', 'cps_plugin_section_text_month', __FILE__);
	add_settings_section('cps_plugin_year_section', 'Year - Graph Settings', 'cps_plugin_section_text_year', __FILE__);
	add_settings_section('cps_plugin_weekday_section', 'Per Weekday - Graph Settings', 'cps_plugin_section_text_weekday', __FILE__);

	add_settings_field('cps_month_title', 'Title', 'cps_month_title', __FILE__ , 'cps_plugin_month_section');
	add_settings_field('cps_year_title', 'Title', 'cps_year_title', __FILE__ , 'cps_plugin_year_section');
	add_settings_field('cps_weekday_title', 'Title', 'cps_weekday_title', __FILE__ , 'cps_plugin_weekday_section');

	add_settings_field('cps_month_width', 'Width of the graph', 'cps_month_width', __FILE__ , 'cps_plugin_month_section');
	add_settings_field('cps_year_width', 'Width of the graph', 'cps_year_width', __FILE__ , 'cps_plugin_year_section');
	add_settings_field('cps_weekday_width', 'Width of the graph', 'cps_weekday_width', __FILE__ , 'cps_plugin_weekday_section');

	add_settings_field('cps_month_height', 'Height of the graph', 'cps_month_height', __FILE__ , 'cps_plugin_month_section');
	add_settings_field('cps_year_height', 'Height of the graph', 'cps_year_height', __FILE__ , 'cps_plugin_year_section');
	add_settings_field('cps_weekday_height', 'Height of the graph', 'cps_weekday_height', __FILE__ , 'cps_plugin_weekday_section');

	add_settings_field('cps_month_legend', 'Show legend', 'cps_month_legend', __FILE__ , 'cps_plugin_month_section');
	add_settings_field('cps_year_legend', 'Show legend', 'cps_year_legend', __FILE__ , 'cps_plugin_year_section');
	add_settings_field('cps_weekday_legend', 'Show legend', 'cps_weekday_legend', __FILE__ , 'cps_plugin_weekday_section');

	add_settings_field('cps_month_color', 'Color of the graph elements', 'cps_month_color', __FILE__ , 'cps_plugin_month_section');
	add_settings_field('cps_year_color', 'Color of the graph elements', 'cps_year_color', __FILE__ , 'cps_plugin_year_section');
	add_settings_field('cps_weekday_color', 'Color of the graph elements', 'cps_weekday_color', __FILE__ , 'cps_plugin_weekday_section');

	add_settings_field('cps_month_backgroundcolor', 'Background color', 'cps_month_backgroundcolor', __FILE__ , 'cps_plugin_month_section');
	add_settings_field('cps_year_backgroundcolor', 'Background color', 'cps_year_backgroundcolor', __FILE__ , 'cps_plugin_year_section');
	add_settings_field('cps_weekday_backgroundcolor', 'Background color', 'cps_weekday_backgroundcolor', __FILE__ , 'cps_plugin_weekday_section');

	add_settings_field('cps_month_charttype', 'Charttype', 'cps_month_charttype', __FILE__ , 'cps_plugin_month_section');
	add_settings_field('cps_year_charttype', 'Charttype', 'cps_year_charttype', __FILE__ , 'cps_plugin_year_section');
	add_settings_field('cps_weekday_charttype', 'Charttype', 'cps_weekday_charttype', __FILE__ , 'cps_plugin_weekday_section');
}



/**
 *	Chart type for month
 *
 */
function cps_month_charttype() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	$items = cps_get_list_of_charttypes();
		echo "<select id='cps_month_charttype' name='cps_plugin_options[cps_month_charttype]'>";
		foreach($items as $item) {
			$selected = ($options['cps_month_charttype']==$item) ? 'selected="selected"' : '';
			echo "<option value='$item' $selected>$item</option>";
		}
		echo "</select>";	
}



/**
 *	Chart type per year
 *
 */
function cps_year_charttype() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	$items = cps_get_list_of_charttypes();
		echo "<select id='cps_year_charttype' name='cps_plugin_options[cps_year_charttype]'>";
		foreach($items as $item) {
			$selected = ($options['cps_year_charttype']==$item) ? 'selected="selected"' : '';
			echo "<option value='$item' $selected>$item</option>";
		}
		echo "</select>";	
}



/**
 *	Chart type per weekday
 *
 */
function cps_weekday_charttype() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	$items = cps_get_list_of_charttypes();
		echo "<select id='cps_weekday_charttype' name='cps_plugin_options[cps_weekday_charttype]'>";
		foreach($items as $item) {
			$selected = ($options['cps_weekday_charttype']==$item) ? 'selected="selected"' : '';
			echo "<option value='$item' $selected>$item</option>";
		}
		echo "</select>";	
}



/**
 * List of charts 
 * 
 */
function cps_get_list_of_charttypes() {
	return array("AreaChart", "PieChart");
}



/**
 *	Default title for year graph
 *
 */
function cps_year_title() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_year_title' name='cps_plugin_options[cps_year_title]' size='40' maxlength='60' type='text' value='{$options['cps_year_title']}' />";
}



/**
 *	Default title for month graph
 *
 */
function cps_month_title() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_month_title' name='cps_plugin_options[cps_month_title]' size='40' maxlength='60' type='text' value='{$options['cps_month_title']}' />";
}



/**
 *	Default title for weekday graph
 *
 */
function cps_weekday_title() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_weekday_title' name='cps_plugin_options[cps_weekday_title]' size='40' maxlength='60' type='text' value='{$options['cps_weekday_title']}' />";
}



/**
 *	Default color for year
 *
 */
function cps_year_color() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_year_color' name='cps_plugin_options[cps_year_color]' size='7' maxlength='7' type='text' value='{$options['cps_year_color']}' />";
}



/**
 *	Default color for month
 *
 */
function cps_month_color() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_month_color' name='cps_plugin_options[cps_month_color]' size='7' maxlength='7' type='text' value='{$options['cps_month_color']}' />";
}


/**
 *	Default color for weekday
 *
 */
function cps_weekday_color() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_weekday_color' name='cps_plugin_options[cps_weekday_color]' size='7' maxlength='7' type='text' value='{$options['cps_weekday_color']}' />";
}



/**
 *	Default backgroundcolor for year
 *
 */
function cps_year_backgroundcolor() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_year_backgroundcolor' name='cps_plugin_options[cps_year_backgroundcolor]' size='7' maxlength='7' type='text' value='{$options['cps_year_backgroundcolor']}' />";
}



/**
 *	Default backgroundcolor for month
 *
 */
function cps_month_backgroundcolor() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_month_backgroundcolor' name='cps_plugin_options[cps_month_backgroundcolor]' size='7' maxlength='7' type='text' value='{$options['cps_month_backgroundcolor']}' />";
}


/**
 *	Default backgroundcolor for weekday
 *
 */
function cps_weekday_backgroundcolor() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_weekday_backgroundcolor' name='cps_plugin_options[cps_weekday_backgroundcolor]' size='7' maxlength='7' type='text' value='{$options['cps_weekday_backgroundcolor']}' />";
}



/**
 *	Default width for month
 *
 */
function cps_month_width() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_month_width' name='cps_plugin_options[cps_month_width]' size='4' maxlength='4' type='text' value='{$options['cps_month_width']}' />";
}



/**
 *	Default width for year
 *
 */
function cps_year_width() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_year_width' name='cps_plugin_options[cps_year_width]' size='4' maxlength='4' type='text' value='{$options['cps_year_width']}' />";
}


/**
 *	Default width for weekday
 *
 */
function cps_weekday_width() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_weekday_width' name='cps_plugin_options[cps_weekday_width]' size='4' maxlength='4' type='text' value='{$options['cps_weekday_width']}' />";
}



/**
 *	Default height for month
 *
 */
function cps_month_height() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_month_height' name='cps_plugin_options[cps_month_height]' size='4' maxlength='4' type='text' value='{$options['cps_month_height']}' />";
}



/*
 *	Default height for year
 *
 */
function cps_year_height() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_year_height' name='cps_plugin_options[cps_year_height]' size='4' maxlength='4' type='text' value='{$options['cps_year_height']}' />";
}



/**
 *	Default height for weekday
 *
 */
function cps_weekday_height() {
	$options = get_option(CPS_PLUGIN_OPTIONS);
	echo "<input id='cps_weekday_height' name='cps_plugin_options[cps_weekday_height]' size='4' maxlength='4' type='text' value='{$options['cps_weekday_height']}' />";
}



/**
 *	Show legend for month?
 *
 */
function cps_month_legend() {
	$options = get_option(CPS_PLUGIN_OPTIONS);	
	if($options['cps_month_legend']) { $checked = ' checked="checked" '; }	
	echo "<input ".$checked." id='cps_month_legend' name='cps_plugin_options[cps_month_legend]' type='checkbox' />";
}



/**
 *	Show legend for year?
 *
 */
function cps_year_legend() {
	$options = get_option(CPS_PLUGIN_OPTIONS);	
	if($options['cps_year_legend']) { $checked = ' checked="checked" '; }	
	echo "<input ".$checked." id='cps_year_legend' name='cps_plugin_options[cps_year_legend]' type='checkbox' />";
}



/**
 *	Show legend for weekday
 *
 */
function cps_weekday_legend() {
	$options = get_option(CPS_PLUGIN_OPTIONS);	
	if($options['cps_weekday_legend']) { $checked = ' checked="checked" '; }	
	echo "<input ".$checked." id='cps_weekday_legend' name='cps_plugin_options[cps_weekday_legend]' type='checkbox' />";
}



/**
 *	Section 'month
 *
 */
function cps_plugin_section_text_month() {
	echo '<p>Settings to be used for creating the <strong>month</strong> graph.</p>';
}



/**
 *	Section 'year'
 *
 */
function cps_plugin_section_text_year() {
	echo '<p>Settings to be used for creating the <strong>year</strong> graph.</p>';
}



/**
 *	Section 'weekday'
 *
 */
function cps_plugin_section_text_weekday() {
	echo '<p>Settings to be used for creating the <strong>weekday</strong> graph.</p>';
}



/**
 *	Validate the input
 *
 */

function cps_plugin_options_validate($input) {

	if ($input['cps_weekday_legend'] == "on") $newinput['cps_weekday_legend']  = true;
	if ($input['cps_month_legend'] == "on") $newinput['cps_month_legend']  = true;
	if ($input['cps_year_legend'] == "on") $newinput['cps_year_legend']  = true;		

	$newinput['cps_weekday_height'] =  intval($input['cps_weekday_height']);			
	$newinput['cps_month_height'] =  intval($input['cps_month_height']);			
	$newinput['cps_year_height'] =  intval($input['cps_year_height']);			
	
	$newinput['cps_weekday_width'] =  intval($input['cps_weekday_width']);			
	$newinput['cps_month_width'] =  intval($input['cps_month_width']);			
	$newinput['cps_year_width'] =  intval($input['cps_year_width']);			

	$newinput['cps_month_title'] = (string) wp_filter_nohtml_kses(substr($input['cps_month_title'] , 0 , 60));
	$newinput['cps_month_backgroundcolor'] =  (string) wp_filter_nohtml_kses(substr($input['cps_month_backgroundcolor'] , 0 , 7));
	$newinput['cps_month_color'] =  (string) wp_filter_nohtml_kses(substr($input['cps_month_color'] , 0 , 7));
	$newinput['cps_month_charttype'] =  (string) wp_filter_nohtml_kses(substr($input['cps_month_charttype'] , 0 , 50));

	$newinput['cps_year_title'] = (string) wp_filter_nohtml_kses(substr($input['cps_year_title'] , 0 , 60));
	$newinput['cps_year_backgroundcolor'] =  (string) wp_filter_nohtml_kses(substr($input['cps_year_backgroundcolor'] , 0 , 7));
	$newinput['cps_year_color'] =  (string) wp_filter_nohtml_kses(substr($input['cps_year_color'] , 0 , 7));
	$newinput['cps_year_charttype'] =  (string) wp_filter_nohtml_kses(substr($input['cps_year_charttype'] , 0 , 50));

	$newinput['cps_weekday_title'] = (string) wp_filter_nohtml_kses(substr($input['cps_weekday_title'] , 0 , 60));
	$newinput['cps_weekday_backgroundcolor'] =  (string) wp_filter_nohtml_kses(substr($input['cps_weekday_backgroundcolor'] , 0 , 7));	
	$newinput['cps_weekday_color'] =  (string) wp_filter_nohtml_kses(substr($input['cps_weekday_color'] , 0 , 7));
	$newinput['cps_weekday_charttype'] =  (string) wp_filter_nohtml_kses(substr($input['cps_weekday_charttype'] , 0 , 50));
	
	return $newinput;
}



/**
 *	Basic layout for admin page for plugin
 *
 */

function cps_plugin_options_page() {
	?>
	<div>
	<h2><?php echo CUDESO_POST_STATS_PLUGIN_NAME; ?></h2>
	<p>Configure the way the Google Charts are displayed. You can include the charts with
		<pre>print cps_get_googlechart_per_month();	</pre>
		<pre>print cps_get_googlechart_per_year();	</pre>
		<pre>print cps_get_googlechart_per_weekday();	</pre>				
	</p>
	<form action="options.php" method="post">
	<?php settings_fields(CPS_PLUGIN_OPTIONS); ?>
	<?php do_settings_sections(__FILE__); ?> 
	<p class="submit"><input class="button-primary" name="Submit" type="submit" value="<?php esc_attr_e('Save Changes'); ?>" /></p>
	</form></div> 
	<?php
}


?>