/*
Theme Name: Assembler
Theme URI: https://wordpress.com/theme/assembler
Author: Automattic
Author URI: https://automattic.com/
Description: Assemble something beautiful.
Requires at least: 6.4
Tested up to: 6.9
Requires PHP: 7.2
Version: 0.0.124
License: GNU General Public License v2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html
Text Domain: assembler
Tags: blog, one-column, three-columns, wide-blocks, block-patterns, custom-colors, custom-logo, custom-menu, editor-style, featured-images, full-site-editing, rtl-language-support, style-variations, template-editing, theme-options, threaded-comments, translation-ready
*/

body {
    -webkit-font-smoothing: antialiased;
}

/* Set default line height for font size presets. */

.has-xx-large-font-size,
.has-xxx-large-font-size {
	line-height: 1;
}

/* Add a transition state for buttons. */

.wp-element-button {
    transition: border, background-color, color, box-shadow, opacity, filter;
    transition-duration: 0.15s;
    transition-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);
    backdrop-filter: blur(30px);
}

/* Fields */

label,
.jetpack-field-label .rich-text.jetpack-field-label__input,
.contact-form .grunion-checkbox-multiple-options legend, 
.contact-form .grunion-radio-options legend,
.wp-block-jetpack-contact-form-container .wp-block-jetpack-contact-form label {
    display: inline-block;
    font-size: var(--wp--preset--font-size--small);
    margin-bottom: 0.25em;
    font-weight: inherit;
}

textarea:not(.block-editor-plain-text),
input:not([type=submit]):not([type=checkbox]):not([type=radio]):not([type=range]),
.wp-block-post-comments-form textarea,
.wp-block-post-comments-form input:not([type=submit]):not([type=checkbox]):not([type=radio]),
.jetpack-contact-form .jetpack-field .jetpack-field__input,
.jetpack-contact-form .jetpack-field .jetpack-field__textarea {
    background-color: var(--wp--custom--input-background);
    border-color: currentColor;
    border-style: solid;
    border-radius: 6px;
    border-width: 1px;
    box-shadow: none;
    box-sizing: border-box;
    color: currentColor;
    font-size: var(--wp--preset--font-size--small);
    font-weight: inherit;
    line-height: 1.5;
    min-height: 42px;
    padding: 0.8rem 1rem;
    width: 100%;
}

/* In dark-controls context, inputs are transparent so they blend into the section background */
.has-dark-controls textarea:not(.block-editor-plain-text),
.has-dark-controls input:not([type=submit]):not([type=checkbox]):not([type=radio]):not([type=range]) {
    background-color: transparent;
}

.has-dark-controls textarea:not(.block-editor-plain-text):focus,
.has-dark-controls input:not([type=submit]):not([type=checkbox]):not([type=radio]):not([type=range]):focus {
    background-color: rgba(0, 0, 0, 0.1);
}

textarea:focus,
input:not([type=submit]):focus,
.wp-block-post-comments-form textarea:focus,
.wp-block-post-comments-form input:not([type=submit]):not([type=checkbox]):not([type=radio]):focus {
    outline: 1px solid currentColor;
}

textarea::placeholder,
.input::placeholder,
.wp-block-jetpack-subscriptions__form .components-base-control__field input::placeholder {
    color: color-mix(in srgb, currentColor 60%, transparent);
}

/* Restore WC's native floating-label padding for all WC text inputs */
.wc-block-components-text-input input:not([type=submit]):not([type=checkbox]):not([type=radio]):not([type=range]) {
    padding: 1.5em .5em .5em;
}

/* WooCommerce select element overrides */
.wc-blocks-components-select.wc-blocks-components-select .wc-blocks-components-select__container {
  background-color: transparent;
  color: inherit
}

/* Double selector here for specificity to override Woo styles */
.wc-blocks-components-select.wc-blocks-components-select .wc-blocks-components-select__container select {
  background-color: var(--wp--custom--input-background);
  border-color: currentColor;
  border-style: solid;
  border-radius: 6px;
  border-width: 1px;
  color: currentColor;
}
.wc-blocks-components-select .wc-blocks-components-select__container select:focus {
  outline-style: solid;
  outline-width: 0.75px;
  outline-color: #000;
}

.has-dark-controls .wc-blocks-components-select.wc-blocks-components-select .wc-blocks-components-select__container {
  background-color: transparent;
}

.has-dark-controls .wc-blocks-components-select.wc-blocks-components-select .wc-blocks-components-select__container select {
  background-color: transparent;
}

.has-dark-controls .wc-blocks-components-select.wc-blocks-components-select .wc-blocks-components-select__container select:focus {
  background-color: rgba(0, 0, 0, 0.1);
}


/* Jetpack Forms: Clean up errors */

.contact-form__error {
    font-size: 13px;
}

.contact-form__input-error {
	font-size: 13px;
    gap: 8px;
}

.contact-form__input-error .contact-form__warning-icon {
    border-width: 0;
}

/* Jetpack Forms: Animated block style tweaks */

.contact-form .is-style-animated .grunion-field-wrap.grunion-field-select-wrap .animated-label__label label,
.contact-form .is-style-animated .grunion-field-wrap .grunion-field.has-placeholder ~ .animated-label__label label,
.contact-form .is-style-animated .grunion-field-wrap .grunion-field:focus ~ .animated-label__label label,
.contact-form .is-style-animated .grunion-field-wrap .grunion-field:not(:placeholder-shown) ~ .animated-label__label label {
	opacity: 0.7;
    font-size: 11px;
}

/* Styling for hero areas. */
.header-cover .wp-block-template-part {
    max-width: none;
}

.header-cover .wp-block-template-part > .wp-block-group {
    padding-left: 0;
    padding-right: 0;
}

/* Cover block styles */
.wp-block-cover[class*="is-style-section"]:not(.is-style-default) .wp-block-cover__image-background {
    opacity: 0.25;
}

.wp-block-cover[class*="is-style-section"]:not(.is-style-default) .wp-block-cover__background {
    opacity: 0;
}

