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
 * Renders a UNION-SCHEMA page — fields that don't apply to the current
 * page_type are simply empty and skipped via `if ( $field )` guards.
 * Supported page_types:
 *   - service_city   (intro, local, problems_we_fix, signs, pricing,
 *                     process, warranty, brands, service_area, trust)
 *   - problem_city   (intro, local, causes, signs, danger, diy_checklist,
 *                     process, pricing, trust)
 *   - cost_page      (intro, local, pricing_table, factors,
 *                     repair_vs_replace, budget_tips, process, trust)
 *   - comparison     (intro, option_a, option_b, comparison_table,
 *                     cost_difference, maintenance, local_fit,
 *                     recommendation, trust)
 *   - location_hub   (intro, local, service_area, brands, trust)
 *
 * Styling is intentionally minimal — layout classes (`acp-*`) are stable
 * CSS hooks; add theme-specific styling in your child theme's style.css.
 *
 * IMPORTANT:
 *   - `schema_json` is injected in <head> via a wp_head action (see
 *     functions-snippet.php) — NOT via this template.
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
    $parts = preg_split( '/[;,]\s*/', trim( $raw ) );
    return array_values( array_filter( array_map( 'trim', $parts ) ) );
}

// Convert "/gas-fireplace-repair-phoenix/" into "Gas Fireplace Repair in Phoenix".
function acp_link_label( $path ) {
    $clean = trim( $path, '/' );
    $label = str_replace( '-', ' ', $clean );
    $label = ucwords( $label );
    $parts = explode( ' ', $label );
    if ( count( $parts ) >= 2 ) {
        $last = array_pop( $parts );
        return implode( ' ', $parts ) . ' in ' . $last;
    }
    return $label;
}

// Render a section with a heading if the content field is non-empty.
function acp_render_section( $heading, $content, $extra_class = '' ) {
    if ( ! $content ) return;
    $class = trim( 'acp-section ' . $extra_class );
    ?>
    <section class="<?php echo esc_attr( $class ); ?>">
        <div class="acp-section__inner">
            <h2><?php echo esc_html( $heading ); ?></h2>
            <?php echo wp_kses_post( $content ); ?>
        </div>
    </section>
    <?php
}

