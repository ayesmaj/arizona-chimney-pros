<?php
/**
 * Arizona Chimney Pros — Service Area Landing Page Template
 * =========================================================
 * Theme-agnostic single template for the `service_area_page` custom post type.
 *
 * Drop this file into your active theme (or child theme) root:
 *   wp-content/themes/YOUR-THEME/single-service_area_page.php
 *
 * WordPress's template hierarchy will pick it up automatically for any post
 * of post_type=service_area_page — no theme modifications required.
 *
 * It reads all ACF fields registered via acf-fields.json (slug, title,
 * intro, local_section, signs_section, pricing_section, process_section,
 * trust_section, faq_1..4, cta, internal_links, schema_json).
 *
 * Styling is intentionally minimal — layout classes (`acp-*`) are stable
 * CSS hooks; add theme-specific styling in your child theme's style.css.
 *
 * IMPORTANT:
 *   - `schema_json` is injected in <head> via a wp_head action (see
 *     functions-snippet.php) — NOT via this template. This keeps the
 *     JSON-LD out of <body> where page builders could wrap it.
 *   - Phone numbers fall back to a single constant. For CallRail dynamic
 *     tracking, override ACP_PHONE in functions-snippet.php.
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

// Centralized phone constant — override in functions.php for CallRail swap.
if ( ! defined( 'ACP_PHONE' ) ) {
    define( 'ACP_PHONE', '(602) 000-0000' );
}
if ( ! defined( 'ACP_PHONE_TEL' ) ) {
    define( 'ACP_PHONE_TEL', '+16020000000' );
}

get_header();

// ACF helper — safe fetch with fallback.
function acp_field( $name, $default = '' ) {
    if ( ! function_exists( 'get_field' ) ) return $default;
    $v = get_field( $name );
    return $v !== false && $v !== null && $v !== '' ? $v : $default;
}

// Parse semicolon/comma separated internal link list into clean array.
function acp_parse_links( $raw ) {
    if ( empty( $raw ) ) return array();
    // Allow both semicolon and comma separators.
    $parts = preg_split( '/[;,]\s*/', trim( $raw ) );
    return array_values( array_filter( array_map( 'trim', $parts ) ) );
}

// Convert "/gas-fireplace-repair-phoenix/" into "Gas Fireplace Repair in Phoenix".
function acp_link_label( $path ) {
    $clean = trim( $path, '/' );
    $label = str_replace( '-', ' ', $clean );
    $label = ucwords( $label );
    // Upgrade trailing city name readability: "Repair Phoenix" -> "Repair in Phoenix"
    // Simple heuristic: if last word looks like a city (capitalized single word), add "in".
    $parts = explode( ' ', $label );
    if ( count( $parts ) >= 2 ) {
        $last = array_pop( $parts );
        return implode( ' ', $parts ) . ' in ' . $last;
    }
    return $label;
}