:root :where(.wp-block-cover.is-light){
    color: var(--wp--preset--color--theme-5, #000);
}

.wp-block-cover[class*="is-style-section"]:not(.is-style-default) .wp-block-cover__background {
    opacity: 0;
}

/* Make sure footers have no margin. */
footer {
	margin-top: 0 !important;
}

/* Social Links: Better default color. */

.wp-block-social-links.is-style-logos-only li.wp-social-link {
	color: currentcolor;
}

.wp-block-social-links.is-style-logos-only .wp-social-link svg {
	height: 1em;
	width: 1em;
}

.wp-block-social-links.has-small-icon-size {
	font-size: 20px;
}

/* Navigation: Remove row gap to improve wrapping behavior */
.wp-block-navigation__container {
    row-gap: 0;
}

/* Move header core/navigation to the right on mobile. */

.order-0 {
	order: 0;
}

.order-1 {
	order: 1;
}

.grow-0 {
	flex-grow: 0;
}

.grow {
	flex-grow: 1;
}

@media (min-width: 600px) {

	.md\:order-0 {
		order: 0;
	}

	.md\:order-1 {
		order: 1;
	}

	.md\:grow-0 {
		flex-grow: 0;
	}

	.md\:grow {
		flex-grow: 1;
	}

}

.overflow-hidden {
	overflow: hidden;
}

/* Utility class for wide and full images with aspect ratios, as core does not support this yet. */
.aspect-16\/9 {
	aspect-ratio: 16/9;
}

.aspect-16\/9 img,
.aspect-16\/9 .components-placeholder {
    aspect-ratio: 16/9;
    object-fit: cover;
}

/* Ensure cropping works. */
.aspect-16\/9 .wp-block-image__crop-area,
.aspect-16\/9 .wp-block-image__crop-area img {
	aspect-ratio: unset;
}

/* WooCommerce Catalog Sorting Styles */
.wc-block-catalog-sorting {
    position: relative;
}

.wc-block-catalog-sorting > div,
.wc-block-catalog-sorting .woocommerce-ordering {
    align-items: center;
    display: flex;
    gap: 8px;
}

.wc-block-catalog-sorting > div >label,
.woocommerce .woocommerce-ordering > label {
    margin: 0;
    text-wrap: nowrap;
}

.wc-block-catalog-sorting select.orderby {
    appearance: none;
    background-color: transparent;
    border: 1px solid color-mix(in srgb, currentColor 50%, transparent);
    font-family: inherit;
    font-size: inherit;
    border-radius: 6px;
    color: currentColor;
    cursor: pointer;
    padding: 0.75rem 2.5rem 0.75rem 0.75rem;
    width: 100%;
}

/* Arrow using CSS triangle for dynamic color */
.wc-block-catalog-sorting::after {
    content: '';
    position: absolute;
    top: 50%;
    right: 0.75rem;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-left: 0.35em solid transparent;
    border-right: 0.35em solid transparent;
    border-top: 0.4em solid currentColor;
    pointer-events: none;
}

/* Make sure the CSS triangle stays the same when it's hovered or selected */
.is-outline-mode .block-editor-block-list__block.wc-block-catalog-sorting:not(.remove-outline):not(.rich-text):not([contenteditable=true]).is-selected:after,
.is-outline-mode .block-editor-block-list__block.wc-block-catalog-sorting:not(.remove-outline).is-hovered:not(.is-selected):after {
    left: auto;
    outline-color: transparent;
    right: 0.75rem;
    top: 50%;
}

/* Remove border and background color from the qty selector */
.wc-block-components-quantity-selector input.input-text.qty.text,
input:not([type=submit]):not([type=checkbox]):not([type=radio]):not([type=range]).wc-block-components-quantity-selector__input {
    background-color: transparent;
    border-style: none;
}

/* Reset padding for the qty selector */
input:not([type=submit]):not([type=checkbox]):not([type=radio]):not([type=range]).qty {
    padding: inherit;
}

/* Remove unwated right margin the qty selector */
.woocommerce div.product form.cart div.quantity .qty {
    margin-right: 0;
}

/* Fix the qty selector height so it matches with the button next to it */
.wp-block-add-to-cart-with-options .wc-block-components-quantity-selector {
    height: 100%;
}

/* Make sure the qty selector's height is the same as the button next to it in the editor */
.wc-block-add-to-cart-with-options__quantity-selector > div,
.wc-block-add-to-cart-with-options__quantity-selector .wc-block-components-quantity-selector {
    height: 100%;
}

/* Remove unnecessary bottom margin from the variation selector labels */
.woocommerce-page label.wp-block-woocommerce-add-to-cart-with-options-variation-selector-attribute-name,
.woocommerce-page label.wc-block-add-to-cart-with-options-variation-selector-attribute-options__pill {
    margin-bottom: 0;
}

/* Remove unwanted top margin from the title of the order confirmation page template */
.wc-block-order-confirmation-status h1 {
    margin-top: 0;
}

/* Add top margin to the express checkout */
.wcpay-express-checkout-wrapper {
    margin-top: var(--wp--style--block-gap);
}

/* Remove unwanted margin from the attribute value */
.wp-block-product-specifications-item__value p {
    margin: 0;
}

/* Remove underline from the attribute value */
.wp-block-product-specifications-item__value p a {
    text-decoration: none;
}

.wp-block-woocommerce-product-specifications th,
.wp-block-woocommerce-product-specifications td {
    border-color: color-mix(in srgb, currentColor 30%, transparent);
}

/* Reset unwanted margins */
.wc-block-components-product-summary,
.wc-block-components-product-summary p {
    margin: 0;
}

/* Make sure the paragraph has a line break */
.wc-block-components-product-summary p + p {
    margin-top: var(--wp--style--block-gap);
}

/* Remove underline from the product name inside cart */
.wc-block-cart-item__wrap .wc-block-components-product-name {
    text-decoration: none;
}

/* Utility class for reversing the order of rows */
@media (min-width: 782px) {
    .wp-block-columns.row-reverse {
        flex-direction: row-reverse;
    }
}

/* Reduce the size of the cart badge. */
.theme-assembler .wc-block-mini-cart__badge {
	font-size: .6em;
}

/* Fix Woo input field */
.theme-assembler .woocommerce div.product form.cart div.quantity .qty {
  min-width: 80px;
}

/* Remove unwanted top margin from small screens */
@container (max-width: 699px) {
    .wp-block-woocommerce-checkout-order-summary-block .wc-block-components-checkout-order-summary__title {
        margin-top: 0;
    }
}
:host{display:block;margin-left:auto;margin-right:auto;position:relative;z-index:1}.swiper{display:block;list-style:none;margin-left:auto;margin-right:auto;overflow:hidden;padding:0;position:relative;z-index:1}.swiper-vertical>.swiper-wrapper{flex-direction:column}.swiper-wrapper{box-sizing:initial;display:flex;height:100%;position:relative;transition-property:transform;transition-timing-function:ease;width:100%;z-index:1}.swiper-android .swiper-slide,.swiper-ios .swiper-slide,.swiper-wrapper{transform:translateZ(0)}.swiper-horizontal{touch-action:pan-y}.swiper-vertical{touch-action:pan-x}.swiper-slide{display:block;flex-shrink:0;height:100%;position:relative;transition-property:transform;width:100%}.swiper-slide-invisible-blank{visibility:hidden}.swiper-autoheight,.swiper-autoheight .swiper-slide{height:auto}.swiper-autoheight .swiper-wrapper{align-items:flex-start;transition-property:transform,height}.swiper-backface-hidden .swiper-slide{backface-visibility:hidden;transform:translateZ(0)}.swiper-3d.swiper-css-mode .swiper-wrapper{perspective:1200px}.swiper-3d .swiper-wrapper{transform-style:preserve-3d}.swiper-3d{perspective:1200px;.swiper-cube-shadow,.swiper-slide{transform-style:preserve-3d}}.swiper-css-mode{>.swiper-wrapper{overflow:auto;scrollbar-width:none;-ms-overflow-style:none;&::-webkit-scrollbar{display:none}}>.swiper-wrapper>.swiper-slide{scroll-snap-align:start start}&.swiper-horizontal{>.swiper-wrapper{scroll-snap-type:x mandatory}>.swiper-wrapper>.swiper-slide:first-child{margin-inline-start:var(--swiper-slides-offset-before);scroll-margin-inline-start:var(--swiper-slides-offset-before)}>.swiper-wrapper>.swiper-slide:last-child{margin-inline-end:var(--swiper-slides-offset-after)}}&.swiper-vertical{>.swiper-wrapper{scroll-snap-type:y mandatory}>.swiper-wrapper>.swiper-slide:first-child{margin-block-start:var(--swiper-slides-offset-before);scroll-margin-block-start:var(--swiper-slides-offset-before)}>.swiper-wrapper>.swiper-slide:last-child{margin-block-end:var(--swiper-slides-offset-after)}}&.swiper-free-mode{>.swiper-wrapper{scroll-snap-type:none}>.swiper-wrapper>.swiper-slide{scroll-snap-align:none}}&.swiper-centered{>.swiper-wrapper:before{content:"";flex-shrink:0;order:9999}>.swiper-wrapper>.swiper-slide{scroll-snap-align:center center;scroll-snap-stop:always}}&.swiper-centered.swiper-horizontal{>.swiper-wrapper>.swiper-slide:first-child{margin-inline-start:var(--swiper-centered-offset-before)}>.swiper-wrapper:before{height:100%;min-height:1px;width:var(--swiper-centered-offset-after)}}&.swiper-centered.swiper-vertical{>.swiper-wrapper>.swiper-slide:first-child{margin-block-start:var(--swiper-centered-offset-before)}>.swiper-wrapper:before{height:var(--swiper-centered-offset-after);min-width:1px;width:100%}}}.swiper-3d{.swiper-slide-shadow,.swiper-slide-shadow-bottom,.swiper-slide-shadow-left,.swiper-slide-shadow-right,.swiper-slide-shadow-top{height:100%;left:0;pointer-events:none;position:absolute;top:0;width:100%;z-index:10}.swiper-slide-shadow{background:#00000026}.swiper-slide-shadow-left{background-image:linear-gradient(270deg,#00000080,#0000)}.swiper-slide-shadow-right{background-image:linear-gradient(90deg,#00000080,#0000)}.swiper-slide-shadow-top{background-image:linear-gradient(0deg,#00000080,#0000)}.swiper-slide-shadow-bottom{background-image:linear-gradient(180deg,#00000080,#0000)}}.swiper-lazy-preloader{border:4px solid #007aff;border-radius:50%;border-top-color:#0000;box-sizing:border-box;height:42px;left:50%;margin-left:-21px;margin-top:-21px;position:absolute;top:50%;transform-origin:50%;width:42px;z-index:10}.swiper-watch-progress .swiper-slide-visible,.swiper:not(.swiper-watch-progress){.swiper-lazy-preloader{animation:swiper-preloader-spin 1s linear infinite}}.swiper-lazy-preloader-white{--swiper-preloader-color:#fff}.swiper-lazy-preloader-black{--swiper-preloader-color:#000}@keyframes swiper-preloader-spin{0%{transform:rotate(0deg)}to{transform:rotate(1turn)}}.swiper-virtual .swiper-slide{-webkit-backface-visibility:hidden;transform:translateZ(0)}.swiper-virtual.swiper-css-mode{.swiper-wrapper:after{content:"";left:0;pointer-events:none;position:absolute;top:0}}.swiper-virtual.swiper-css-mode.swiper-horizontal{.swiper-wrapper:after{height:1px;width:var(--swiper-virtual-size)}}.swiper-virtual.swiper-css-mode.swiper-vertical{.swiper-wrapper:after{height:var(--swiper-virtual-size);width:1px}}.swiper-button-next,.swiper-button-prev{align-items:center;color:#007aff;cursor:pointer;display:flex;height:44px;justify-content:center;position:absolute;width:44px;z-index:10;&.swiper-button-disabled{cursor:auto;opacity:.35;pointer-events:none}&.swiper-button-hidden{cursor:auto;opacity:0;pointer-events:none}.swiper-navigation-disabled &{display:none!important}svg{fill:currentColor;height:100%;-o-object-fit:contain;object-fit:contain;pointer-events:none;transform-origin:center;width:100%}}.swiper-button-lock{display:none}.swiper-button-next,.swiper-button-prev{margin-top:-22px;top:50%}.swiper-button-prev{left:4px;right:auto;.swiper-navigation-icon{transform:rotate(180deg)}}.swiper-button-next{left:auto;right:4px}.swiper-horizontal{.swiper-button-next,.swiper-button-prev,~.swiper-button-next,~.swiper-button-prev{margin-left:0;margin-top:-22px;top:50%}&.swiper-rtl .swiper-button-next,&.swiper-rtl~.swiper-button-next,&~.swiper-button-prev,.swiper-button-prev{left:4px;right:auto}&.swiper-rtl .swiper-button-prev,&.swiper-rtl~.swiper-button-prev,&~.swiper-button-next,.swiper-button-next{left:auto;right:4px}&.swiper-rtl .swiper-button-next,&.swiper-rtl~.swiper-button-next,&~.swiper-button-prev,.swiper-button-prev{.swiper-navigation-icon{transform:rotate(180deg)}}&.swiper-rtl .swiper-button-prev,&.swiper-rtl~.swiper-button-prev{.swiper-navigation-icon{transform:rotate(0deg)}}}.swiper-vertical{.swiper-button-next,.swiper-button-prev,~.swiper-button-next,~.swiper-button-prev{left:50%;margin-left:-22px;margin-top:0;right:auto}.swiper-button-prev,~.swiper-button-prev{bottom:auto;top:4px;.swiper-navigation-icon{transform:rotate(-90deg)}}.swiper-button-next,~.swiper-button-next{bottom:4px;top:auto;.swiper-navigation-icon{transform:rotate(90deg)}}}.swiper-pagination{position:absolute;text-align:center;transform:translateZ(0);transition:opacity .3s;z-index:10;&.swiper-pagination-hidden{opacity:0}&.swiper-pagination-disabled,.swiper-pagination-disabled>&{display:none!important}}.swiper-horizontal>.swiper-pagination-bullets,.swiper-pagination-bullets.swiper-pagination-horizontal,.swiper-pagination-custom,.swiper-pagination-fraction{bottom:8px;left:0;top:auto;width:100%}.swiper-pagination-bullets-dynamic{font-size:0;overflow:hidden;.swiper-pagination-bullet{position:relative;transform:scale(.33)}.swiper-pagination-bullet-active,.swiper-pagination-bullet-active-main{transform:scale(1)}.swiper-pagination-bullet-active-prev{transform:scale(.66)}.swiper-pagination-bullet-active-prev-prev{transform:scale(.33)}.swiper-pagination-bullet-active-next{transform:scale(.66)}.swiper-pagination-bullet-active-next-next{transform:scale(.33)}}.swiper-pagination-bullet{background:#000;border-radius:50%;display:inline-block;height:8px;opacity:.2;width:8px;button&{-webkit-appearance:none;-moz-appearance:none;appearance:none;border:none;box-shadow:none;margin:0;padding:0}.swiper-pagination-clickable &{cursor:pointer}&:only-child{display:none!important}}.swiper-pagination-bullet-active{background:#007aff;opacity:1}.swiper-pagination-vertical.swiper-pagination-bullets,.swiper-vertical>.swiper-pagination-bullets{left:auto;right:8px;top:50%;transform:translate3d(0,-50%,0);.swiper-pagination-bullet{display:block;margin:6px 0}&.swiper-pagination-bullets-dynamic{top:50%;transform:translateY(-50%);width:8px;.swiper-pagination-bullet{display:inline-block;transition:transform .2s,top .2s}}}.swiper-horizontal>.swiper-pagination-bullets,.swiper-pagination-horizontal.swiper-pagination-bullets{.swiper-pagination-bullet{margin:0 4px}&.swiper-pagination-bullets-dynamic{left:50%;transform:translateX(-50%);white-space:nowrap;.swiper-pagination-bullet{transition:transform .2s,left .2s}}}.swiper-horizontal.swiper-rtl>.swiper-pagination-bullets-dynamic .swiper-pagination-bullet{transition:transform .2s,right .2s}.swiper-pagination-fraction{color:inherit}.swiper-pagination-progressbar{background:#00000040;position:absolute;.swiper-pagination-progressbar-fill{background:#007aff;height:100%;left:0;position:absolute;top:0;transform:scale(0);transform-origin:left top;width:100%}.swiper-rtl & .swiper-pagination-progressbar-fill{transform-origin:right top}&.swiper-pagination-horizontal,&.swiper-pagination-vertical.swiper-pagination-progressbar-opposite,.swiper-horizontal>&,.swiper-vertical>&.swiper-pagination-progressbar-opposite{height:4px;left:0;top:0;width:100%}&.swiper-pagination-horizontal.swiper-pagination-progressbar-opposite,&.swiper-pagination-vertical,.swiper-horizontal>&.swiper-pagination-progressbar-opposite,.swiper-vertical>&{height:100%;left:0;top:0;width:4px}}.swiper-pagination-lock{display:none}.swiper-scrollbar{background:#0000001a;border-radius:10px;position:relative;touch-action:none;&.swiper-scrollbar-disabled,.swiper-scrollbar-disabled>&{display:none!important}&.swiper-scrollbar-horizontal,.swiper-horizontal>&{bottom:4px;height:4px;left:1%;position:absolute;top:auto;width:98%;z-index:50}&.swiper-scrollbar-vertical,.swiper-vertical>&{height:98%;left:auto;position:absolute;right:4px;top:1%;width:4px;z-index:50}}.swiper-scrollbar-drag{background:#00000080;border-radius:10px;height:100%;left:0;position:relative;top:0;width:100%}.swiper-scrollbar-cursor-drag{cursor:move}.swiper-scrollbar-lock{display:none}.swiper-zoom-container{align-items:center;display:flex;height:100%;justify-content:center;text-align:center;width:100%;>canvas,>img,>svg{max-height:100%;max-width:100%;-o-object-fit:contain;object-fit:contain}}.swiper-slide-zoomed{cursor:move;touch-action:none}.swiper .swiper-notification{left:0;opacity:0;pointer-events:none;position:absolute;top:0;z-index:-1000}.swiper-free-mode>.swiper-wrapper{margin:0 auto;transition-timing-function:ease-out}.swiper-grid>.swiper-wrapper{flex-wrap:wrap}.swiper-grid-column>.swiper-wrapper{flex-direction:column;flex-wrap:wrap}.swiper-fade{&.swiper-free-mode{.swiper-slide{transition-timing-function:ease-out}}.swiper-slide{pointer-events:none;transition-property:opacity;.swiper-slide{pointer-events:none}}.swiper-slide-active{pointer-events:auto;& .swiper-slide-active{pointer-events:auto}}}.swiper.swiper-cube{overflow:visible}.swiper-cube{.swiper-slide{backface-visibility:hidden;height:100%;pointer-events:none;transform-origin:0 0;visibility:hidden;width:100%;z-index:1;.swiper-slide{pointer-events:none}}&.swiper-rtl .swiper-slide{transform-origin:100% 0}.swiper-slide-active{&,& .swiper-slide-active{pointer-events:auto}}.swiper-slide-active,.swiper-slide-next,.swiper-slide-prev{pointer-events:auto;visibility:visible}.swiper-cube-shadow{bottom:0;height:100%;left:0;opacity:.6;position:absolute;width:100%;z-index:0;&:before{background:#000;bottom:0;content:"";filter:blur(50px);left:0;position:absolute;right:0;top:0}}}.swiper-cube{.swiper-slide-next+.swiper-slide{pointer-events:auto;visibility:visible}}.swiper-cube{.swiper-slide-shadow-cube.swiper-slide-shadow-bottom,.swiper-slide-shadow-cube.swiper-slide-shadow-left,.swiper-slide-shadow-cube.swiper-slide-shadow-right,.swiper-slide-shadow-cube.swiper-slide-shadow-top{backface-visibility:hidden;z-index:0}}.swiper.swiper-flip{overflow:visible}.swiper-flip{.swiper-slide{backface-visibility:hidden;pointer-events:none;z-index:1;.swiper-slide{pointer-events:none}}.swiper-slide-active{&,& .swiper-slide-active{pointer-events:auto}}}.swiper-flip{.swiper-slide-shadow-flip.swiper-slide-shadow-bottom,.swiper-slide-shadow-flip.swiper-slide-shadow-left,.swiper-slide-shadow-flip.swiper-slide-shadow-right,.swiper-slide-shadow-flip.swiper-slide-shadow-top{backface-visibility:hidden;z-index:0}}.swiper-creative{.swiper-slide{backface-visibility:hidden;overflow:hidden;transition-property:transform,opacity,height}}.swiper.swiper-cards{overflow:visible}.swiper-cards{.swiper-slide{backface-visibility:hidden;overflow:hidden;transform-origin:center bottom}}:root {
	--jp-carousel-primary-color: #fff;
	--jp-carousel-primary-subtle-color: #999;
	--jp-carousel-bg-color: #000;
	--jp-carousel-bg-faded-color: #222;
	--jp-carousel-border-color: #3a3a3a;
	--jp-carousel-fade-duration: 100ms;
}

/*
Every opacity fade in the module runs through this class, so it stays on the
compositor and JS only has to flip the target value.
*/
.jp-carousel-fade {
	transition: opacity var(--jp-carousel-fade-duration) ease-out;
}

@media ( prefers-reduced-motion: reduce ) {

	.jp-carousel-fade {
		transition-duration: 0s;
	}
}

:root .jp-carousel-light {
	--jp-carousel-primary-color: #000;
	--jp-carousel-primary-subtle-color: #646970;
	--jp-carousel-bg-color: #fff;
	--jp-carousel-bg-faded-color: #fbfbfb;
	--jp-carousel-border-color: #dcdcde;
}

.jp-carousel-overlay .swiper-button-prev,
.jp-carousel-overlay .swiper-rtl .swiper-button-next,
.jp-carousel-overlay .swiper-button-next,
.jp-carousel-overlay .swiper-rtl .swiper-button-prev {
	background-image: none;
}

/* end of temporary fix */

[data-carousel-extra]:not(.jp-carousel-wrap) img,
[data-carousel-extra]:not(.jp-carousel-wrap) img + figcaption {
	cursor: pointer;
}

.jp-carousel-wrap * {
	line-height: inherit;
}

.jp-carousel-wrap.swiper {
	height: auto;
	width: 100vw;
}

.jp-carousel-overlay .swiper-zoom-container {
	background-size: 200%;
	background-repeat: no-repeat;
	background-position: center;
}

/*
To prevent flash of prev/next image scale transition after pinch zoom we need
to hide them. Swiper does not add a class of `swiper-slide-zoomed` to slides
on pinch and zoom so we have to target all affected elements in touch devices.
*/
.jp-carousel-overlay .swiper-slide.swiper-slide-prev .swiper-zoom-container img,
.jp-carousel-overlay .swiper-slide.swiper-slide-next .swiper-zoom-container img {
	transition: none !important;
}

.jp-carousel-overlay .swiper-button-prev,
.jp-carousel-overlay .swiper-button-next {
	opacity: 0.5;
	transition: 0.5s opacity ease-out;
	height: initial;
	width: initial;
	padding: 20px 40px;
	background-image: none;
}

.jp-carousel-overlay .swiper-button-prev:hover,
.jp-carousel-overlay .swiper-button-next:hover {
	opacity: 1;
}

.jp-carousel-overlay .swiper-button-next::after,
.jp-carousel-overlay .swiper-rtl .swiper-button-next::after,
.jp-carousel-overlay .swiper-button-prev::after,
.jp-carousel-overlay .swiper-rtl .swiper-button-prev::after {
	content: none;
}

.jp-carousel-overlay .swiper-button-prev svg,
.jp-carousel-overlay .swiper-button-next svg {
	height: 30px;
	width: 28px;
	background: var(--jp-carousel-bg-color);
	border-radius: 4px;
}

.jp-carousel-overlay .swiper-button-prev svg:hover,
.jp-carousel-overlay .swiper-button-next svg:hover {
	background: var(--jp-carousel-primary-subtle-color);
}

.jp-carousel-overlay {
	font-family: "Helvetica Neue", sans-serif !important;
	z-index: 2147483647;
	overflow-x: hidden;
	overflow-y: auto;
	direction: ltr;
	position: fixed;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	background: var(--jp-carousel-bg-color);
}

.jp-carousel-overlay * {
	box-sizing: border-box;
}

/* Fix for Twenty Nineteen theme compatibility */
.jp-carousel-overlay h1::before,
.jp-carousel-overlay h2::before,
.jp-carousel-overlay h3::before {
	content: none;
	display: none;
}

.jp-carousel-overlay .swiper .swiper-button-prev {
	left: 0;
	right: auto;
}

.jp-carousel-overlay .swiper .swiper-button-next {
	right: 0;
	left: auto;
}

.jp-carousel-overlay .swiper.swiper-rtl .swiper-button-prev,
.jp-carousel-overlay .swiper.swiper-rtl .swiper-button-next {
	transform: scaleX(-1);
}

.jp-carousel-container {
	display: grid;
	grid-template-rows: 1fr 64px; /* 1. main carousel, 2. info area as footer */
	height: 100%;
}

.jp-carousel-hide-controls .jp-carousel-container {
	grid-template-rows: 1fr;
}

.jp-carousel-hide-controls .swiper-wrapper {
	margin-top: -32px; /* Compensate for the remove of the height of the info bar. */
}


.jp-carousel-hide-controls .jp-swiper-button-next,
.jp-carousel-hide-controls .jp-swiper-button-prev {
	margin-top: -54px; /* The height of the info bar plus any top padding on the nav button itself. */
}

.jp-carousel-msg {
	font-family: "Open Sans", sans-serif;
	font-style: normal;
	display: inline-block;
	line-height: 19px;
	padding: 11px 15px;
	font-size: 14px;
	text-align: center;
	margin: 25px 20px 0 2px;
	background-color: var(--jp-carousel-primary-color);
	border-left: 4px solid #ffba00;
	box-shadow: 0 1px 1px 0 rgba(0, 0, 0, 0.1);
}

.jp-carousel-info {
	display: flex;
	flex-direction: column;
	text-align: left !important;
	-webkit-font-smoothing: subpixel-antialiased !important;
	z-index: 100;
	background-color: var(--jp-carousel-bg-color);
	transition: opacity 200ms ease-out;
	opacity: 1;
}

.jp-carousel-hide-controls .jp-carousel-info {
	visibility: hidden;
	height: 0;
	overflow: hidden;
}

.jp-carousel-info-footer {
	position: relative;
	background-color: var(--jp-carousel-bg-color);
	height: 64px;
	display: flex;
	align-items: center;
	justify-content: space-between;
	width: 100vw;
}

.jp-carousel-info-extra {
	display: none;
	background-color: var(--jp-carousel-bg-color);
	padding: 35px;
	width: 100vw;
	border-top: 1px solid var(--jp-carousel-bg-faded-color);
}

.jp-carousel-title-and-caption {
	margin-bottom: 15px;
}

.jp-carousel-info-extra.jp-carousel-show {
	display: block;
}

.jp-carousel-info ::selection {
	background: var(--jp-carousel-primary-color); /* Safari */
	color: var(--jp-carousel-primary-color);
}

.jp-carousel-info ::-moz-selection {
	background: var(--jp-carousel-primary-color); /* Firefox */
	color: var(--jp-carousel-primary-color);
}

.jp-carousel-photo-info {
	left: 0 !important;
	width: 100% !important;
}

.jp-carousel-comments-wrapper {
	padding: 0;
	width: 100% !important;
	display: none;
}

.jp-carousel-comments-wrapper.jp-carousel-show {
	display: block;
}

.jp-carousel-comments-wrapper > .jp-carousel-photo-info {
	display: none;
}

.jp-carousel-transitions .jp-carousel-photo-info {
	transition: 400ms ease-out;
}

.jp-carousel-buttons {
	margin: -18px -20px 15px;
	padding: 8px 10px;
	border-bottom: 1px solid #222;
	background: #222;
	text-align: center;
}

div.jp-carousel-buttons a {
	border: none !important;
	color: var(--jp-carousel-primary-subtle-color);
	font: 400 11px/1.2em "Helvetica Neue", sans-serif !important;
	letter-spacing: 0 !important;
	padding: 5px 2px 5px 0;
	text-decoration: none !important;
	text-shadow: none !important;
	vertical-align: middle;
	-webkit-font-smoothing: subpixel-antialiased;
}

div.jp-carousel-buttons a:hover {
	color: var(--jp-carousel-primary-color);
	border: none !important;
}

.jp-carousel-transitions div.jp-carousel-buttons a:hover {
	transition: none !important;
}

.jp-carousel-slide,
.jp-carousel-slide img {
	transform: translate3d(0, 0, 0);
}

.jp-carousel-close-hint {
	letter-spacing: 0 !important;
	position: fixed;
	top: 20px;
	right: 30px;
	padding: 10px;
	text-align: right;
	width: 45px;
	height: 45px;
	z-index: 15;
	color: var(--jp-carousel-primary-color);
	cursor: pointer;
	transition: opacity 200ms ease-out;
}

.jp-carousel-transitions .jp-carousel-close-hint {
	transition: color 200ms linear;
}

.jp-carousel-close-hint svg {
	padding: 3px 2px;
	background: var(--jp-carousel-bg-color);
	border-radius: 4px;
}

.jp-carousel-close-hint svg:hover {
	background: var(--jp-carousel-primary-subtle-color);
}

.jp-carousel-close-hint:hover {
	color: var(--jp-carousel-primary-color);
}

.jp-carousel-close-hint:hover span {
	border-color: var(--jp-carousel-primary-color);
}

/** Pagination Start **/
.jp-carousel-pagination-container {
	flex: 1;
	margin: 0 15px 0 35px;
}

.jp-swiper-pagination,
.jp-carousel-pagination {
	color: var(--jp-carousel-primary-color);
	font-size: 15px; /* same as .jp-carousel-info-footer .jp-carousel-photo-title  */
	font-weight: 400;
	white-space: nowrap;
	display: none;
	position: static !important;
}

.jp-carousel-pagination-container .swiper-pagination {
	text-align: left;
	line-height: 8px;
}

.jp-carousel-pagination {
	padding-left: 5px;
}

.jp-swiper-pagination .swiper-pagination-bullet {
	background: var(--jp-carousel-primary-subtle-color);
	margin: 0 4px;
}

.jp-swiper-pagination .swiper-pagination-bullet.swiper-pagination-bullet-active {
	background: var(--jp-carousel-primary-color);
}

.jp-swiper-pagination .swiper-pagination-bullet:not(.swiper-pagination-bullet-active) {
	background: var(--jp-carousel-primary-color);
	opacity: 0.5;
}

/** Pagination End **/

/** Title and Desc Start **/
.jp-carousel-info-footer .jp-carousel-photo-title-container {
	flex: 4;
	justify-content: center;
	overflow: hidden;
	margin: 0;
}

.jp-carousel-photo-title,
.jp-carousel-photo-caption {
	background: none !important;
	border: none !important;
	display: inline-block;
	font: 400 20px/1.3em "Helvetica Neue", sans-serif;
	line-height: normal;
	letter-spacing: 0 !important;
	margin: 0 0 10px 0;
	padding: 0;
	overflow: hidden;
	text-shadow: none !important;
	text-transform: none !important;
	color: var(--jp-carousel-primary-color);
}

.jp-carousel-info-footer .jp-carousel-photo-caption {
	text-align: center;
	font-size: 15px; /* same as .jp-carousel-pagination */
	white-space: nowrap;
	color: var(--jp-carousel-primary-subtle-color);
	cursor: pointer;
	margin: 0;
	text-overflow: ellipsis;
}

.jp-carousel-info-footer .jp-carousel-photo-caption p {
	margin: 0;
}

.jp-carousel-photo-title {
	font-size: 32px;
	margin-bottom: 2px;
}

.jp-carousel-photo-description {
	color: var(--jp-carousel-primary-subtle-color);
	font-size: 16px;
	margin: 25px 0;
	width: 100%;
	overflow: hidden;
	overflow-wrap: break-word;
}

.jp-carousel-photo-description p {
	color: var(--jp-carousel-primary-subtle-color);
	line-height: 1.4;
	margin-bottom: 0;
}

.jp-carousel-photo-description p a,
.jp-carousel-comments p a,
.jp-carousel-info .jp-carousel-photo-caption a,
.jp-carousel-info .jp-carousel-caption a {
	color: var(--jp-carousel-primary-color) !important;
	border: none !important;
	text-decoration: underline !important;
	font-weight: 400 !important;
	font-style: normal !important;
}

.jp-carousel-photo-description p strong,
.jp-carousel-photo-description p b {
	font-weight: 700;
	color: var(--jp-carousel-primary-subtle-color);
}

.jp-carousel-photo-description p em,
.jp-carousel-photo-description p i {
	font-style: italic;
	color: var(--jp-carousel-primary-subtle-color);
}

.jp-carousel-photo-description p a:hover,
.jp-carousel-comments p a:hover,
.jp-carousel-info .jp-carousel-photo-caption a:hover,
.jp-carousel-info .jp-carousel-caption a:hover {
	color: var(--jp-carousel-primary-subtle-color) !important;
}

.jp-carousel-photo-description p:empty {
	display: none;
}

.jp-carousel-photo-info h1::before,
.jp-carousel-photo-info h1::after,
.jp-carousel-comments-wrapper h1::before,
.jp-carousel-comments-wrapper h1::after {
	content: none !important;
}

.jp-carousel-caption {
	font-size: 14px;
	font-weight: 400;
	margin: 0;
}

/** Title and Desc End **/

/** Meta Box Start **/
.jp-carousel-image-meta {
	color: var(--jp-carousel-primary-color);
	font: 12px/1.4 "Helvetica Neue", sans-serif !important;
	width: 100%;
	display: none;
}

.jp-carousel-image-meta.jp-carousel-show {
	display: block;
}

.jp-carousel-image-meta li,
.jp-carousel-image-meta h5 {
	font-family: "Helvetica Neue", sans-serif !important;
	position: inherit !important;
	top: auto !important;
	right: auto !important;
	left: auto !important;
	bottom: auto !important;
	background: none !important;
	border: none !important;
	font-weight: 400 !important;
	/* stylelint-disable-next-line declaration-property-unit-allowed-list -- this should be changed to a unitless value: https://developer.wordpress.org/coding-standards/wordpress-coding-standards/css/#values */
	line-height: 1.3em !important;
}

.jp-carousel-image-meta ul {
	margin: 0 !important;
	padding: 0 !important;
	list-style: none !important;
}

.jp-carousel-image-meta li {
	width: 48% !important;
	display: inline-block !important;
	vertical-align: top !important;
	margin: 0 2% 15px 0 !important;
	color: var(--jp-carousel-primary-color) !important;
	font-size: 13px !important;
}

.jp-carousel-image-meta h5 {
	color: var(--jp-carousel-primary-subtle-color) !important;
	text-transform: uppercase !important;
	font-size: 10px !important;
	margin: 0 0 2px !important;
	letter-spacing: 0.1em !important;
}

a.jp-carousel-image-download {
	display: inline-block;
	clear: both;
	color: var(--jp-carousel-primary-subtle-color);
	line-height: 1;
	font-weight: 400;
	font-size: 14px;
	text-decoration: none;
}

a.jp-carousel-image-download svg {
	display: inline-block;
	vertical-align: middle;
	margin: 0 3px;
	padding-bottom: 2px;
}

a.jp-carousel-image-download span.photo-size {
	font-size: 11px;
	border-radius: 1em;
	margin-left: 2px;
	display: inline-block;
}

a.jp-carousel-image-download span.photo-size-times {
	padding: 0 1px 0 2px;
}

/** Meta Box End **/

/** Comments Start **/
.jp-carousel-comments {
	font: 15px/1.7 "Helvetica Neue", sans-serif !important;
	font-weight: 400;
	background: none transparent;
	width: 100%;
	bottom: 10px;
	margin-top: 20px;
}

.jp-carousel-comments p a:hover,
.jp-carousel-comments p a:focus,
.jp-carousel-comments p a:active {
	color: var(--jp-carousel-primary-color) !important;
}

.jp-carousel-comment {
	background: none transparent;
	color: var(--jp-carousel-primary-subtle-color);
	overflow: auto;
	width: 100%;
	display: flex;
}

.jp-carousel-comment + .jp-carousel-comment {
	margin-top: 20px;
}

.jp-carousel-comment:last-of-type {
	margin-bottom: 20px;
}

.jp-carousel-comment p {
	color: var(--jp-carousel-primary-subtle-color) !important;
}

.jp-carousel-comment .comment-author {
	font-size: 15px;
	font-weight: 500;
	padding: 0;
	width: auto;
	display: inline;
	float: none;
	border: none;
	margin: 0;
}

.jp-carousel-comment .comment-author a {
	color: var(--jp-carousel-primary-color);
}

.jp-carousel-comment .comment-gravatar {
	float: none;
	margin-right: 10px;
}

.jp-carousel-comment .comment-content {
	border: none;
	padding: 0;
}

.jp-carousel-comment .avatar {
	margin: 0;
	border-radius: 4px;
	border: none !important;
	padding: 0 !important;
	background-color: transparent !important;
	min-width: 64px;
	min-height: 64px;
	width: 64px;
	height: 64px;
}

.jp-carousel-comment .comment-date {
	color: var(--jp-carousel-primary-subtle-color);
	font-size: 11px;
	border-bottom: 1px solid var(--jp-carousel-bg-faded-color);
	margin-bottom: 6px;
}

#jp-carousel-comment-form {
	margin: 0 0 10px !important;
	width: 100%;
}

#jp-carousel-comment-form.jp-carousel-is-disabled {
	opacity: 0.5;
	pointer-events: none;
}

