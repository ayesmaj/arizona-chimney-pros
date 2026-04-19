<?php
/**
 * Arizona Chimney Pros — functions.php Snippet
 * ============================================
 * Paste the contents of this file into your active (child) theme's
 * functions.php, OR load it as a tiny mu-plugin:
 *   wp-content/mu-plugins/acp-seo-pages.php
 *
 * Responsibilities:
 *   1. Register the `service_area_page` custom post type
 *   2. Register a clean rewrite so pages live at /{slug}/ (flat URLs)
 *   3. Inject the ACF `schema_json` field into <head> as JSON-LD
 *   4. Output meta title/description from ACF (overrides theme default)
 *   5. Set canonical URL
 *   6. Provide a hook to override the phone number for CallRail
 *
 * IMPORTANT:
 *   - Flush rewrite rules ONCE after installing: Settings → Permalinks → Save.
 *   - Requires ACF (free or Pro). The `get_field` checks make it safe
 *     to load even if ACF is temporarily disabled.
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }


// ─────────────────────────────────────────────
// 1. Register the custom post type
// ─────────────────────────────────────────────
add_action( 'init', 'acp_register_service_area_cpt' );
function acp_register_service_area_cpt() {
    $labels = array(
        'name'          => 'Service Area Pages',
        'singular_name' => 'Service Area Page',
        'add_new'       => 'Add New',
        'add_new_item'  => 'Add New Service Area Page',
        'edit_item'     => 'Edit Service Area Page',
        'new_item'      => 'New Service Area Page',
        'view_item'     => 'View Service Area Page',
        'search_items'  => 'Search Service Area Pages',
        'menu_name'     => 'SEO Pages',
    );

    register_post_type( 'service_area_page', array(
        'labels'             => $labels,
        'public'             => true,
        'show_in_menu'       => true,
        'show_in_rest'       => true,  // Gutenberg-friendly, also ACF REST
        'menu_icon'          => 'dashicons-location-alt',
        'supports'           => array( 'title', 'editor', 'custom-fields', 'thumbnail' ),
        'has_archive'        => false,  // No /service_area_page/ archive — flat URLs only
        'rewrite'            => array(
            'slug'       => '',      // Flat URL: /{post-slug}/ not /service_area_page/{slug}/
            'with_front' => false,
        ),
        'capability_type'    => 'page',
    ) );
}


// ─────────────────────────────────────────────
// 2. Flat URL rewrite — serve /{slug}/ from service_area_page posts
// ─────────────────────────────────────────────
// Because the CPT's rewrite slug is '' above, WordPress registers
// /{post-name}/ URLs directly. This adds an explicit fallback rule
// to avoid collisions with page/post slugs.
add_filter( 'rewrite_rules_array', 'acp_flat_rewrite_rules' );
function acp_flat_rewrite_rules( $rules ) {
    $new = array(
        '([^/]+)/?$' => 'index.php?post_type=service_area_page&name=$matches[1]',
    );
    // Only apply as a fallback — don't shadow real pages/posts.
    return $rules + $new;
}


// ─────────────────────────────────────────────
// 3. Inject JSON-LD schema into <head>
// ─────────────────────────────────────────────
add_action( 'wp_head', 'acp_inject_schema_json', 5 );
function acp_inject_schema_json() {
    if ( ! is_singular( 'service_area_page' ) ) return;
    if ( ! function_exists( 'get_field' ) ) return;

    $schema = get_field( 'schema_json' );
    if ( empty( $schema ) ) return;

    // Defensive: if the stored value was somehow escaped by WP, unescape once.
    $schema = trim( $schema );
    // Strip accidental <script> wrappers if user pasted raw tag in admin.
    $schema = preg_replace( '#^\s*<script[^>]*>#i', '', $schema );
    $schema = preg_replace( '#</script>\s*$#i', '', $schema );

    echo "\n<script type=\"application/ld+json\">\n" . $schema . "\n</script>\n";
}


// ─────────────────────────────────────────────
// 4. Meta title and description from ACF
// ─────────────────────────────────────────────
add_filter( 'pre_get_document_title', 'acp_override_meta_title', 20 );
function acp_override_meta_title( $title ) {
    if ( ! is_singular( 'service_area_page' ) ) return $title;
    if ( ! function_exists( 'get_field' ) ) return $title;

    $meta_title = get_field( 'meta_title' );
    return ! empty( $meta_title ) ? $meta_title : $title;
}

add_action( 'wp_head', 'acp_meta_description', 1 );
function acp_meta_description() {
    if ( ! is_singular( 'service_area_page' ) ) return;
    if ( ! function_exists( 'get_field' ) ) return;

    $desc = get_field( 'meta_description' );
    if ( empty( $desc ) ) return;

    echo '<meta name="description" content="' . esc_attr( $desc ) . '">' . "\n";
}


// ─────────────────────────────────────────────
// 5. Canonical URL
// ─────────────────────────────────────────────
add_action( 'wp_head', 'acp_canonical_url', 2 );
function acp_canonical_url() {
    if ( ! is_singular( 'service_area_page' ) ) return;
    $url = get_permalink();
    echo '<link rel="canonical" href="' . esc_url( $url ) . '">' . "\n";
}


// ─────────────────────────────────────────────
// 6. Phone override for CallRail dynamic number tracking
// ─────────────────────────────────────────────
// Usage: when CallRail is wired up, set these with the tracked number.
// (CallRail's JS will still client-side swap; these are the SSR defaults.)
if ( ! defined( 'ACP_PHONE' ) ) {
    define( 'ACP_PHONE', '(602) 000-0000' );
}
if ( ! defined( 'ACP_PHONE_TEL' ) ) {
    define( 'ACP_PHONE_TEL', '+16020000000' );
}


// ─────────────────────────────────────────────
// 7. Minimal default styling (safe to remove if your theme handles it)
// ─────────────────────────────────────────────
add_action( 'wp_head', 'acp_inline_styles', 10 );
function acp_inline_styles() {
    if ( ! is_singular( 'service_area_page' ) ) return;
    ?>
    <style id="acp-default-styles">
        .acp-page { max-width: 900px; margin: 0 auto; padding: 0 1.25rem; }
        .acp-hero { padding: 3rem 0 2rem; text-align: center; }
        .acp-hero__title { font-size: clamp(1.75rem, 4vw, 2.75rem); line-height: 1.15; margin: 0 0 .5rem; }
        .acp-hero__subtitle { color: #666; font-size: 1.1rem; margin: 0 0 1.25rem; }
        .acp-hero__cta { display: flex; gap: .75rem; justify-content: center; flex-wrap: wrap; }
        .acp-btn { display: inline-block; padding: .75rem 1.5rem; border-radius: 6px; text-decoration: none; font-weight: 600; transition: transform .15s ease; }
        .acp-btn--primary { background: #b8421c; color: #fff; }
        .acp-btn--secondary { background: transparent; color: #b8421c; border: 2px solid #b8421c; }
        .acp-btn--lg { padding: 1rem 2rem; font-size: 1.1rem; }
        .acp-btn:hover { transform: translateY(-1px); color: #fff; }
        .acp-btn--secondary:hover { background: #b8421c; }
        .acp-section { padding: 2rem 0; border-bottom: 1px solid #eee; }
        .acp-section:last-child { border-bottom: none; }
        .acp-section h2 { font-size: 1.5rem; margin: 0 0 1rem; }
        .acp-faq__list { display: grid; gap: 1rem; }
        .acp-faq__item { padding: 1rem; background: #fafafa; border-radius: 6px; }
        .acp-faq__q { font-weight: 600; margin: 0 0 .5rem; }
        .acp-faq__a { margin: 0; color: #444; }
        .acp-cta { background: #fff7f2; text-align: center; }
        .acp-related__list { list-style: none; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(240px,1fr)); gap: .5rem; }
        .acp-related__list a { display: block; padding: .75rem 1rem; background: #f5f5f5; border-radius: 6px; text-decoration: none; color: #333; }
        .acp-related__list a:hover { background: #ececec; }
        .acp-pricing__range { background: #f9f9f9; padding: .75rem 1rem; border-left: 3px solid #b8421c; border-radius: 4px; }
    </style>
    <?php
}
