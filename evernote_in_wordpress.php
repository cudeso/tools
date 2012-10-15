/**
 *	Include Evernote RSS feed in your Wordpress blog
 *
 *	Put this snippet somewhere in your custom Wordpress theme
 *
 *  Reference: http://codex.wordpress.org/Function_Reference/fetch_feed
 *  Reference: http://codex.wordpress.org/Plugin_API/Filter_Reference/wp_feed_cache_transient_lifetime
 *
 *	@version 20121015
 * 	@author Koen Van Impe <koen.vanimpe@cudeso.be>
 *	@license New BSD : http://www.vanimpe.eu/license
 *
 */
  
// When you are changing your theme, the retrieved feed will be cached. You can prevent caching with limiting the lifetime. 
// Don't use this in a production environment!!
/*
function return_1( $seconds ) {
 return 1;
}
add_filter( 'wp_feed_cache_transient_lifetime' , return_1);
*/

// Limit the number of items to retrieve
$maxitems_feed = 10;
$feed_url = "http://www.evernote.com/_whatever_links_to_your_feed/rss.jsp";
$rss = fetch_feed($feed_url . "?max=" . $maxitems_feed . "&sort=2");

if (!is_wp_error( $rss ) ) : // Checks that the object is created correctly 
   // Figure out how many total items there are, but limit it to maxitems_feed. 
   $maxitems = $rss->get_item_quantity($maxitems_feed); 
   // Build an array of all the items, starting with element 0 (first element).
   $rss_items = $rss->get_items(0, $maxitems); 
endif;

if (!($maxitems == 0)) {
	?><h1><?php _e( 'Evernote Feed' ); ?></h1>
	<ul>
	<?php
	foreach($rss_items as $item) {
		?>
		<li>
			<a href='<?php echo esc_url( $item->get_permalink() ); ?>'
			        title='<?php echo 'Posted '.$item->get_date('j F Y | G:i'); ?>'>
			        <?php echo esc_html( $item->get_title() ); ?></a>
		</li>
		<?php
	}
	?>
	</ul>
	<?php
}