textarea#jp-carousel-comment-form-comment-field {
	background: var(--jp-carousel-bg-faded-color);
	border: 1px solid var(--jp-carousel-border-color);
	color: var(--jp-carousel-primary-subtle-color);
	font: 16px/1.4 "Helvetica Neue", sans-serif !important;
	width: 100%;
	padding: 10px 10px 5px;
	margin: 0;
	float: none;
	height: 147px;
	box-shadow: inset 2px 2px 2px rgba(0, 0, 0, 0.1);
	border-radius: 3px;
	overflow: hidden;
	box-sizing: border-box;
}

textarea#jp-carousel-comment-form-comment-field::-webkit-input-placeholder {
	color: #555;
}

textarea#jp-carousel-comment-form-comment-field:focus {
	background: var(--jp-carousel-bg-faded-color);
	color: var(--jp-carousel-primary-subtle-color);
}

textarea#jp-carousel-comment-form-comment-field:focus::-webkit-input-placeholder {
	color: var(--jp-carousel-primary-subtle-color);
}

#jp-carousel-loading-overlay {
	display: none;
	position: fixed;
	top: 0;
	bottom: 0;
	left: 0;
	right: 0;
}

#jp-carousel-loading-wrapper {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 100vh;
	width: 100vw;
}

#jp-carousel-library-loading {
	color: var(--jp-carousel-primary-color);
}

