# -*- coding: utf-8 -*-
"""Stamp the $99 Expert Fireplace Inspection offer onto every page of the static site.

The site is a static export (132 WordPress-rendered pages), so "shared
components" are rendered here, once, from site/offer/inspection-offer.config.js
and written into every page between <!-- acp-offer:NAME --> markers.
Re-running is safe: each block is stripped and re-rendered.

    python tools/apply_inspection_offer.py
"""
import io, json, os, re, sys, datetime
from html import escape as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
ORIGIN = 'https://arizonachimneypros.com'
VER = '10'

cfg_src = io.open(os.path.join(SITE, 'offer', 'inspection-offer.config.js'), encoding='utf-8').read()
CFG = json.loads(cfg_src[cfg_src.index('{'):cfg_src.rindex('}') + 1])
G = CFG['general']
BOOK, LEARN, TEL, PHONE = CFG['bookingUrl'], CFG['learnUrl'], CFG['phoneHref'], CFG['phoneDisplay']
TODAY = datetime.date.today().isoformat()

PHONE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 11.5a19.79 19.79 0 01-3.07-8.63A2 2 0 012 .82h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 8.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>'
ARROW = '<svg class="ao-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>'
ICONS = ['<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><circle cx="12" cy="12" r="4"/></svg>',
         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="12" cy="12" r="3"/></svg>',
         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 3h9l5 5v13H6z"/><path d="M9 13h6M9 17h6"/></svg>',
         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 20h16M6 20V9l6-5 6 5v11"/><path d="M10 20v-6h4v6"/></svg>',
         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="M12 7v10M9 10h4.5a2 2 0 010 4H9"/></svg>']

# card photos (site/images/cards/<name>-{480,960}.webp, 4:3) — generated set, prompts in site/images/cards/generated.json
CARD_IMG = {'included': ['g-inc-evaluation', 'g-inc-diagnosis', 'g-inc-findings', 'g-inc-written', 'g-inc-remodel', 'g-inc-honest'],
            'steps': ['g-step-inspect', 'g-step-options', 'g-step-decide']}
CARD_SIZES = {'included': '(max-width: 640px) calc(100vw - 32px), (max-width: 1000px) 50vw, 400px',
              'steps': '(max-width: 900px) calc(100vw - 32px), 400px'}


def card_img(kind, i):
    n = CARD_IMG[kind][i]
    return (f'<img src="/images/cards/{n}-960.webp" srcset="/images/cards/{n}-480.webp 480w, /images/cards/{n}-960.webp 960w" '
            f'sizes="{CARD_SIZES[kind]}" width="960" height="720" alt="" loading="lazy" decoding="async">')


# ───────────────────────── helpers ─────────────────────────
def wrap(name, html):
    return f'<!-- acp-offer:{name} -->{html}<!-- /acp-offer:{name} -->'


def strip(name, text):
    return re.sub(rf'\s*<!-- acp-offer:{name} -->.*?<!-- /acp-offer:{name} -->', '', text, flags=re.S)


def strip_all(text):
    return re.sub(r'\s*<!-- acp-offer:([a-z0-9-]+) -->.*?<!-- /acp-offer:\1 -->', '', text, flags=re.S)


def svc(stype):
    return {**G, **CFG.get(stype, {})} if stype != 'general' else G


def btn(label, href, cls='ao-btn ao-btn--ember', event='inspection_offer_click', placement='', icon=''):
    return (f'<a class="{cls}" href="{href}" data-offer-event="{event}" data-offer-placement="{placement}">'
            f'{icon}{H(label)}</a>')


# ───────────────────────── shared partials ─────────────────────────
def announcement_bar():
    return wrap('bar', f'''
<div class="acp-offer-bar" role="region" aria-label="{H(G["name"])} offer">
  <div class="acp-offer-bar__in">
    <span class="ao-desktop"><b>$99</b> Expert Fireplace Inspection</span>
    <span class="ao-desktop acp-offer-bar__sep" aria-hidden="true"></span>
    <span class="ao-desktop">Clear Findings <span class="ao-credit">&amp; Written Pricing</span></span>
    <span class="ao-mobile"><b>$99</b> Inspection &middot; <span class="ao-credit">Written Pricing</span></span>
    <a class="ao-link" href="{BOOK}" data-offer-event="inspection_offer_click" data-offer-placement="announcement_bar"><span class="ao-desktop">Book Inspection</span><span class="ao-mobile">Book</span>{ARROW}</a>
  </div>
</div>''')


def offer_card_hero():
    items = ['Professional on-site assessment', 'Evaluation relevant to the requested service',
             'Clear explanation of visible findings', 'Repair or remodeling recommendations', 'Written options and pricing']
    return wrap('hero-card', f'''
<div class="hero__card ao-card ao-card--hero acp-offer-anim" data-offer-view="hero_card">
  <span class="ao-eyebrow">The Expert Visit</span>
  <div class="ao-card__price"><b>$99</b><span>per visit</span></div>
  <p class="ao-card__title">Fireplace Inspection &amp; Project Evaluation</p>
  <ul class="ao-card__list">{''.join(f'<li>{H(i)}</li>' for i in items)}</ul>
  <div class="ao-card__credit"><b>One visit &rarr; <em>Written Pricing</em></b><p>You get clear findings and written options before any work begins. No obligation.</p></div>
  {btn('Reserve My Inspection', BOOK, placement='hero_card')}
  <p class="ao-card__foot"><a href="#" data-offer-modal-open data-offer-placement="hero_card" style="color:inherit">What the $99 covers</a> &middot; Respond within 1 hour</p>
</div>''')


def hero_bg():
    return wrap('hero-bg', '''<div class="ao-hero-bg" aria-hidden="true"><img src="/images/hero/home-hero-1672.webp" srcset="/images/hero/home-hero-1000.webp 1000w, /images/hero/home-hero-1672.webp 1672w" sizes="100vw" width="1672" height="941" alt="" fetchpriority="high" decoding="async"></div>''')


def hero_visual():
    return wrap('hero-visual', f'''
<div class="hero__card ao-hero-visual acp-offer-anim" data-offer-view="hero_visual">
  <img class="ao-hero-visual__img" src="/images/hero/fireplace-inspection-hero-720.webp" srcset="/images/hero/fireplace-inspection-hero-720.webp 720w, /images/hero/fireplace-inspection-hero-1080.webp 1080w" sizes="(max-width: 900px) 100vw, 560px" width="720" height="900" alt="Arizona Chimney Pros technician inspecting a gas fireplace in a Phoenix home" fetchpriority="high">
  <div class="ao-hero-visual__banner">
    <div class="ao-hero-visual__price"><b>$99</b><span>Expert Fireplace<br>Inspection</span></div>
    <p class="ao-hero-visual__credit">Clear findings and <em>written pricing before any work</em></p>
    {btn('Book My $99 Inspection', BOOK, placement='hero_visual')}
    <a class="ao-hero-visual__how" href="#" data-offer-modal-open data-offer-placement="hero_visual">What the $99 covers</a>
  </div>
</div>''')



def how_it_works():
    steps = ''.join(f'<div class="ao-step acp-offer-anim"><div class="ao-step__media" aria-hidden="true">{card_img("steps", i)}</div>'
                    f'<div class="ao-step__body"><div class="ao-step__num">0{i + 1}</div><h3>{H(t)}</h3><p>{H(d)}</p></div></div>'
                    for i, (t, d) in enumerate(CFG['steps']))
    return wrap('how', f'''
<section class="ao-section ao-section--ivory" id="how-the-99-works" aria-labelledby="ao-how-title">
  <div class="ao-wrap ao-center acp-offer-anim">
    <span class="ao-eyebrow">Simple. Transparent. Professional.</span>
    <h2 class="ao-title" id="ao-how-title">How the $99 Inspection Works</h2>
    <div class="ao-steps"><div class="ao-steps__line" aria-hidden="true"></div>{steps}</div>
    <p class="ao-closing">You are paying for real expertise &mdash; not a sales visit.</p>
    <div class="ao-cta-row">{btn('Book My Inspection', BOOK, placement='how_it_works')}<a class="ao-btn ao-btn--ghost-dark" href="{LEARN}">See What&rsquo;s Included</a></div>
  </div>
</section>''')


def included(dark=True):
    tiles = ''.join(f'<div class="ao-tile{" ao-tile--credit" if i == 5 else ""} acp-offer-anim"><div class="ao-tile__bg" aria-hidden="true">{card_img("included", i)}</div>'
                    f'<div class="ao-ico">{ICONS[i]}</div><div class="ao-tile__body"><h3>{H(t)}</h3><p>{H(d)}</p></div></div>'
                    for i, (t, d) in enumerate(CFG['included']))
    return wrap('included', f'''
<section class="ao-section {'ao-section--charcoal' if dark else 'ao-section--stone'}" aria-labelledby="ao-inc-title">
  <div class="ao-wrap acp-offer-anim">
    <span class="ao-eyebrow">What&rsquo;s Included</span>
    <h2 class="ao-title" id="ao-inc-title">More Than a Quick Look</h2>
    <p class="ao-lead">Your inspection is designed to give you a clear understanding of the fireplace, the available options, and the expected next step before you approve additional work.</p>
    <div class="ao-grid">{tiles}</div>
    <p class="ao-note">Accessible visual evaluation. Concealed conditions cannot be diagnosed without opening structures; any additional testing is explained and priced first.</p>
  </div>
</section>''')


def inline_card(stype, compact=False, placement='inline'):
    s = svc(stype)
    details = ''
    if stype == 'remodeling' and not compact:
        details = '<ul class="ao-chips">' + ''.join(f'<li>{H(d)}</li>' for d in s.get('details', [])) + '</ul>'
    return wrap('inline-' + placement, f'''
<div class="ao-card ao-card--inline{' ao-card--compact' if compact else ''} acp-offer-anim" data-offer-view="{placement}">
  <div class="ao-card__big">$99<small>{'Written pricing included' if compact else 'Per visit'}</small></div>
  <div><h3>{H(s["inlineTitle"] if not compact else "Start With a Professional $99 Inspection")}</h3><p>{H(s["inlineCopy"] if not compact else G["inlineCopy"])}</p>{details}</div>
  <div class="ao-card__actions">{btn(s["primaryCta"] if not compact else "Book Inspection", BOOK, placement=placement)}
    <a class="ao-btn ao-btn--ghost-dark" href="{TEL}" data-offer-event="inspection_phone_click" data-offer-placement="{placement}">{PHONE_SVG}Call Now</a></div>
</div>''')


def final_cta(stype):
    s = svc(stype)
    return wrap('final', f'''
<section class="ao-final final-cta" id="contact-cta" aria-labelledby="cta-heading">
  <div class="ao-wrap acp-offer-anim" data-offer-view="final_cta">
    <span class="ao-eyebrow">Professional Answers Start Here</span>
    <h2 class="ao-title" id="cta-heading">Book Your $99 Fireplace Inspection</h2>
    <p class="ao-lead">We&rsquo;ll evaluate the fireplace, explain what we find, and provide clear written options &mdash; before any work begins.</p>
    <div class="ao-cta-row">{btn(s["primaryCta"] if stype != "general" else "Book My Inspection", BOOK, placement='final_cta')}
      <a class="ao-btn ao-btn--ghost" href="{TEL}" data-offer-event="inspection_phone_click" data-offer-placement="final_cta">{PHONE_SVG}Call {PHONE}</a></div>
    <p class="ao-area">{H(CFG["serviceAreaLine"])}</p>
  </div>
</section>''')


def footer_block():
    return wrap('footer', f'''
<div class="ao-footer-offer">
  <div><b>$99 <em>Expert Fireplace Inspection</em></b><span>Clear findings and written pricing before any work</span></div>
  {btn('Book Inspection', BOOK, placement='footer')}
</div>''')


def body_end(with_dock):
    dock = f'''
<div class="acp-offer-dock" id="acp-offer-dock" role="region" aria-label="Book a $99 inspection">
  <div class="acp-offer-dock__text"><b><em>$99</em> Inspection</b><span>Written pricing</span></div>
  <a class="acp-offer-dock__call" href="{TEL}" aria-label="Call {PHONE}" data-offer-event="inspection_phone_click" data-offer-placement="mobile_dock">{PHONE_SVG}</a>
  {btn('Book Now', BOOK, event='inspection_mobile_dock_click', placement='mobile_dock')}
</div>
<div class="acp-offer-float" id="acp-offer-float" hidden role="complementary" aria-label="Book a $99 inspection">
  <button class="acp-offer-float__close" type="button" aria-label="Dismiss" data-offer-float-close>&times;</button>
  <small>Need Clear Answers?</small><b>Book a <em>$99</em> Inspection</b><p>Clear findings and written pricing</p>
  {btn('Book Now', BOOK, event='inspection_floating_card_click', placement='floating_card')}
</div>''' if with_dock else ''
    modal = f'''
<div class="acp-offer-modal" id="acp-offer-modal" hidden role="dialog" aria-modal="true" aria-labelledby="acp-offer-modal-title" tabindex="-1">
  <div class="acp-offer-modal__box">
    <button class="acp-offer-modal__close" type="button" aria-label="Close" data-offer-modal-close>&times;</button>
    <span class="ao-eyebrow">The $99 Visit</span>
    <h2 id="acp-offer-modal-title">{H(CFG["feeLabel"])}</h2>
    <p class="acp-offer-modal__flow">$99 Inspection {ARROW} <em>Findings &amp; Written Pricing</em></p>
    <p>{H(CFG["feeModal"])}</p>
    {btn('Book My $99 Inspection', BOOK, placement='credit_modal')}
  </div>
</div>'''
    return wrap('end', dock + modal)


def faq_items(idx):
    return ''.join(f'<div class="faq-item"><button class="faq-item__q" type="button">{H(CFG["faq"][i][0])}<svg class="faq-item__chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg></button><div class="faq-item__a"><p>{H(CFG["faq"][i][1])}</p></div></div>'
                   for i in idx)


# ───────────────────────── page classification ─────────────────────────
def service_type(rel):
    r = rel.lower()
    for kw, t in [('fireplace-remodel', 'remodeling'), ('remodel', 'remodeling'),
                  ('wood-to-gas', 'installation'), ('installation', 'installation'), ('gas-insert-vs', 'installation'),
                  ('gas-fireplace-repair', 'gasRepair'), ('gas-fireplace', 'gasRepair'), ('pilot-light', 'gasRepair'),
                  ('thermopile', 'gasRepair'), ('fireplace-wont-light', 'gasRepair'), ('fireplace-remote', 'gasRepair'),
                  ('gas-log', 'gasRepair'), ('gas-smell', 'gasRepair'), ('fireplace-blower', 'gasRepair'),
                  ('fireplace-glass', 'gasRepair'), ('fireplace-repair-phoenix', 'gasRepair'),
                  ('chimney', 'chimney'), ('creosote', 'chimney'), ('smoke-backing', 'chimney'),
                  ('water-in-fireplace', 'chimney'), ('firebox', 'chimney'), ('damper', 'chimney'), ('monsoon', 'chimney')]:
        if kw in r:
            return t
    return 'general'


def city_of(html, prefix):
    m = re.search(rf'<h1[^>]*>\s*{prefix} in\s*(?:<span[^>]*>)?([A-Za-z .]+?)(?:</span>)?,\s*AZ', html)
    return m.group(1).strip() if m else None


# ───────────────────────── text sweep ─────────────────────────
PHRASES = [
    (r'Free roof inspection \+ \$99 interior diagnostic credited toward any repair', '$99 inspection with written pricing'),
    (r'Free roof inspection \+ 30-minute interior diagnostic', '$99 inspection with written pricing'),
    (r'Free roof and unit inspection', '$99 fireplace inspection with written pricing'),
    (r'(?i)free roof &amp; firebox inspections?', '$99 fireplace &amp; chimney inspection with written pricing'),
    (r'(?i)a free roof inspection', 'a $99 inspection with written pricing'),
    (r'(?i)free roof inspection', '$99 inspection with written pricing'),
    (r'(?i)free estimates — call today', '$99 inspection with written pricing — call today'),
    (r'(?i)free estimates\. call today', '$99 inspection with written pricing. Call today'),
    # earlier runs wrote the credit idea into page prose and data; strip it wherever it appears
    (r'(?i)\$99 inspection credited toward approved work', '$99 inspection with written pricing'),
    (r'(?i)\$99 inspection, credited toward approved work', '$99 inspection with written pricing'),
    (r'(?i)\$99 (on-site|in-home|fireplace|fireplace &amp; chimney|fireplace & chimney) inspection, credited toward approved work', r'$99 \1 inspection with written pricing'),
    (r'(?i)\$99 design &amp; inspection visit, credited toward approved work', '$99 design &amp; inspection visit with written pricing'),
    (r'\$99 Credited to Approved Work', 'Clear Written Pricing'),
    (r'(?i)full \$99 credited toward approved work', 'professional on-site inspection with written pricing'),
    (r'(?i), credited toward approved work', ' with written pricing'),
    (r'(?i) credited toward approved work', ' with written pricing'),
    (r'Get Free Estimate', G['primaryCta']),
    (r'Book Your Free Estimate', 'Book Your $99 Inspection'),
    (r'Free Estimates', 'Clear Written Pricing'),
    (r'Free Estimate', G['navCta']),
    (r'for your free estimate', 'to book your $99 inspection'),
    (r'free on-site estimates?', '$99 on-site inspection with written pricing'),
    (r'free in-home estimates?', '$99 in-home inspection with written pricing'),
    (r'free estimates?', '$99 inspection with written pricing'),
    (r'Free Consultation', '$99 Design &amp; Inspection Visit'),
    (r'free consultation', '$99 design &amp; inspection visit with written pricing'),
    (r'complimentary (?:estimate|inspection|consultation)', '$99 inspection with written pricing'),
    (r'no-obligation (?:estimate|quote)', '$99 inspection'),
    (r'free (?:quote|inspection)', '$99 inspection with written pricing'),
    (r'(?i)free estimates?', '$99 inspection with written pricing'),

    # ── legacy '$99 diagnostic credited toward the repair' promises in older page copy ──
    (r'\(\$99,? credited (?:to|toward) (?:the )?repair\)', '($99 diagnostic)'),
    (r'(?i)Diagnostic visit is \$99, credited toward any repair', 'Diagnostic visit is $99, with written pricing for any repair'),
    (r'(?i)Our diagnostic is \$99 and credited toward the repair', 'Our diagnostic is $99, with written pricing for any repair'),
    (r'(?i)Diagnostic is \$99 and credited toward the repair', 'Diagnostic is $99, with written pricing for any repair'),
    (r'(?i)\$99 diagnostic, credited toward any repair', '$99 diagnostic with written pricing for any repair'),
    (r'(?i)\$99 diagnostic credited toward the repair', '$99 diagnostic with written pricing'),
    (r'(?i)Every visit includes the \$99 diagnostic, credited toward the repair if you proceed', 'Every visit starts with the $99 diagnostic, followed by written pricing'),
    (r'(?i)We diagnose in 30 minutes &mdash; \$99 credited to the repair', 'We diagnose in 30 minutes &mdash; $99 diagnostic, written pricing'),
    (r'(?i)We diagnose in 30 minutes — \$99 credited to the repair', 'We diagnose in 30 minutes — $99 diagnostic, written pricing'),
    (r'(?i)that gets credited toward the repair cost if you move forward with us', 'and we quote any repair in writing before work begins'),
    (r'(?i)that gets credited toward the repair if you move forward with us', 'and we quote any repair in writing before work begins'),
    (r'(?i)gets credited toward the repair if you proceed with us that same visit, so you(?:&#8217;|&rsquo;|\')re not paying twice', 'covers the visit and the diagnosis; any repair is quoted separately in writing'),
    (r'(?i), and that amount is credited toward any repair done on the same visit, so it doesn(?:&#8217;|&rsquo;|\')t add to your total', ', and we quote any repair in writing before doing the work'),
    (r'(?i), and that amount is credited directly toward the repair when you move forward with us', ', and we quote any repair in writing before you decide'),
    (r'(?i), and that amount is credited toward any repair[^.<]*', ', and we quote any repair in writing before doing the work'),
    (r'(?i)\(\$75-\$125\) credited toward the repair, and only quote', '($75-$125) and only quote'),
    (r'(?i)is \$99&ndash;\$189 and is credited toward any repair work you book', 'is $99&ndash;$189, with written pricing for any repair work'),
    (r'(?i)\$99 to \$189, credited toward any repair work you book', '$99 to $189, with written pricing for any repair work'),
    (r'(?i)\$99&ndash;\$189, credited against the repair if you book the work', '$99&ndash;$189, quoted separately from any repair work'),
    (r'(?i)the inspection fee is credited toward that work when you book with us on the same visit or within 14 days', 'the inspection fee covers the visit and the repair is quoted separately in writing'),
    (r'(?i)the inspection fee is credited toward the repair total', 'the inspection fee covers the visit and any repair is quoted separately'),
    (r'(?i), credited toward the repair if you approve work on the same visit', ''),
    (r'(?i), which is credited toward the repair cost if you proceed with us', ''),
    (r'(?i)Clear findings, written options, and the full \$99 credited toward approved repair, installation, or remodeling work', 'Clear findings and written options for repair, installation, or remodeling before any work begins'),
    (r'(?i)Full fee credited toward approved repair, installation, or remodeling work', 'Clear findings and written pricing before any work begins'),
    (r'(?i), the complete \$99 is credited toward the project', ', you receive written pricing before any work begins'),
    (r'(?i)We charge a \$99 diagnostic fee for the inspection and testing visit — that fee is credited in full toward the cost of any repair we complete on the same visit\. You(?:&#8217;|&rsquo;|\')re not paying for a second trip\.', 'We charge a $99 diagnostic fee for the inspection and testing visit, and we quote any repair in writing before the work starts.'),
    (r'(?i)Our \$99 diagnostic fee is credited toward whatever repair we complete on the same visit, so you(?:&#8217;|&rsquo;|\')re not paying for the diagnosis separately if we fix it that day\.', 'Our $99 diagnostic fee covers the visit and the diagnosis; any repair is quoted separately in writing.'),
    (r'(?i), which is credited in full toward the repair if you move forward\.', '.'),
    (r'(?i)If you move forward with the repair, that fee is credited toward the total cost of the job\. You only pay it separately if you decide not to proceed after the diagnosis[^.]*\.', 'The fee covers the visit and the diagnosis, and any repair is quoted separately in writing.'),
    (r'(?i)We charge a \$99 diagnostic fee to come out and identify the problem — that amount gets credited toward your repair if you move forward\.', 'We charge a $99 diagnostic fee to come out and identify the problem.'),
    (r'(?i)We charge a \$99 diagnostic fee that gets credited toward whatever repair you approve, so you(?:&#8217;|&rsquo;|\')re not paying twice — once to find out what(?:&#8217;|&rsquo;|\')s wrong and again to fix it\.', 'We charge a $99 diagnostic fee to find out exactly what is wrong, and quote any repair in writing before fixing it.'),
    (r'(?i) — that fee is credited directly toward the job if you move forward with us\.', '.'),
    # last resort for anything phrased differently
    (r'(?i),? (?:and )?(?:is |gets |that gets )?credited (?:toward|to|against|directly toward) (?:any |the |that )?(?:repair(?: cost| total| work)?|project|work)(?: you book| if you[^.,;<]*| when you[^.,;<]*)?', ''),
    (r'Get a Book \$99 Inspection', 'Book $99 Inspection'),
    (r'(?i)Free written estimates? on every service call\.', 'Written pricing with every $99 inspection.'),
    (r'(?i)free written (?:estimate|quote)s?', 'written pricing'),
    (r'(?i)roof inspection \(free\)', 'roof inspection ($99)'),
    (r'(?i)estimates for fireplace remodeling are free with no obligation', 'our $99 design and inspection visit for fireplace remodeling includes written pricing with no obligation'),
    (r'(?i)\ba free in-home consultation', 'a $99 in-home consultation'),
    (r'(?i)\bFree design consult(?:ation)?s?\b', '$99 design visit'),
]
PROTECT = re.compile(r'(<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<svg[^>]*>.*?</svg>|<!--.*?-->)', re.S | re.I)


def sweep_text(html):
    parts = PROTECT.split(html)
    for i in range(0, len(parts), 2):
        seg = parts[i]
        for pat, rep in PHRASES:
            seg = re.sub(pat, rep.replace('\\', '\\\\'), seg)
        parts[i] = seg
    return ''.join(parts)


LEFT = re.compile(r'free (?:estimate|inspection|consultation|quote|on-site|roof)|complimentary (?:estimate|inspection)|no-cost inspection|book your free|get free', re.I)


def leftovers(html):
    out = []
    for i, seg in enumerate(PROTECT.split(html)):
        if i % 2: continue
        for m in LEFT.finditer(seg):
            out.append(re.sub(r'\s+', ' ', seg[max(0, m.start() - 60):m.end() + 40]))
    return out


# ───────────────────────── JSON-LD ─────────────────────────
RETIRED_FAQ = {'Does the entire $99 go toward the work?', 'Do you offer free estimates?'}
JSON_PHRASES = [(re.compile(p, re.I), re.sub(r'&amp;', '&', r)) for p, r in PHRASES]


def fix_jsonld(html, stype, page_kind):
    def walk(v):
        if isinstance(v, dict): return {k: walk(x) for k, x in v.items()}
        if isinstance(v, list): return [walk(x) for x in v]
        if isinstance(v, str):
            for pat, rep in JSON_PHRASES:
                v = pat.sub(rep, v)
        return v

    def sub(m):
        try:
            d = json.loads(m.group(2))
        except Exception:
            return m.group(0)
        d = walk(d)
        nodes = d.get('@graph') if isinstance(d, dict) and '@graph' in d else [d]
        offer = {'@type': 'Offer', 'name': G['name'], 'price': str(CFG['price']), 'priceCurrency': CFG['currency'],
                 'url': ORIGIN + LEARN,
                 'description': 'Professional on-site fireplace inspection with clear findings and written pricing for any recommended work.'}
        for n in nodes:
            if not isinstance(n, dict): continue
            t = n.get('@type')
            if t == 'Service' or (isinstance(t, list) and 'Service' in t):
                n['offers'] = offer
            if t == 'FAQPage':
                answers = {q: a for q, a in CFG['faq']}
                ents = [e for e in n.get('mainEntity', []) if e.get('name') not in RETIRED_FAQ]
                for e in ents:                       # answers follow the config on every run
                    if e.get('name') in answers:
                        e['acceptedAnswer'] = {'@type': 'Answer', 'text': answers[e['name']]}
                if page_kind == 'service':
                    names = {e.get('name') for e in ents}
                    for i in CFG['serviceFaq']:
                        q, a = CFG['faq'][i]
                        if q not in names:
                            ents.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
                n['mainEntity'] = ents
        return m.group(1) + json.dumps(d, ensure_ascii=False) + '</script>'
    return re.sub(r'(<script[^>]*application/ld\+json[^>]*>)(.*?)</script>', sub, html, flags=re.S)


# ───────────────────────── per-page transforms ─────────────────────────
def head_assets(html):
    html = strip('head', html)
    tags = wrap('head', f'<link rel="stylesheet" href="/offer/inspection-offer.css?v={VER}"><script>document.documentElement.classList.add("acp-offer-js")</script><script src="/offer/inspection-offer.config.js?v={VER}"></script><script src="/offer/inspection-offer.js?v={VER}" defer></script>')
    return html.replace('</head>', tags + '\n</head>', 1)


def cta_label():
    """Full label on wide screens, 'Book $99' where the pill would clip."""
    return f'<span class="ao-cta-long">{H(G["navCta"])}</span><span class="ao-cta-short">Book $99</span>'


def header_cta(html):
    attrs = (f'href="{BOOK}" title="Professional on-site inspection with written pricing" aria-label="{H(G["navCta"])} — professional on-site inspection with written pricing" '
             f'data-offer-event="inspection_offer_click" data-offer-placement="header"')
    # homepage header: the Free Estimate pill
    html = re.sub(r'<a class="btn btn--primary" href="/contact/"[^>]*>(?:Free Estimate|Book \$99 Inspection)</a>',
                  lambda m: f'<a class="btn btn--primary" {attrs}>{cta_label()}</a>', html, count=1)
    # every other page: the "Call Now" pill in .header__actions (the phone number link stays beside it)
    def in_actions(m):
        return re.sub(r'<a href="(?:tel:[^"]*|/contact/)" class="btn btn--primary"[^>]*>(?:Call Now|Free Estimate|Get Free Estimate|Book \$99 Inspection)</a>',
                      lambda x: f'<a class="btn btn--primary" {attrs}>{cta_label()}</a>', m.group(0), count=1)
    return re.sub(r'<div class="header__actions">.*?</div>', in_actions, html, count=1, flags=re.S)


def phone_icons(html):
    """Header phone link and the floating call button become icon-only round buttons.
    Lookaheads require href=tel: so the CSS comment that quotes <a class="header__phone"> is left alone."""
    head = f'<a href="{TEL}" class="header__phone ao-phone" aria-label="Call {H(PHONE)}">{PHONE_SVG}</a>'
    flt = f'<a href="{TEL}" class="float-cta" aria-label="Call Arizona Chimney Pros">{PHONE_SVG}</a>'
    html = re.sub(r'<a (?=[^>]*class="header__phone)(?=[^>]*href="tel:)[^>]*>.*?</a>', head, html, flags=re.S)
    html = re.sub(r'<a (?=[^>]*class="float-cta)(?=[^>]*href="tel:)[^>]*>.*?</a>', flt, html, flags=re.S)
    return html


SITE_HEADER = io.open(os.path.join(os.path.dirname(__file__), 'site-header.html'), encoding='utf-8').read()


def site_header(html):
    """Pages without the real header (old self-contained WP pages) get it injected; their ad-hoc nav is hidden by CSS."""
    body = html[html.find('<body'):]
    if 'class="header__inner"' in body or 'class="container header__inner"' in body:
        return html
    html = re.sub(r'<body([^>]*?)class="', r'<body\1class="acp-injected-header ', html, count=1)
    return re.sub(r'(<div class="wp-site-blocks"[^>]*>)', lambda m: m.group(1) + wrap('site-header', SITE_HEADER), html, count=1)


def _img(name, widths, w, h, sizes, alt='', extra=''):
    srcset = ', '.join(f'/images/about/{name}-{x}.webp {x}w' for x in widths)
    return (f'<img src="/images/about/{name}-{widths[-2] if len(widths) > 1 else widths[0]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{alt}" decoding="async" {extra}>')


def about_page(html):
    """Idempotent: reads the copy back out of either the original inline-styled sections or the converted ones."""
    sec = re.compile(r'<section[^>]*>.*?</section>', re.S)
    secs = list(sec.finditer(html))
    hero = next((m for m in secs if 'background:#0f0f0f;padding:100px' in m.group(0)[:120] or 'class="ao-about-hero"' in m.group(0)[:60]), None)
    story = next((m for m in secs if 'grid-template-columns:1fr 1fr;gap:64px' in m.group(0)[:160] or 'class="ao-about-story"' in m.group(0)[:60]), None)
    if not hero or not story:
        return html
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', hero.group(0), re.S).group(1).strip()
    lead = re.search(r'</h1>\s*<p[^>]*>(.*?)</p>', hero.group(0), re.S).group(1).strip()
    new_hero = f"""<section class="ao-about-hero" aria-labelledby="about-h1">
  <div class="ao-about-hero__bg" aria-hidden="true">{_img('about-hero', [1000, 1600, 2048], 2048, 1152, '100vw', extra='fetchpriority="high"')}</div>
  <div class="ao-about-hero__inner acp-offer-anim">
    <span class="ao-eyebrow">About Us</span>
    <h1 id="about-h1">{h1}</h1>
    <p>{lead}</p>
    <div class="ao-cta-row">{btn(G['primaryCta'], BOOK, placement='about_hero')}<a class="ao-btn ao-btn--ghost" href="{TEL}">{PHONE_SVG} Call {H(PHONE)}</a></div>
  </div>
</section>"""
    st = story.group(0)
    h2 = re.search(r'<h2[^>]*>(.*?)</h2>', st, re.S).group(1).strip()
    paras = [p.strip() for p in re.findall(r'<p[^>]*>(.*?)</p>', st, re.S)]
    stats = re.findall(r'<div style="font-size:2\.2rem[^"]*">(.*?)</div>\s*<div style="font-size:0\.875rem[^"]*">(.*?)</div>', st, re.S) \
        or re.findall(r'<b>(.*?)</b><span>(.*?)</span>', st, re.S)
    new_story = f"""<section class="ao-about-story" aria-labelledby="about-story-h2">
  <div class="ao-wrap ao-about-story__grid">
    <figure class="ao-about-story__media acp-offer-anim">{_img('about-story', [700, 1100], 1100, 1375, '(max-width: 900px) calc(100vw - 32px), 520px', alt='Arizona Chimney Pros technician servicing a gas fireplace burner in a Phoenix-area home', extra='loading="lazy"')}</figure>
    <div class="ao-about-story__text acp-offer-anim">
      <h2 id="about-story-h2">{h2}</h2>
      {''.join(f'<p>{p}</p>' for p in paras)}
    </div>
  </div>
  <div class="ao-wrap"><div class="ao-about-stats acp-offer-anim">{''.join(f'<div><b>{n.strip()}</b><span>{l.strip()}</span></div>' for n, l in stats)}</div></div>
</section>"""
    html = html[:hero.start()] + new_hero + html[hero.end():story.start()] + new_story + html[story.end():]
    # the truck wrap photo carries the retired phone number — drop that section until a current photo exists
    html = re.sub(r'<section(?: class="ao-about-truck")? style="padding:0 0 64px;">\s*<div[^>]*>\s*<img[^>]*arizona-chimney-pros-truck[^>]*>\s*</div>\s*</section>', '', html, count=1)
    html = re.sub(r'<body([^>]*?)class="', lambda m: '<body' + m.group(1) + 'class="acp-about ', html, count=1)
    html = html.replace('/wp-content/uploads/2026/05/arizona-chimney-pros-truck.png', '/images/about/about-hero-1600.webp')   # JSON-LD primary image: the truck wrap shows the retired number
    html = html.replace('<section style="padding:72px 24px;max-width:700px;margin:0 auto;text-align:center;">',
                        '<section class="ao-about-cta" style="padding:72px 24px;max-width:700px;margin:0 auto;text-align:center;">', 1)
    return html


def page_hero_ctas(html, stype):
    """Service/guide hero: booking becomes the primary action, with the service-specific label."""
    s = svc(stype)
    label = s['primaryCta'] if stype != 'general' else G['primaryCta']
    pat = re.compile(r'(<a href="tel:[^"]*" class="btn btn--)primary( btn--lg">.*?</a>)\s*<a href="/contact/" class="btn btn--(?:ghost|primary) btn--lg"[^>]*>[^<]*</a>', re.S)
    def sub(m):
        return (f'<a href="{BOOK}" class="btn btn--primary btn--lg" data-offer-event="inspection_offer_click" data-offer-placement="page_hero">{H(label)}</a> '
                + m.group(1) + 'ghost' + m.group(2))
    return re.sub(r'<section class="page-hero.*?</section>', lambda sec: pat.sub(sub, sec.group(0), count=1), html, count=1, flags=re.S)


def home_hero(html):
    html = re.sub(r'(<span class="label">)[^<]*(</span>\s*<h1 id="hero-heading")', r'\1Arizona Fireplace Specialists\2', html, count=1)
    html = re.sub(r'(<h1 id="hero-heading" class="hero__title">).*?(</h1>)', r'\1Know Exactly What <span class="text-orange">Your Fireplace Needs.</span>\2', html, count=1, flags=re.S)
    html = re.sub(r'(<p class="hero__subtitle">).*?(</p>)',
                  r'\1Book a professional on-site fireplace inspection for $99. Get clear findings, written options, and expert guidance for repair, installation, or a complete fireplace transformation. Clear answers before any work begins.\2', html, count=1, flags=re.S)
    ctas = (f'<div class="hero__ctas"><a class="btn btn--primary btn--lg" href="{BOOK}" data-offer-event="inspection_offer_click" data-offer-placement="hero">{H(G["primaryCta"])}</a>'
            f'<a class="btn btn--ghost btn--lg" href="{TEL}" data-offer-event="inspection_phone_click" data-offer-placement="hero">Call Now</a></div>'
            + wrap('hero-benefits', '<ul class="ao-hero-benefits"><li>Professional On-Site Evaluation</li><li>Clear Findings</li><li>Written Pricing</li><li>No Obligation</li></ul>'))
    html = strip('hero-benefits', html)
    html = re.sub(r'<div class="hero__ctas">.*?</div>', lambda m: ctas, html, count=1, flags=re.S)
    html = strip('hero-card', html); html = strip('hero-visual', html); html = strip('hero-bg', html); html = strip('hero-pill', html)
    html = re.sub(r'<div class="hero__card">.*?</div>\s*(?=<div class="hero__badge")', '', html, count=1, flags=re.S)   # original "Our Specialties" card
    # full-bleed photo behind a centered hero (the side card/visual is hidden by CSS)
    html = re.sub(r'<section class="hero(?: ao-hero--full)?"', '<section class="hero ao-hero--full"', html, count=1)
    html = re.sub(r'(<section class="hero ao-hero--full"[^>]*>)', lambda m: m.group(1) + hero_bg(), html, count=1)
    html = html.replace('<h1 id="hero-heading"', wrap('hero-pill', '<div class="ao-hero-pill"><b>$99</b> Expert Fireplace Inspection <span>&middot; written pricing, no obligation</span></div>') + '\n<h1 id="hero-heading"', 1)
    # flow band right after the hero, then How/Included before the before-after gallery
    html = strip('flow', html); html = strip('how', html); html = strip('included', html)
    html = html.replace('<section class="ba-v2-section', how_it_works() + '\n' + included(True) + '\n<section class="ba-v2-section', 1)
    # before/after connection
    html = strip('ba-lead', html); html = strip('ba-cta', html)
    lead = wrap('ba-lead', '<div class="ao-ba-lead acp-offer-anim"><span class="ao-eyebrow">Your Inspection Can Be the First Step</span><h2 class="ao-title">From &ldquo;What Does This Need?&rdquo; to a Complete Transformation</h2><p class="ao-lead">Whether your fireplace needs a focused repair or a complete redesign, the $99 inspection gives you clear options and written pricing before the project begins.</p></div>')
    html = html.replace('<div class="ba-v2-hdr">', lead + '\n<div class="ba-v2-hdr">', 1)
    i = html.find('<section class="ba-v2-section'); j = html.find('</section>', i)
    html = html[:j] + wrap('ba-cta', f'<div class="ao-ba-cta">{btn("Let&rsquo;s Inspect Your Fireplace", BOOK, placement="before_after")}</div>') + html[j:]
    # FAQ: swap the "free estimates" item for the real answer, then add two more
    html = re.sub(r'<div class="faq-item">\s*<button class="faq-item__q">(?:<br />)?\s*Do you offer free estimates\?.*?</div>\s*</p></div>',
                  faq_items([0]), html, count=1, flags=re.S)
    html = re.sub(r'<div class="faq-item"><button class="faq-item__q" type="button">' + re.escape(CFG['faq'][0][0]) + r'<svg.*?</div></div>',
                  lambda m: faq_items([0]), html, count=1, flags=re.S)
    html = strip('home-faq', html)
    html = html.replace('</div>\n<p><!-- ===== FINAL', wrap('home-faq', faq_items([2, 3])) + '</div>\n<p><!-- ===== FINAL', 1) if '<!-- ===== FINAL' in html else html
    return html


def service_faq(html):
    html = strip('svc-faq', html)
    return re.sub(r'(<div class="faq-list">.*?)(</div>\s*</div>\s*</div>\s*</section>)',
                  lambda m: m.group(1) + wrap('svc-faq', faq_items(CFG['serviceFaq'])) + m.group(2), html, count=1, flags=re.S)


def replace_final(html, stype):
    html = strip('final', html)
    if re.search(r'<section class="final-cta"', html):
        return re.sub(r'<section class="final-cta".*?</section>', lambda m: final_cta(stype), html, count=1, flags=re.S)
    return html.replace('<footer class="wp-block-template-part">', final_cta(stype) + '\n<footer class="wp-block-template-part">', 1)


def service_cards(html, stype, kind):
    html = strip('inline-inline', html); html = strip('inline-compact', html)
    if kind == 'service':
        html = re.sub(r'(<section class="section section--raised">.*?</section>)', lambda m: m.group(1) + '\n' + inline_card(stype, False, 'inline'), html, count=1, flags=re.S)
    html = html.replace('<!-- acp-offer:final -->', inline_card(stype, True, 'compact') + '\n<!-- acp-offer:final -->', 1)
    return html


def footer(html):
    html = strip('footer', html)
    html = html.replace('<footer class="acp-footer-clean" role="contentinfo"> <div class="inner">', '<footer class="acp-footer-clean" role="contentinfo"> <div class="inner">' + footer_block(), 1) \
        if '<footer class="acp-footer-clean" role="contentinfo"> <div class="inner">' in html else \
        re.sub(r'(<footer class="acp-footer-clean"[^>]*>\s*<div class="inner">)', lambda m: m.group(1) + footer_block(), html, count=1)
    if f'href="{LEARN}">$99 Inspection</a>' not in html:
        html = html.replace('<li><a href="/about/">About Us</a></li>', f'<li><a href="{LEARN}">$99 Inspection</a></li> <li><a href="/about/">About Us</a></li>', 1)
    return html


def dedupe_brand(title):
    """'X | Arizona Chimney Pros - Arizona Chimney Pros' -> 'X | Arizona Chimney Pros'."""
    core = re.sub(r'\s*[-|–]\s*Arizona Chimney Pros\s*$', '', title)
    return core if 'Arizona Chimney Pros' in core else title


def metadata(html, rel, stype, page_kind):
    def set_tag(h, pat, new):
        return re.sub(pat, new, h, count=1) if re.search(pat, h) else h
    html = re.sub(r'<title>([^<]*)</title>', lambda m: '<title>' + dedupe_brand(m.group(1).strip()) + '</title>', html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")([^"]*)(")', lambda m: m.group(1) + dedupe_brand(m.group(2).strip()) + m.group(3), html, count=1)
    if rel == 'index.html':
        html = set_tag(html, r'<title>[^<]*</title>', '<title>Arizona Fireplace Services | $99 Expert Inspection</title>')
        desc = 'Book a $99 expert fireplace inspection with Arizona Chimney Pros. Get clear findings and written pricing for repair, installation, or remodeling before any work begins.'
        html = set_tag(html, r'<meta property="og:title" content="[^"]*"', '<meta property="og:title" content="Arizona Fireplace Services | $99 Expert Inspection"')
        html = set_tag(html, r'<meta property="og:description" content="[^"]*"', f'<meta property="og:description" content="{desc}"')
        if '<meta name="description"' not in html:
            html = html.replace('<title>', f'<meta name="description" content="{desc}">\n<title>', 1)
    elif rel == 'contact/index.html':
        desc = 'Book your $99 expert fireplace inspection. Clear findings and written options for repair, installation, or remodeling before any work begins.'
        html = set_tag(html, r'<title>[^<]*</title>', '<title>Book a $99 Fireplace Inspection | Arizona Chimney Pros</title>')
        html = set_tag(html, r'<meta property="og:title" content="[^"]*"', '<meta property="og:title" content="Book a $99 Fireplace Inspection | Arizona Chimney Pros"')
        html = set_tag(html, r'<meta property="og:description" content="[^"]*"', f'<meta property="og:description" content="{desc}"')
        if '<meta name="description"' not in html:
            html = html.replace('<title>', f'<meta name="description" content="{desc}">\n<title>', 1)
    elif page_kind == 'service':
        city = city_of(html, 'Gas Fireplace Repair') if stype == 'gasRepair' else city_of(html, 'Chimney Inspection')
        if city and stype == 'gasRepair' and 'gas-fireplace-repair' in rel:
            t = f'Gas Fireplace Repair in {city}, AZ | $99 Diagnostic'
            html = set_tag(html, r'<title>[^<]*</title>', f'<title>{t}</title>')
            html = set_tag(html, r'<meta property="og:title" content="[^"]*"', f'<meta property="og:title" content="{t}"')
        elif city and 'chimney-inspection' in rel:
            t = f'Chimney Inspection in {city}, AZ | $99 Visit'
            html = set_tag(html, r'<title>[^<]*</title>', f'<title>{t}</title>')
            html = set_tag(html, r'<meta property="og:title" content="[^"]*"', f'<meta property="og:title" content="{t}"')
    return html


def contact_page(html):
    html = re.sub(r'<h1>Book Your Free <em>Fireplace Estimate</em></h1>|<h1>Book Your \$99 Expert <em>Fireplace Inspection</em></h1>',
                  '<h1>Book Your $99 Expert <em>Fireplace Inspection</em></h1>', html, count=1)
    html = re.sub(r'(<div class="acp-book__eyebrow">)[^<]*(</div>)', r'\1$99 Inspection &middot; Written Pricing\2', html, count=1)
    html = re.sub(r'(<p class="acp-book__sub">).*?(</p>)', r'\1Tell us what is happening with your fireplace or what you want to transform. Our team will contact you to confirm the appointment details.\2', html, count=1, flags=re.S)
    html = re.sub(r'<div class="acp-bookform-head">.*?</div>\s*<div id="acp-wizard-mount">',
                  lambda m: '<div class="acp-bookform-head"><div class="kicker">$99 Expert Inspection</div><h3>Request My Inspection</h3><p>Tell us what you need and when. We&rsquo;ll call to confirm your appointment.</p></div>\n<div id="acp-wizard-mount">', html, count=1, flags=re.S)
    html = strip('booksum', html)
    summary = wrap('booksum', f'''<div class="ao-booksum" data-offer-view="booking_summary">
  <div class="ao-booksum__head"><b>Your Inspection Includes</b><span class="ao-booksum__price">Inspection fee<em>$99</em></span></div>
  <ul><li>Professional on-site evaluation</li><li>Clear findings and recommendations</li><li>Written repair, installation, or remodeling options</li><li>No obligation to approve additional work</li></ul>
  <p>The $99 covers the professional visit and evaluation. Any recommended work is quoted separately in writing. <a href="#" data-offer-modal-open data-offer-placement="booking_summary">What the $99 covers</a></p>
</div>''')
    html = html.replace('<div class="acp-bookform-head">', summary + '\n<div class="acp-bookform-head">', 1)
    # the no-JS fallback form's submit button
    html = re.sub(r'(<button[^>]*class="[^"]*wp-block-button__link[^"]*"[^>]*type="submit"[^>]*>)[^<]*(</button>)', r'\1Request My $99 Inspection\2', html, count=1)
    return html


def inspection_page(contact_html):
    html = contact_html
    html = html.replace(f'{ORIGIN}/contact/', f'{ORIGIN}{LEARN}')
    html = html.replace('page-id-315', 'page-id-315 acp-inspection-page')
    html = re.sub(r'<title>[^<]*</title>', '<title>$99 Fireplace Inspection | Arizona Chimney Pros</title>', html, count=1)
    desc = 'Book a professional $99 fireplace inspection with Arizona Chimney Pros. Get clear findings and written options for repair, installation, or remodeling before any work begins.'
    html = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{desc}"', html, count=1)
    html = re.sub(r'<meta property="og:title" content="[^"]*"', '<meta property="og:title" content="$99 Fireplace Inspection | Arizona Chimney Pros"', html, count=1)
    html = re.sub(r'<meta property="og:description" content="[^"]*"', f'<meta property="og:description" content="{desc}"', html, count=1)
    html = html.replace('&rsaquo; Contact</div>', f'&rsaquo; $99 Inspection</div>')
    # JSON-LD: rename the page, add the FAQ
    def sub(m):
        try: d = json.loads(m.group(2))
        except Exception: return m.group(0)
        nodes = d.get('@graph') if isinstance(d, dict) and '@graph' in d else [d]
        for n in nodes:
            if not isinstance(n, dict): continue
            if n.get('@type') == 'WebPage':
                n['name'] = '$99 Fireplace Inspection | Arizona Chimney Pros'; n['description'] = desc
            if n.get('@type') == 'BreadcrumbList':
                for it in n.get('itemListElement', []):
                    if it.get('name') in ('Contact', 'Contact Arizona Chimney Pros'): it['name'] = '$99 Inspection'
        if isinstance(d, dict) and '@graph' in d and not any(isinstance(n, dict) and n.get('@type') == 'FAQPage' for n in nodes):
            d['@graph'].append({'@type': 'FAQPage', '@id': f'{ORIGIN}{LEARN}#faq',
                                'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in CFG['faq']]})
            d['@graph'].append({'@type': 'Service', 'name': G['name'], 'serviceType': 'Fireplace inspection', 'provider': {'@id': f'{ORIGIN}/#organization'},
                                'areaServed': 'Phoenix metro area, Arizona', 'url': f'{ORIGIN}{LEARN}',
                                'offers': {'@type': 'Offer', 'name': G['name'], 'price': str(CFG['price']), 'priceCurrency': CFG['currency'], 'url': ORIGIN + LEARN,
                                           'description': 'Professional on-site fireplace inspection with clear findings and written pricing for any recommended work.'}})
        return m.group(1) + json.dumps(d, ensure_ascii=False) + '</script>'
    html = re.sub(r'(<script[^>]*application/ld\+json[^>]*>)(.*?)</script>', sub, html, count=1, flags=re.S)
    cases = [('Gas Fireplace Repair', CFG['gasRepair']['inlineCopy'], '/services/gas-fireplace-repair/', CFG['gasRepair']['name']),
             ('Fireplace Remodeling', CFG['remodeling']['inlineCopy'], '/services/fireplace-remodeling/', CFG['remodeling']['name']),
             ('Fireplace Installation', CFG['installation']['inlineCopy'], '/services/fireplace-installation/', CFG['installation']['name']),
             ('Chimney Services', CFG['chimney']['inlineCopy'], '/services/chimney-inspection-phoenix/', CFG['chimney']['name'])]
    usecases = ''.join(f'<div class="ao-usecase acp-offer-anim"><span class="ao-eyebrow">{H(t)}</span><h3>{H(n)}</h3><p>{H(c)}</p><a href="{u}">Learn about {H(t).lower()} &rarr;</a></div>' for t, c, u, n in cases)
    faq = ''.join(f'<details><summary>{H(q)}</summary><p>{H(a)}</p></details>' for q, a in CFG['faq'])
    content = wrap('inspection-body', f'''
<section class="acp-offer-page-hero acp-offer-anim" aria-labelledby="ao-page-title">
  <div class="acp-offer-page-hero__img" style="background-image:url('/images/before-after/fireplace-remodel-limestone-after.webp')" role="img" aria-label="Remodeled fireplace with cast limestone mantel"></div>
  <div class="acp-offer-page-hero__shade" aria-hidden="true"></div>
  <div class="ao-wrap">
    <div>
      <span class="ao-eyebrow">Arizona Fireplace Specialists</span>
      <h1 id="ao-page-title">$99 Expert <em>Fireplace Inspection</em></h1>
      <p class="ao-lead">{H(G["description"])} One professional visit, clear answers, and no obligation.</p>
      <ul class="ao-hero-benefits"><li>Professional On-Site Evaluation</li><li>Clear Findings</li><li>Written Pricing</li><li>No Obligation</li></ul>
      <div class="ao-cta-row" style="justify-content:flex-start">{btn(G["primaryCta"], "#book", placement="inspection_hero")}<a class="ao-btn ao-btn--ghost" href="{TEL}" data-offer-event="inspection_phone_click" data-offer-placement="inspection_hero">{PHONE_SVG}Call {PHONE}</a></div>
    </div>
    {offer_card_hero().replace('hero__card ', '')}
  </div>
</section>
{included(False)}
{how_it_works()}
<section class="ao-section ao-section--stone" aria-labelledby="ao-uc-title">
  <div class="ao-wrap acp-offer-anim"><span class="ao-eyebrow">Built Around Your Project</span><h2 class="ao-title" id="ao-uc-title">One Visit, Four Ways to Use It</h2>
  <p class="ao-lead">The same $99 visit, with the evaluation focused on what you actually need.</p><div class="ao-usecases">{usecases}</div></div>
</section>
<section class="ao-section ao-section--charcoal" aria-labelledby="ao-ba-title">
  <div class="ao-wrap acp-offer-anim"><span class="ao-eyebrow">Your Inspection Can Be the First Step</span><h2 class="ao-title" id="ao-ba-title">From &ldquo;What Does This Need?&rdquo; to a Complete Transformation</h2>
  <p class="ao-lead">Whether your fireplace needs a focused repair or a complete redesign, the $99 inspection gives you clear options before the project begins.</p>
  <div class="ao-ba-pair"><figure><img src="/images/before-after/fireplace-remodel-granite-before.webp" alt="Before – painted brick wood-burning fireplace" loading="lazy" width="640" height="800"><figcaption>Before</figcaption></figure>
  <figure><img src="/images/before-after/fireplace-remodel-granite-after.webp" alt="After – linear gas fireplace with black granite surround and walnut mantel" loading="lazy" width="640" height="800"><figcaption>After</figcaption></figure></div></div>
</section>
<section class="ao-section ao-section--ivory" aria-labelledby="ao-faq-title">
  <div class="ao-wrap ao-center acp-offer-anim"><span class="ao-eyebrow">Straight Answers</span><h2 class="ao-title" id="ao-faq-title">Frequently Asked Questions</h2><div class="ao-faq">{faq}</div></div>
</section>
<div id="book"></div>''')
    html = strip('inspection-body', html)
    html = html.replace('<section class="acp-book"', content + '\n<section class="acp-book"', 1)
    html = html.replace('<h1>Book Your $99 Expert <em>Fireplace Inspection</em></h1>', '<h2 style="font:inherit;margin:0">Request Your $99 <em>Fireplace Inspection</em></h2>', 1)
    html = html.replace('data-offer-service="general"', 'data-offer-service="general" data-offer-page="inspection"')
    return html


def process(rel, html):
    kind = ('home' if rel == 'index.html' else 'contact' if rel == 'contact/index.html'
            else 'service' if rel.startswith('services/') or rel.split('/')[0] in ('chimney-repair-tempe', 'fireplace-repair-phoenix')
            else 'guide' if rel.startswith(('guides/', 'blog/')) or rel == 'about/index.html'
            else 'other')
    stype = service_type(rel) if kind in ('service', 'guide') else 'general'
    html = strip_all(html)
    html = head_assets(html)
    def body_tag(m):
        attrs = re.sub(r' data-offer-service="[^"]*"', '', m.group(1)).replace('acp-offer-has-dock ', '').replace('acp-injected-header ', '').replace('acp-about ', '')
        return '<body' + attrs + ' data-offer-service="' + stype + '">'
    html = re.sub(r'<body([^>]*)>', body_tag, html, count=1)
    html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + announcement_bar(), html, count=1)
    html = site_header(html)
    html = header_cta(html)
    html = phone_icons(html)
    if rel == 'about/index.html':
        html = about_page(html)
    html = html.replace('<div class="trust-item"><br />Free Estimates</div>', '<div class="trust-item"><br />Clear Written Pricing</div>')
    if kind == 'home':
        html = home_hero(html)
    if kind == 'contact':
        html = contact_page(html)
    if kind in ('home', 'service', 'guide', 'other') and rel not in ('404.html', 'llms-txt/index.html'):
        html = replace_final(html, stype)
        if kind in ('service', 'guide'):
            html = page_hero_ctas(html, stype)
            html = service_cards(html, stype, kind)
        if kind == 'service':
            html = service_faq(html)
    html = footer(html)
    html = metadata(html, rel, stype, kind)
    html = fix_jsonld(html, stype, kind)
    html = sweep_text(html)
    with_dock = kind != 'contact' and rel not in ('404.html',)
    if with_dock:
        html = re.sub(r'<body([^>]*?)class="', r'<body\1class="acp-offer-has-dock ', html, count=1)
    html = html.replace('</body>', body_end(with_dock) + '\n</body>', 1)
    return html, kind


def main():
    report = {'pages': 0, 'left': {}}
    contact_html = None
    for root, _, files in os.walk(SITE):
        for fn in files:
            if not fn.endswith('.html'): continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, SITE).replace('\\', '/')
            if rel == 'inspection/index.html': continue
            html = io.open(p, encoding='utf-8', errors='surrogateescape').read()
            new, kind = process(rel, html)
            if kind == 'contact': contact_html = new
            io.open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(new)
            report['pages'] += 1
            lf = leftovers(new)
            if lf: report['left'][rel] = lf
    # dedicated page
    insp = inspection_page(contact_html)
    insp, _ = (insp, None)
    os.makedirs(os.path.join(SITE, 'inspection'), exist_ok=True)
    io.open(os.path.join(SITE, 'inspection', 'index.html'), 'w', encoding='utf-8', newline='').write(insp)
    # sitemaps
    for sm in ('page-sitemap.xml', 'sitemap-1.xml'):
        sp = os.path.join(SITE, sm)
        if not os.path.exists(sp): continue
        x = io.open(sp, encoding='utf-8').read()
        if f'{ORIGIN}{LEARN}</loc>' not in x:
            x = x.replace('</urlset>', f'<url><loc>{ORIGIN}{LEARN}</loc><lastmod>{TODAY}T00:00:00+00:00</lastmod></url>\n</urlset>')
            io.open(sp, 'w', encoding='utf-8', newline='').write(x)
    print('pages stamped:', report['pages'], '| inspection page written | leftovers in', len(report['left']), 'pages')
    for rel, lf in list(report['left'].items())[:12]:
        print('  ', rel); [print('      -', s[:140]) for s in lf[:3]]


if __name__ == '__main__':
    main()