while ( have_posts() ) : the_post();

    $title           = acp_field( 'title', get_the_title() );
    $city            = acp_field( 'city' );
    $state           = acp_field( 'state', 'Arizona' );
    $service         = acp_field( 'service' );
    $price_range     = acp_field( 'price_range' );
    $intro           = acp_field( 'intro' );
    $local_section   = acp_field( 'local_section' );
    $signs_section   = acp_field( 'signs_section' );
    $pricing_section = acp_field( 'pricing_section' );
    $process_section = acp_field( 'process_section' );
    $trust_section   = acp_field( 'trust_section' );
    $cta_headline    = acp_field( 'cta_headline', 'Need Help Right Now?' );
    $cta_text        = acp_field( 'cta_text', 'Call for a fast, honest estimate. Same-day appointments available across the Valley.' );
    $internal_links  = acp_parse_links( acp_field( 'internal_links' ) );

    ?>

    <article class="acp-page acp-service-area" itemscope itemtype="https://schema.org/Service">

        <header class="acp-hero">
            <div class="acp-hero__inner">
                <h1 class="acp-hero__title"><?php echo esc_html( $title ); ?></h1>
                <?php if ( $city ) : ?>
                    <p class="acp-hero__subtitle">
                        Fast, local <?php echo esc_html( strtolower( $service ) ); ?> —
                        <?php echo esc_html( $city ); ?>, <?php echo esc_html( $state ); ?>
                    </p>
                <?php endif; ?>
                <div class="acp-hero__cta">
                    <a class="acp-btn acp-btn--primary" href="tel:<?php echo esc_attr( ACP_PHONE_TEL ); ?>">
                        Call <?php echo esc_html( ACP_PHONE ); ?>
                    </a>
                    <a class="acp-btn acp-btn--secondary" href="#acp-contact">Get a Free Estimate</a>
                </div>
            </div>
        </header>

        <?php if ( $intro ) : ?>
            <section class="acp-section acp-intro">
                <div class="acp-section__inner"><?php echo wp_kses_post( $intro ); ?></div>
            </section>
        <?php endif; ?>

        <?php if ( $local_section ) : ?>
            <section class="acp-section acp-local">
                <div class="acp-section__inner">
                    <h2>Why This Happens in <?php echo esc_html( $city ?: 'Arizona' ); ?></h2>
                    <?php echo wp_kses_post( $local_section ); ?>
                </div>
            </section>
        <?php endif; ?>

        <?php if ( $signs_section ) : ?>
            <section class="acp-section acp-signs">
                <div class="acp-section__inner">
                    <h2>Signs You Need <?php echo esc_html( $service ?: 'Service' ); ?></h2>
                    <?php echo wp_kses_post( $signs_section ); ?>
                </div>
            </section>
        <?php endif; ?>

        <?php if ( $pricing_section ) : ?>
            <section class="acp-section acp-pricing">
                <div class="acp-section__inner">
                    <h2>What It Costs<?php echo $city ? ' in ' . esc_html( $city ) : ''; ?></h2>
                    <?php if ( $price_range ) : ?>
                        <p class="acp-pricing__range"
                           itemprop="offers" itemscope itemtype="https://schema.org/AggregateOffer">
                            <strong>Typical range:</strong> <span itemprop="priceRange"><?php echo esc_html( $price_range ); ?></span>
                        </p>
                    <?php endif; ?>
                    <?php echo wp_kses_post( $pricing_section ); ?>
                </div>
            </section>
        <?php endif; ?>

        <?php if ( $process_section ) : ?>
            <section class="acp-section acp-process">
                <div class="acp-section__inner">
                    <h2>How We Fix It</h2>
                    <?php echo wp_kses_post( $process_section ); ?>
                </div>
            </section>
        <?php endif; ?>

        <?php if ( $trust_section ) : ?>
            <section class="acp-section acp-trust">
                <div class="acp-section__inner">
                    <h2>Why Homeowners Trust Arizona Chimney Pros</h2>
                    <?php echo wp_kses_post( $trust_section ); ?>
                </div>
            </section>
        <?php endif; ?>

        <?php
        // FAQs — render up to 4 Q/A pairs. Marked up with microdata so if the
        // JSON-LD is stripped the page still has inline FAQ schema.
        $faqs = array();
        for ( $i = 1; $i <= 4; $i++ ) {
            $q = acp_field( "faq_{$i}_q" );
            $a = acp_field( "faq_{$i}_a" );
            if ( $q && $a ) $faqs[] = array( 'q' => $q, 'a' => $a );
        }
        if ( $faqs ) : ?>
            <section class="acp-section acp-faq" itemscope itemtype="https://schema.org/FAQPage">
                <div class="acp-section__inner">
                    <h2>Frequently Asked Questions</h2>
                    <dl class="acp-faq__list">
                        <?php foreach ( $faqs as $faq ) : ?>
                            <div class="acp-faq__item"
                                 itemscope itemprop="mainEntity"
                                 itemtype="https://schema.org/Question">
                                <dt class="acp-faq__q" itemprop="name"><?php echo esc_html( $faq['q'] ); ?></dt>
                                <dd class="acp-faq__a"
                                    itemscope itemprop="acceptedAnswer"
                                    itemtype="https://schema.org/Answer">
                                    <span itemprop="text"><?php echo esc_html( $faq['a'] ); ?></span>
                                </dd>
                            </div>
                        <?php endforeach; ?>
                    </dl>
                </div>
            </section>
        <?php endif; ?>

        <section id="acp-contact" class="acp-section acp-cta">
            <div class="acp-section__inner">
                <h2><?php echo esc_html( $cta_headline ); ?></h2>
                <p><?php echo esc_html( $cta_text ); ?></p>
                <div class="acp-cta__buttons">
                    <a class="acp-btn acp-btn--primary acp-btn--lg" href="tel:<?php echo esc_attr( ACP_PHONE_TEL ); ?>">
                        Call <?php echo esc_html( ACP_PHONE ); ?>
                    </a>
                </div>
            </div>
        </section>

        <?php if ( $internal_links ) : ?>
            <aside class="acp-section acp-related" aria-label="Related services">
                <div class="acp-section__inner">
                    <h2>Related Services</h2>
                    <ul class="acp-related__list">
                        <?php foreach ( $internal_links as $link ) :
                            // Guard against stray full URLs — we only want internal paths.
                            $href = '/' . ltrim( $link, '/' );
                            $label = acp_link_label( $link );
                        ?>
                            <li><a href="<?php echo esc_url( $href ); ?>"><?php echo esc_html( $label ); ?></a></li>
                        <?php endforeach; ?>
                    </ul>
                </div>
            </aside>
        <?php endif; ?>

    </article>

<?php endwhile;

get_footer();