#jp-carousel-comment-form-spinner {
	display: none;
	position: absolute;
	margin: 0 auto;
	top: calc(50% - 10px);
	left: 0;
	bottom: 0;
	right: 0;
	color: var(--jp-carousel-primary-color);
	text-align: center;
}

.jp-carousel-info-content-wrapper {
	max-width: 800px;
	margin: auto;
}

#jp-carousel-comment-form-submit-and-info-wrapper {
	display: none;
	overflow: hidden;
	width: 100%;
}

#jp-carousel-comment-form-commenting-as input {
	background: var(--jp-carousel-bg-color);
	border: 1px solid var(--jp-carousel-border-color);
	color: var(--jp-carousel-primary-subtle-color);
	font: 16px/1.4 "Helvetica Neue", sans-serif !important;
	padding: 10px;
	float: left;
	box-shadow: inset 2px 2px 2px rgba(0, 0, 0, 0.2);
	border-radius: 2px;
	width: 285px;
}

#jp-carousel-comment-form-commenting-as input:focus {
	background: var(--jp-carousel-bg-faded-color);
	color: var(--jp-carousel-primary-subtle-color);
}

#jp-carousel-comment-form-commenting-as p {
	font: 400 13px/1.7 "Helvetica Neue", sans-serif !important;
	margin: 22px 0 0;
	float: left;
}