while ( have_posts() ) : the_post();

    // Core identity fields.
    $title           = acp_field( 'title', get_the_title() );
    $city            = acp_field( 'city' );
    $state           = acp_field( 'state', 'Arizona' );
    $service         = acp_field( 'service' );
    $page_type       = acp_field( 'page_type', 'service_city' );
    $price_range     = acp_field( 'price_range' );

    // Content fields — union across page types.
    $intro                      = acp_field( 'intro' );
    $local_section              = acp_field( 'local_section' );
    $signs_section              = acp_field( 'signs_section' );
    $pricing_section            = acp_field( 'pricing_section' );
    $process_section            = acp_field( 'process_section' );
    $trust_section              = acp_field( 'trust_section' );

    // Service-city specific.
    $problems_we_fix_section    = acp_field( 'problems_we_fix_section' );
    $warranty_section           = acp_field( 'warranty_section' );

    // Problem-city specific.
    $causes_section             = acp_field( 'causes_section' );
    $danger_section             = acp_field( 'danger_section' );
    $diy_checklist_section      = acp_field( 'diy_checklist_section' );

    // Cost-page specific.
    $pricing_table_section      = acp_field( 'pricing_table_section' );
    $factors_section            = acp_field( 'factors_section' );
    $repair_vs_replace_section  = acp_field( 'repair_vs_replace_section' );
    $budget_tips_section        = acp_field( 'budget_tips_section' );

    // Comparison specific.
    $option_a_section           = acp_field( 'option_a_section' );
    $option_b_section           = acp_field( 'option_b_section' );
    $comparison_table_section   = acp_field( 'comparison_table_section' );
    $cost_difference_section    = acp_field( 'cost_difference_section' );
    $maintenance_section        = acp_field( 'maintenance_section' );
    $local_fit_section          = acp_field( 'local_fit_section' );
    $recommendation_section     = acp_field( 'recommendation_section' );

    // Locally-injected (non-Claude).
    $brands_serviced_section    = acp_field( 'brands_serviced_section' );
    $service_area_section       = acp_field( 'service_area_section' );

    // CTA + links.
    $cta_headline    = acp_field( 'cta_headline', 'Need Help Right Now?' );
    $cta_text        = acp_field( 'cta_text', 'Call for a fast, honest estimate. Same-day appointments available across the Valley.' );
    $internal_links  = acp_parse_links( acp_field( 'internal_links' ) );

    // Testimonials — 3 picks, locally injected.
    $reviews = array();
    for ( $i = 1; $i <= 3; $i++ ) {
        $author = acp_field( "review_{$i}_author" );
        $text   = acp_field( "review_{$i}_text" );
        if ( $author && $text ) {
            $reviews[] = array(
                'author' => $author,
                'text'   => $text,
                'city'   => acp_field( "review_{$i}_city" ),
                'rating' => (int) acp_field( "review_{$i}_rating", 5 ),
            );
        }
    }
    ?>

    <article class="acp-page acp-page--<?php echo esc_attr( $page_type ); ?>"
             itemscope itemtype="https://schema.org/Service">

        <header class="acp-hero">
            <div class="acp-hero__inner">
                <h1 class="acp-hero__title"><?php echo esc_html( $title ); ?></h1>
                <?php if ( $city ) : ?>
                    <p class="acp-hero__subtitle">
                        Fast, local <?php echo esc_html( strtolower( $service ) ); ?> —
                        <?php echo esc_html( $city ); ?>, <?php echo esc_html( $state ); ?>
                    </p>
                <?php endif; ?>
                <?php if ( $reviews ) : ?>
                    <p class="acp-hero__rating" aria-label="5 star rated across the Phoenix metro">
                        <span class="acp-hero__stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
                        <span class="acp-hero__rating-text">Rated 5/5 by Valley homeowners</span>
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

        <?php
        // -----------------------------------------------------------------
        // PAGE-TYPE-AWARE SECTION ORDER
        // Each case picks which sections render and in what order.
        // -----------------------------------------------------------------
        if ( $page_type === 'comparison' ) :
            // Comparison pages: options → table → cost diff → maintenance → local fit → recommendation.
            acp_render_section( 'Option A: Overview', $option_a_section, 'acp-option-a' );
            acp_render_section( 'Option B: Overview', $option_b_section, 'acp-option-b' );
            acp_render_section( 'Side-by-Side Comparison', $comparison_table_section, 'acp-comparison-table' );
            acp_render_section( 'Cost Difference Over 10 Years', $cost_difference_section, 'acp-cost-difference' );
            acp_render_section( 'Maintenance Reality', $maintenance_section, 'acp-maintenance' );
            acp_render_section( 'Which Fits Arizona Better?', $local_fit_section, 'acp-local-fit' );
            acp_render_section( 'Our Recommendation', $recommendation_section, 'acp-recommendation' );

        elseif ( $page_type === 'cost_page' ) :
            // Cost pages: local → pricing table → factors → repair vs replace → budget tips → process.
            if ( $local_section ) acp_render_section(
                'Why Pricing in ' . ( $city ?: 'Arizona' ) . ' Is Different',
                $local_section, 'acp-local'
            );
            acp_render_section( 'Typical Prices in ' . ( $city ?: 'Arizona' ), $pricing_table_section, 'acp-pricing-table' );
            acp_render_section( 'What Drives the Price Up or Down', $factors_section, 'acp-factors' );
            acp_render_section( 'Repair or Replace?', $repair_vs_replace_section, 'acp-repair-replace' );
            acp_render_section( 'How to Save Without Cutting Corners', $budget_tips_section, 'acp-budget' );
            acp_render_section( 'How We Quote Honestly', $process_section, 'acp-process' );

        elseif ( $page_type === 'problem_city' ) :
            // Problem pages: local → causes → signs → danger → diy → process → pricing.
            if ( $local_section ) acp_render_section(
                'Why This Happens in ' . ( $city ?: 'Arizona' ),
                $local_section, 'acp-local'
            );
            acp_render_section( 'What Actually Causes This', $causes_section, 'acp-causes' );
            if ( $signs_section ) acp_render_section(
                'Warning Signs to Watch For',
                $signs_section, 'acp-signs'
            );
            acp_render_section( 'Safe to Wait vs Call Right Now', $danger_section, 'acp-danger' );
            acp_render_section( 'What You Can Safely Check Yourself', $diy_checklist_section, 'acp-diy' );
            if ( $process_section ) acp_render_section(
                'How We Fix It',
                $process_section, 'acp-process'
            );
            if ( $pricing_section ) {
                ?>
                <section class="acp-section acp-pricing">
                    <div class="acp-section__inner">
                        <h2>What It Costs<?php echo $city ? ' in ' . esc_html( $city ) : ''; ?></h2>
                        <?php if ( $price_range ) : ?>
                            <p class="acp-pricing__range"
                               itemprop="offers" itemscope itemtype="https://schema.org/AggregateOffer">
                                <strong>Typical range:</strong>
                                <span itemprop="priceRange"><?php echo esc_html( $price_range ); ?></span>
                            </p>
                        <?php endif; ?>
                        <?php echo wp_kses_post( $pricing_section ); ?>
                    </div>
                </section>
                <?php
            }

        elseif ( $page_type === 'location_hub' ) :
            // Hub pages: local → service_area → brands.
            if ( $local_section ) acp_render_section(
                'About ' . ( $city ?: 'the Area' ),
                $local_section, 'acp-local'
            );
            acp_render_section( 'Cities We Serve', $service_area_section, 'acp-service-area' );
            acp_render_section( 'Brands We Service', $brands_serviced_section, 'acp-brands' );

        else :
            // service_city (default): local → problems_we_fix → signs → pricing → process → warranty → brands.
            if ( $local_section ) acp_render_section(
                'Why This Happens in ' . ( $city ?: 'Arizona' ),
                $local_section, 'acp-local'
            );
            acp_render_section(
                'Problems We Fix',
                $problems_we_fix_section, 'acp-problems'
            );
            if ( $signs_section ) acp_render_section(
                'Signs You Need ' . ( $service ?: 'Service' ),
                $signs_section, 'acp-signs'
            );
            if ( $pricing_section ) {
                ?>
                <section class="acp-section acp-pricing">
                    <div class="acp-section__inner">
                        <h2>What It Costs<?php echo $city ? ' in ' . esc_html( $city ) : ''; ?></h2>
                        <?php if ( $price_range ) : ?>
                            <p class="acp-pricing__range"
                               itemprop="offers" itemscope itemtype="https://schema.org/AggregateOffer">
                                <strong>Typical range:</strong>
                                <span itemprop="priceRange"><?php echo esc_html( $price_range ); ?></span>
                            </p>
                        <?php endif; ?>
                        <?php echo wp_kses_post( $pricing_section ); ?>
                    </div>
                </section>
                <?php
            }
            if ( $process_section ) acp_render_section(
                'How We Fix It',
                $process_section, 'acp-process'
            );
            acp_render_section( 'Warranty & Workmanship Guarantee', $warranty_section, 'acp-warranty' );
            acp_render_section( 'Brands We Service', $brands_serviced_section, 'acp-brands' );
            acp_render_section( 'Cities We Serve', $service_area_section, 'acp-service-area' );
        endif;
        ?>

        <?php
        // -----------------------------------------------------------------
        // TESTIMONIALS — rendered for all page types when reviews exist.
        // Schema.org Review microdata for inline fallback if JSON-LD is stripped.
        // -----------------------------------------------------------------
        if ( $reviews ) : ?>
            <section class="acp-section acp-testimonials"
                     itemscope itemtype="https://schema.org/LocalBusiness">
                <meta itemprop="name" content="Arizona Chimney Pros" />
                <div class="acp-section__inner">
                    <h2>What <?php echo esc_html( $city ?: 'Arizona' ); ?> Homeowners Say</h2>
                    <div class="acp-testimonials__grid">
                        <?php foreach ( $reviews as $rv ) : ?>
                            <figure class="acp-testimonial"
                                    itemprop="review"
                                    itemscope itemtype="https://schema.org/Review">
                                <div class="acp-testimonial__rating"
                                     itemprop="reviewRating"
                                     itemscope itemtype="https://schema.org/Rating">
                                    <meta itemprop="ratingValue" content="<?php echo esc_attr( $rv['rating'] ); ?>" />
                                    <meta itemprop="bestRating" content="5" />
                                    <span aria-label="<?php echo esc_attr( $rv['rating'] ); ?> out of 5 stars">
                                        <?php echo str_repeat( '&#9733;', max( 1, min( 5, $rv['rating'] ) ) ); ?>
                                    </span>
                                </div>
                                <blockquote class="acp-testimonial__text" itemprop="reviewBody">
                                    <?php echo esc_html( $rv['text'] ); ?>
                                </blockquote>
                                <figcaption class="acp-testimonial__author"
                                            itemprop="author"
                                            itemscope itemtype="https://schema.org/Person">
                                    <span itemprop="name"><?php echo esc_html( $rv['author'] ); ?></span>
                                    <?php if ( $rv['city'] ) : ?>
                                        <span class="acp-testimonial__city"> — <?php echo esc_html( $rv['city'] ); ?>, AZ</span>
                                    <?php endif; ?>
                                </figcaption>
                            </figure>
                        <?php endforeach; ?>
                    </div>
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
        // FAQs — now up to 6 Q/A pairs. Marked up with microdata so if the
        // JSON-LD is stripped the page still has inline FAQ schema.
        $faqs = array();
        for ( $i = 1; $i <= 6; $i++ ) {
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