#jp-carousel-comment-form-commenting-as fieldset {
	float: left;
	border: none;
	margin: 20px 0 0 0;
	padding: 0;
	clear: both;
}

#jp-carousel-comment-form-commenting-as label {
	font: 400 13px/1.7 "Helvetica Neue", sans-serif !important;
	margin: 0 20px 3px 0;
	float: left;
	width: 100px;
}

#jp-carousel-comment-form-button-submit {
	margin-top: 20px;
	margin-left: auto;
	display: block;
	border: solid 1px var(--jp-carousel-primary-color);
	background: var(--jp-carousel-bg-color);
	border-radius: 3px;
	padding: 8px 16px;
	font-size: 14px;
	color: var(--jp-carousel-primary-color);
}

#jp-carousel-comment-form-button-submit:active,
#jp-carousel-comment-form-button-submit:focus {
	background: var(--jp-carousel-primary-color);
	color: var(--jp-carousel-bg-color);
}

#jp-carousel-comment-form-container {
	margin-bottom: 15px;
	width: 100%;
	margin-top: 20px;
	color: var(--jp-carousel-primary-subtle-color);
	position: relative;
	overflow: hidden;
}

#jp-carousel-comment-post-results {
	display: none;
	overflow: auto;
	width: 100%;
}

#jp-carousel-comment-post-results span {
	display: block;
	text-align: center;
	margin-top: 20px;
	width: 100%;
	overflow: auto;
	padding: 1em 0;
	box-sizing: border-box;
	border-radius: 2px;
	font: 13px/1.4 "Helvetica Neue", sans-serif !important;
	border: 1px solid var(--jp-carousel-border-color);
	box-shadow: inset 0 0 5px 0 rgba(0, 0, 0, 0.2);
}

.jp-carousel-comment-post-error {
	color: #df4926;
}

#jp-carousel-comments-closed {
	display: none;
	color: var(--jp-carousel-primary-subtle-color);
}

#jp-carousel-comments-loading {
	font: 400 15px/1.7 "Helvetica Neue", sans-serif !important;
	display: none;
	color: var(--jp-carousel-primary-subtle-color);
	text-align: left;
	margin-bottom: 20px;
	width: 100%;
	bottom: 10px;
	margin-top: 20px;
}

/** Icons Start **/
.jp-carousel-photo-icons-container {
	flex: 1;
	display: block;
	text-align: right;
	margin: 0 20px 0 30px;
	white-space: nowrap;
}

.jp-carousel-icon-btn {
	padding: 16px;
	text-decoration: none;
	border: none;
	background: none;
	display: inline-block;
	height: 64px;
}

.jp-carousel-icon {
	border: none;
	display: inline-block;
	line-height: 0;
	font-weight: 400;
	font-style: normal;
	border-radius: 4px;
	width: 31px; /* Prevent comments indicator from changing icon width */
	padding: 4px 3px 3px;
}

.jp-carousel-icon:hover {
	background: var(--jp-carousel-primary-subtle-color);
}

.jp-carousel-icon svg {
	display: inline-block;
}

.jp-carousel-overlay rect {
	fill: var(--jp-carousel-primary-color);
}

.jp-carousel-selected .jp-carousel-icon {
	background: var(--jp-carousel-primary-color);
}

.jp-carousel-selected rect {
	fill: var(--jp-carousel-bg-color);
}

.jp-carousel-icon-comments.jp-carousel-show {
	display: inline-block;
}

.jp-carousel-icon .jp-carousel-has-comments-indicator {
	display: none;
	font-size: 12px;
	vertical-align: top;
	margin-left: -16px;
	line-height: 1;
	padding: 2px 4px;
	border-radius: 4px;
	background: var(--jp-carousel-primary-color);
	color: var(--jp-carousel-bg-color);
	font-weight: 400;
	font-family: "Helvetica Neue", sans-serif !important;
	position: relative;
}

.jp-carousel-selected .jp-carousel-icon .jp-carousel-has-comments-indicator {
	background: var(--jp-carousel-bg-color);
	color: var(--jp-carousel-primary-color);
}

.jp-carousel-has-comments-indicator.jp-carousel-show {
	display: inline-block;
}

/** Icons End **/

/* Small screens */
@media only screen and ( max-width: 760px ) {

	.jp-carousel-overlay .swiper .swiper-button-next,
	.jp-carousel-overlay .swiper .swiper-button-prev {
		display: none !important;
	}

	.jp-carousel-buttons {
		display: none !important;
	}

	.jp-carousel-image-meta {
		float: none !important;
		width: 100% !important;
		box-sizing: border-box;
		margin-left: 0;
	}

	.jp-carousel-close-hint {
		font-size: 26px !important;
		position: fixed !important;
		top: 10px;
		right: 10px;
	}

	/* The admin bar is fixed at top: 0*/
	.admin-bar .jp-carousel-close-hint {
		top: 40px;
	}

	.jp-carousel-slide img {
		opacity: 1;
	}

	.jp-carousel-wrap {
		background-color: var(--jp-carousel-bg-color);
	}

	.jp-carousel-fadeaway {
		display: none;
	}

	.jp-carousel-info > .jp-carousel-photo-info {
		display: none;
	}

	.jp-carousel-comments-wrapper > .jp-carousel-photo-info {
		display: block;
	}

	.jp-carousel-caption {
		overflow: visible !important;
	}

	.jp-carousel-info-footer .jp-carousel-photo-title-container {
		display: none;
	}

	.jp-carousel-photo-icons-container {
		margin: 0 10px 0 0;
		white-space: nowrap;
	}

	.jp-carousel-icon-btn {
		padding-left: 20px;
	}

	.jp-carousel-pagination {
		padding-left: 5px;
	}

	.jp-carousel-pagination-container {
		margin-left: 25px;
	}

	.jp-carousel-comment .avatar {
		min-width: 48px;
	}

	#jp-carousel-comment-form-commenting-as fieldset,
	#jp-carousel-comment-form-commenting-as input {
		width: 100%;
		float: none;
	}
}
/* =Tiled Gallery Default Styles
-------------------------------------------------------------- */

.tiled-gallery {
	clear: both;
	margin: 0 0 20px;
	overflow: hidden;
}

.tiled-gallery img {
	margin: 2px !important; /* Ensure that this value isn't overridden by themes that give content images blanket margins */
}

.tiled-gallery .gallery-group {
	float: left;
	position: relative;
}

.tiled-gallery .tiled-gallery-item {
	float: left;
	margin: 0;
	position: relative;
	width: inherit; /* prevents ie8 bug with inline width styles */
}

.tiled-gallery .gallery-row {
	overflow: hidden;
}

.tiled-gallery .tiled-gallery-item a { /* Needs to reset some properties for theme compatibility */
	background: transparent;
	border: none;
	color: inherit;
	margin: 0;
	padding: 0;
	text-decoration: none;
	width: auto;
}

.tiled-gallery .tiled-gallery-item img,
.tiled-gallery .tiled-gallery-item img:hover { /* Needs to reset some properties for theme compatibility */
	background: none;
	border: none;
	box-shadow: none;
	max-width: 100%;
	padding: 0;
	vertical-align: middle;
}

.tiled-gallery-caption { /* Captions */
	background: #f0f0f1;
	background: rgba(255, 255, 255, 0.8);
	color: #333;
	font-size: 13px;
	font-weight: 400;
	overflow: hidden;
	padding: 10px 0;
	position: absolute;
	bottom: 0;
	text-indent: 10px;
	text-overflow: ellipsis;
	width: 100%;
	white-space: nowrap;
}

.tiled-gallery .tiled-gallery-item-small .tiled-gallery-caption { /* Smaller captions */
	font-size: 11px;
}

/* Hide galleries in widgets until they've been resized to fit.
   Gallery widgets are almost guaranteed to need resizing, and
   the jump is a little more obvious than galleries in content. */
.widget-gallery .tiled-gallery-unresized {
	visibility: hidden;
	height: 0;
	overflow: hidden;
}

/* =Greyscale
-------------------------------------------------------------- */

.tiled-gallery .tiled-gallery-item img.grayscale {
	-webkit-filter: grayscale(1);
	-ms-filter: grayscale(1);
	-o-filter: grayscale(1);
	filter: grayscale(1);
}

.tiled-gallery .tiled-gallery-item:hover img.grayscale {
	-webkit-filter: none;
	-ms-filter: none;
	-o-filter: none;
	filter: none;
}


/* =Circles Layout
-------------------------------------------------------------- */

.tiled-gallery.type-circle .tiled-gallery-item img {
	border-radius: 50% !important; /* Ensure that circles are displayed in themes that add border-radius to all images as a default */
	object-fit: cover;
}

.tiled-gallery.type-circle .tiled-gallery-caption {
	display: none;
}


/* =Square Layout
-------------------------------------------------------------- */
.tiled-gallery.type-square .tiled-gallery-item img {
	object-fit: cover;
}
