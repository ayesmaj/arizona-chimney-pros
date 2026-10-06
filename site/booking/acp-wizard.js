/*
 * Arizona Chimney Pros — booking wizard v2 (mockup build)
 * Runs on arizonachimneypros.com/contact
 *
 * Progressive enhancement over the existing Jetpack Forms block:
 *  - The real form stays in the page. Without JS, visitors see and use it.
 *  - With JS, the form is parked off-screen and a 6-step wizard renders in
 *    the #acp-wizard-mount panel. On submit, the wizard writes its answers
 *    into the real form's fields and submits THAT form, so every existing
 *    hook keeps working: Jetpack anti-spam (JWT, fill-duration, Akismet),
 *    the branded admin + customer emails, and the CRM lead intake.
 *  - Any error during boot restores the original form (fail-open).
 *
 * Address autocomplete: Photon (photon.komoot.io) — keyless, CORS-open OSM
 * geocoder, verified working for Phoenix-metro house numbers. "Verified"
 * requires a picked suggestion with a house number; the structured fields
 * (street/city/zip) are still validated when typed by hand, so junk like
 * "mcke" can never submit. If the API is down the step degrades to strict
 * manual entry instead of blocking the lead.
 *
 * Served from the acp-platform Vercel app because WordPress entity-encodes
 * "&" inside inline scripts (turning "&&" into a SyntaxError). External
 * files are immune, so all logic lives here and only a <script src> loader
 * sits in the page.
 */
(function () {
  "use strict";

  var VERSION = "2";
  var PHOTON = "https://photon.komoot.io/api/";
  var GEO_BIAS = { lat: 33.45, lon: -112.07 }; // central Phoenix
  var SERVICE_CITIES = [
    "Phoenix", "Scottsdale", "Mesa", "Chandler", "Gilbert", "Paradise Valley",
    "Cave Creek", "Anthem", "Glendale", "Tempe", "Surprise", "Goodyear",
    "Queen Creek", "Fountain Hills", "Peoria", "Avondale", "Buckeye",
    "Laveen", "Tolleson", "Apache Junction",
  ];
  var ISSUE_CHIPS = [
    "Won't turn on", "Pilot light issue", "Smells like gas", "Smoke coming in",
    "Cracks / damage", "Needs cleaning", "Remodel project", "Just an inspection",
  ];
  var PHONE_DISPLAY = "(602) 536-8034";
  var PHONE_HREF = "+16025368034";

  /* ── tiny helpers ─────────────────────────────────────────────────── */

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function esc(s) {
    // Suggestion text comes from an external API and is rendered via
    // innerHTML, so it must be properly escaped.
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  /** Set a Jetpack field's value so the WP Interactivity store notices. */
  function setField(input, value) {
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }
  function svg(path) {
    return "<svg width='15' height='15' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>" + path + "</svg>";
  }
  var ICONS = {
    service: svg("<path d='M12 2c1 4-4 6-4 10a4 4 0 0 0 8 0c0-2-1-3-1-3s3 1 3 5a6 6 0 0 1-12 0C6 8 11 7 12 2z'/>"),
    issue: svg("<path d='M21 11.5a8.4 8.4 0 0 1-8.5 8.3 8.6 8.6 0 0 1-3.9-.9L3 20l1.1-5.4a8.2 8.2 0 0 1-.9-3.8A8.4 8.4 0 0 1 11.7 2.5h.5a8.4 8.4 0 0 1 8.8 8.3z'/>"),
    schedule: svg("<rect x='3' y='4' width='18' height='18' rx='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/>"),
    contact: svg("<path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/><circle cx='12' cy='7' r='4'/>"),
    address: svg("<path d='M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z'/><circle cx='12' cy='10' r='3'/>"),
    review: svg("<path d='M22 11.1V12a10 10 0 1 1-5.9-9.1'/><polyline points='22 4 12 14 9 11'/>"),
    search: svg("<circle cx='11' cy='11' r='8'/><line x1='21' y1='21' x2='16.7' y2='16.7'/>"),
    pin: svg("<path d='M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z'/><circle cx='12' cy='10' r='3'/>"),
    check: svg("<polyline points='20 6 9 17 4 12'/>"),
  };

  /* ── styles (wizard card only — page layout CSS lives in the page) ── */

  var CSS = "" +
".acpw{--ink:#f5f2ed;--dim:#cfc9bc;--faint:#a59e90;--ember:#ff6a1a;--ember2:#f9a11b;--gold:#c9a86a;--panel:#211f1c;--panel2:#262421;--line:#3a362f;--ok:#5fbf7a;--err:#ff6b6b;" +
"font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:var(--ink);background:linear-gradient(165deg,#201e1b,#171614 62%);border:1px solid var(--line);border-radius:18px;padding:24px 24px 20px;position:relative;overflow:visible;box-shadow:0 20px 55px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.04)}" +
".acpw *{box-sizing:border-box}" +
".acpw-steps{display:flex;align-items:flex-start;margin:2px 0 20px}" +
".acpw-st{flex:0 0 auto;display:flex;flex-direction:column;align-items:center;gap:6px;width:52px}" +
".acpw-st .c{width:34px;height:34px;border-radius:50%;border:1.5px solid var(--line);background:var(--panel);color:var(--dim);font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;transition:all .25s}" +
".acpw-st .t{font-size:11px;color:var(--dim);letter-spacing:.3px;white-space:nowrap}" +
".acpw-st.cur .c{border-color:var(--ember);color:var(--ember);box-shadow:0 0 0 3px rgba(255,106,26,.15),0 0 18px rgba(255,106,26,.25)}" +
".acpw-st.cur .t{color:var(--ink)}" +
".acpw-st.done .c{background:rgba(255,106,26,.14);border-color:var(--ember);color:var(--ember)}" +
".acpw-conn{flex:1 1 0;height:2px;background:#4a453c;margin-top:16px;min-width:8px;border-radius:1px;transition:background .25s}" +
".acpw-conn.done{background:var(--ember)}" +
".acpw-mbar{display:none;height:4px;background:#3a362f;border-radius:2px;margin:2px 0 16px;overflow:hidden}" +
".acpw-mbar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--ember),var(--ember2));border-radius:2px;transition:width .3s ease}" +
"@media(max-width:640px){.acpw-steps{display:none}.acpw-mbar{display:block}}" +
".acpw-stephead{display:flex;gap:12px;align-items:center;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin-bottom:16px}" +
".acpw-stephead .ic{width:34px;height:34px;border-radius:9px;background:rgba(255,106,26,.13);color:var(--ember);display:flex;align-items:center;justify-content:center;flex-shrink:0}" +
".acpw-stephead h4{margin:0;font-size:14.5px}" +
".acpw-stephead h4 b{color:var(--ink)}" +
".acpw-stephead h4 span{color:var(--faint);font-weight:400}" +
".acpw-stephead p{margin:2px 0 0;font-size:12px;color:var(--dim)}" +
".acpw-step{animation:acpwIn .28s ease}" +
"@keyframes acpwIn{from{opacity:0;transform:translateX(14px)}to{opacity:1;transform:none}}" +
"@media (prefers-reduced-motion:reduce){.acpw-step{animation:none}}" +
".acpw-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}" +
"@media(max-width:560px){.acpw-grid{grid-template-columns:1fr}}" +
".acpw-opt{display:block;width:100%;text-align:left;background:var(--panel);border:1px solid var(--line);color:var(--ink);border-radius:10px;padding:12px 38px 12px 14px;font-size:14px;font-weight:600;cursor:pointer;position:relative;transition:border-color .15s,box-shadow .15s,background .15s}" +
".acpw-opt.sel::after{content:\"\u2713\";position:absolute;right:13px;top:50%;transform:translateY(-50%);color:var(--ember);font-weight:800;font-size:15px}" +
".acpw-opt:hover{border-color:rgba(255,106,26,.55)}" +
".acpw-opt.sel{border-color:var(--ember);background:rgba(255,106,26,.13);box-shadow:0 0 0 1px var(--ember),0 0 20px rgba(255,106,26,.22)}" +
".acpw-chips{display:flex;flex-wrap:wrap;gap:8px;margin:2px 0 4px}" +
".acpw-chip{background:var(--panel);border:1px solid var(--line);color:var(--dim);border-radius:999px;padding:8px 14px;font-size:13px;cursor:pointer;transition:all .15s}" +
".acpw-chip.sel{border-color:var(--gold);color:var(--ink);background:rgba(201,168,106,.13)}" +
".acpw-label{display:block;font-size:11px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:var(--faint);margin:14px 0 6px}" +
".acpw-input,.acpw-ta,.acpw-selectlike{width:100%;background:var(--panel) !important;border:1px solid var(--line) !important;color:var(--ink) !important;border-radius:10px;padding:11px 13px;font-size:16px;outline:none;box-shadow:none;transition:border-color .15s,box-shadow .15s}" +
".acpw-input::placeholder,.acpw-ta::placeholder{color:var(--faint) !important;opacity:1}" +
".acpw-input:focus,.acpw-ta:focus{border-color:var(--ember);box-shadow:0 0 0 1px var(--ember),0 0 16px rgba(255,106,26,.14)}" +
".acpw-input.bad{border-color:var(--err)}" +
".acpw-input:disabled,.acpw-selectlike[aria-disabled='true']{opacity:.7}" +
".acpw-ta{resize:vertical;min-height:80px;font-family:inherit}" +
".acpw-err{color:var(--err);font-size:12.5px;margin-top:8px}" +
".acpw-hint{color:var(--faint);font-size:12px;margin-top:6px;line-height:1.5}" +
".acpw-cal{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 12px 10px;margin-bottom:4px;max-width:380px}" +
".acpw-cal-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}" +
".acpw-cal-title{font-weight:700;font-size:14px}" +
".acpw-cal-nav{width:36px;height:36px;border-radius:8px;border:1px solid var(--line);background:none;color:var(--dim);font-size:18px;line-height:1;cursor:pointer}" +
".acpw-cal-nav:hover:enabled{border-color:var(--ember);color:var(--ember)}" +
".acpw-cal-nav:disabled{opacity:.3;cursor:default}" +
".acpw-cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}" +
".acpw-cal-dow{text-align:center;font-size:10.5px;font-weight:700;letter-spacing:.5px;color:var(--faint);text-transform:uppercase;padding:4px 0}" +
".acpw-cal-dow.offd{color:#6a6458;text-decoration:line-through}" +
".acpw-cal-day{height:38px;border-radius:8px;border:1px solid transparent;background:none;color:var(--ink);font-size:13.5px;font-weight:600;cursor:pointer;padding:0}" +
".acpw-cal-day:hover:enabled{border-color:rgba(255,106,26,.5)}" +
".acpw-cal-day.sel{background:var(--ember);color:#fff;box-shadow:0 0 14px rgba(255,106,26,.4)}" +
".acpw-cal-day:disabled{color:#57524a;cursor:default}" +
".acpw-cal-day.offd{color:#453f37;text-decoration:line-through}" +
"@media(max-width:560px){.acpw-cal{max-width:none}.acpw-cal-day{height:42px}}" +
".acpw-slots{display:grid;grid-template-columns:1fr 1fr;gap:8px}" +
"@media(max-width:560px){.acpw-slots{grid-template-columns:1fr}}" +
".acpw-date{color-scheme:dark}" +
".acpw-addr2{display:grid;grid-template-columns:1.1fr 1fr;gap:18px}" +
"@media(max-width:700px){.acpw-addr2{grid-template-columns:1fr}}" +
".acpw-addrwrap{position:relative}" +
".acpw-searchwrap{position:relative}" +
".acpw-searchwrap .sic{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--faint);pointer-events:none;display:flex}" +
".acpw-searchwrap .acpw-input{padding-left:36px;padding-right:34px}" +
".acpw-clear{position:absolute;right:6px;top:50%;transform:translateY(-50%);background:none;border:0;color:var(--faint);font-size:16px;cursor:pointer;padding:6px;line-height:1}" +
".acpw-clear:hover{color:var(--ink)}" +
".acpw-sugg{position:absolute;z-index:40;left:0;right:0;top:calc(100% + 5px);background:#26241f;border:1px solid var(--line);border-radius:11px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,.55)}" +
".acpw-sugg button{display:flex;gap:9px;align-items:flex-start;width:100%;text-align:left;background:none;border:0;border-bottom:1px solid rgba(255,255,255,.05);color:var(--ink);padding:10px 13px;font-size:13.5px;cursor:pointer}" +
".acpw-sugg button:last-child{border-bottom:0}" +
".acpw-sugg button:hover,.acpw-sugg button.hl{background:rgba(255,106,26,.12)}" +
".acpw-sugg .pi{color:var(--ember);flex-shrink:0;margin-top:1px;display:flex}" +
".acpw-sugg .sub{display:block;color:var(--faint);font-size:11.5px;margin-top:2px}" +
".acpw-vbanner{display:flex;gap:10px;align-items:center;border:1px solid rgba(95,191,122,.5);background:rgba(95,191,122,.08);border-radius:11px;padding:11px 14px;margin-bottom:4px}" +
".acpw-vbanner .vc{width:26px;height:26px;border-radius:50%;border:1.5px solid var(--ok);color:var(--ok);display:flex;align-items:center;justify-content:center;flex-shrink:0}" +
".acpw-vbanner b{display:block;font-size:13.5px;color:var(--ink)}" +
".acpw-vbanner span{font-size:12px;color:var(--dim)}" +
".acpw-vbanner.warn{border-color:rgba(232,179,76,.5);background:rgba(232,179,76,.07)}" +
".acpw-vbanner.warn .vc{border-color:#e8b34c;color:#e8b34c}" +
".acpw-cols2{display:grid;grid-template-columns:1fr 1fr;gap:0 12px}" +
".acpw-review{border:1px solid var(--line);border-radius:12px;background:var(--panel);padding:4px 16px;margin-top:2px}" +
".acpw-row{display:flex;justify-content:space-between;gap:12px;align-items:baseline;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:14px}" +
".acpw-row:last-child{border-bottom:0}" +
".acpw-row .k{color:var(--faint);font-size:11px;letter-spacing:1.2px;text-transform:uppercase;flex-shrink:0}" +
".acpw-row .v{text-align:right;font-weight:600;white-space:pre-line}" +
".acpw-row .e{background:none;border:0;color:var(--ember);font-size:12px;cursor:pointer;padding:0 0 0 8px;text-decoration:underline}" +
".acpw-nav{display:flex;gap:10px;margin-top:20px;align-items:center;justify-content:space-between}" +
".acpw-back{display:inline-flex;align-items:center;gap:7px;background:var(--panel);border:1px solid var(--line);color:var(--dim);border-radius:10px;padding:12px 20px;font-size:14px;font-weight:600;cursor:pointer}" +
".acpw-back:hover{color:var(--ink);border-color:var(--faint)}" +
".acpw-next{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:linear-gradient(90deg,var(--ember),#ff7d33);border:0;color:#fff;border-radius:10px;padding:15px 26px;min-height:50px;font-size:15px;font-weight:700;cursor:pointer;box-shadow:0 6px 18px rgba(255,106,26,.3);transition:transform .12s,box-shadow .12s;margin-left:auto}" +
".acpw-next:hover{transform:translateY(-1px);box-shadow:0 8px 22px rgba(255,106,26,.4)}" +
".acpw-next:disabled{opacity:.55;cursor:wait;transform:none}" +
".acpw-success{text-align:center;padding:30px 8px 14px}" +
".acpw-success .ic{width:56px;height:56px;border-radius:50%;background:rgba(95,191,122,.14);border:1.5px solid var(--ok);color:var(--ok);display:flex;align-items:center;justify-content:center;margin:0 auto 16px}" +
".acpw-success h3{font-family:'Inter',-apple-system,sans-serif;font-weight:800;letter-spacing:-.01em;font-size:23px;margin:0 0 8px}" +
".acpw-success p{color:var(--dim);font-size:14px;line-height:1.6;margin:0 0 6px}" +
".acpw-success a{color:var(--ember);font-weight:700;text-decoration:none}" +
".acp-book .acpw{background:none;border:0;box-shadow:none;padding:4px 0 0;border-radius:0}";

  /* ── real form access ─────────────────────────────────────────────── */

  function getRealForm() {
    var forms = document.querySelectorAll("form.contact-form");
    for (var i = 0; i < forms.length; i++) {
      if (forms[i].querySelector("[name='g315-serviceaddress']")) return forms[i];
    }
    return null;
  }

  function selectOptions(sel) {
    var out = [];
    if (!sel) return out;
    for (var i = 0; i < sel.options.length; i++) {
      var o = sel.options[i];
      if (/select an option/i.test(o.textContent)) continue;
      out.push({ value: o.value || o.textContent, label: o.textContent.trim() });
    }
    return out;
  }

  /* ── premium success card ─────────────────────────────────────────── */

  function successCard() {
    var s = el("div", "acpw");
    s.setAttribute("role", "status");
    var box = el("div", "acpw-success");
    var ic = el("div", "ic");
    ic.innerHTML = ICONS.check;
    box.appendChild(ic);
    box.appendChild(el("h3", null, "Your request is in."));
    box.appendChild(el("p", null, "Thank you — we’ve received your booking request and sent a confirmation to your email."));
    var p2 = el("p");
    p2.innerHTML = "We’ll call you shortly to confirm your appointment time. Need us right now? <a href='tel:" + PHONE_HREF + "'>Call " + PHONE_DISPLAY + "</a>";
    box.appendChild(p2);
    s.appendChild(box);
    return s;
  }

  /* ── wizard ───────────────────────────────────────────────────────── */

  function buildWizard(form) {
    var F = {
      service: form.querySelector("[name='g315-serviceneeded']"),
      date: form.querySelector("[name='g315-preferreddate']"),
      time: form.querySelector("[name='g315-preferredtime']"),
      name: form.querySelector("[name='g315-fullname']"),
      phone: form.querySelector("[name='g315-phone']"),
      email: form.querySelector("[name='g315-email']"),
      address: form.querySelector("[name='g315-serviceaddress']"),
      notes: form.querySelector("[name='g315-tellusaboutthejoboptional']"),
    };
    for (var k in F) if (!F[k] && k !== "notes") return null;

    var services = selectOptions(F.service);
    var slots = selectOptions(F.time);
    if (!services.length || !slots.length) return null;

    var state = {
      step: 0,
      service: "", issues: [], notes: "",
      date: "", time: "",
      name: "", phone: "", email: "",
      addr: { search: "", apt: "", street: "", city: "", zip: "" },
      addressVerified: false, inArea: null,
    };

    var STEPS = [
      { key: "service", label: "Service", title: "Service Needed", sub: "What can we help you with?", icon: ICONS.service },
      { key: "issue", label: "Issue", title: "What’s Going On", sub: "Optional — helps us arrive prepared.", icon: ICONS.issue },
      { key: "schedule", label: "Schedule", title: "Preferred Time", sub: "We’ll call to confirm the exact slot.", icon: ICONS.schedule },
      { key: "contact", label: "Contact", title: "Your Details", sub: "Only used to confirm this appointment.", icon: ICONS.contact },
      { key: "address", label: "Address", title: "Your Address", sub: "Please confirm your service address.", icon: ICONS.address },
      { key: "review", label: "Review", title: "Review & Send", sub: "Check everything looks right.", icon: ICONS.review },
    ];

    var root = el("div", "acpw");
    root.setAttribute("data-acpw", VERSION);

    // Bot defenses for API mode: when the wizard appeared, and a field only
    // bots fill (off-screen, not focusable, hidden from assistive tech).
    var startedAt = Date.now();
    var honeypot = document.createElement("input");
    honeypot.type = "text";
    honeypot.name = "company";
    honeypot.tabIndex = -1;
    honeypot.setAttribute("autocomplete", "off");
    honeypot.setAttribute("aria-hidden", "true");
    honeypot.style.cssText = "position:absolute;left:-9999px;width:1px;height:1px;opacity:0";
    root.appendChild(honeypot);

    // numbered progress row
    var stepsBar = el("div", "acpw-steps");
    var stepNodes = [], connNodes = [];
    STEPS.forEach(function (s, i) {
      if (i > 0) {
        var conn = el("div", "acpw-conn");
        connNodes.push(conn);
        stepsBar.appendChild(conn);
      }
      var st = el("div", "acpw-st");
      var c = el("div", "c", String(i + 1));
      st.appendChild(c);
      st.appendChild(el("div", "t", s.label));
      stepNodes.push(st);
      stepsBar.appendChild(st);
    });
    root.appendChild(stepsBar);

    var mbar = el("div", "acpw-mbar");
    var mbarFill = document.createElement("i");
    mbar.appendChild(mbarFill);
    root.appendChild(mbar);

    var stepHead = el("div", "acpw-stephead");
    stepHead.setAttribute("tabindex", "-1");
    stepHead.setAttribute("aria-live", "polite");
    root.appendChild(stepHead);

    var body = el("div");
    root.appendChild(body);

    var errBox = el("div", "acpw-err");
    errBox.setAttribute("role", "alert");
    root.appendChild(errBox);

    var nav = el("div", "acpw-nav");
    var backBtn = el("button", "acpw-back");
    backBtn.type = "button";
    backBtn.innerHTML = "&#8249;&nbsp; Back";
    var nextBtn = el("button", "acpw-next");
    nextBtn.type = "button";
    nav.appendChild(backBtn);
    nav.appendChild(nextBtn);
    root.appendChild(nav);

    function setError(msg) { errBox.textContent = msg || ""; }

    /* ── step 1: service ── */
    function renderService() {
      var wrap = el("div", "acpw-step");
      var grid = el("div", "acpw-grid");
      services.forEach(function (s) {
        var o = el("button", "acpw-opt" + (state.service === s.value ? " sel" : ""), s.label);
        o.type = "button";
        o.onclick = function () {
          state.service = s.value;
          grid.querySelectorAll(".acpw-opt").forEach(function (n) { n.classList.remove("sel"); });
          o.classList.add("sel");
          setError("");
        };
        grid.appendChild(o);
      });
      wrap.appendChild(grid);
      return wrap;
    }

    /* ── step 2: issue ── */
    function renderIssue() {
      var wrap = el("div", "acpw-step");
      wrap.appendChild(el("label", "acpw-label", "Common issues — tap any that apply"));
      var chips = el("div", "acpw-chips");
      ISSUE_CHIPS.forEach(function (c) {
        var ch = el("button", "acpw-chip" + (state.issues.indexOf(c) !== -1 ? " sel" : ""), c);
        ch.type = "button";
        ch.onclick = function () {
          var i = state.issues.indexOf(c);
          if (i === -1) state.issues.push(c); else state.issues.splice(i, 1);
          ch.classList.toggle("sel");
        };
        chips.appendChild(ch);
      });
      wrap.appendChild(chips);
      var ta = el("textarea", "acpw-ta");
      fieldLabel(wrap, "Tell us more (optional)", ta);
      ta.placeholder = "Smell, smoke, last cleaning, gas or wood burning, anything unusual…";
      ta.value = state.notes;
      ta.oninput = function () { state.notes = ta.value; };
      wrap.appendChild(ta);
      return wrap;
    }

    /* ── step 3: schedule ── */
    function nextBusinessDay() {
      var d = new Date();
      d.setDate(d.getDate() + 1);
      while (d.getDay() === 6) d.setDate(d.getDate() + 1); // skip Saturdays only
      return d;
    }
    function iso(d) {
      var m = d.getMonth() + 1, day = d.getDate();
      return d.getFullYear() + "-" + (m < 10 ? "0" : "") + m + "-" + (day < 10 ? "0" : "") + day;
    }
    function renderSchedule() {
      var wrap = el("div", "acpw-step");
      wrap.appendChild(el("label", "acpw-label", "Preferred date \— closed Saturdays"));

      var minD = nextBusinessDay();
      var maxD = new Date(); maxD.setDate(maxD.getDate() + 90);
      var minIso = iso(minD), maxIso = iso(maxD);
      var MONTHS = ["January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"];
      var DOWS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

      if (state.calY == null) {
        var base = state.date
          ? new Date(+state.date.slice(0, 4), +state.date.slice(5, 7) - 1, 1)
          : new Date(minD.getFullYear(), minD.getMonth(), 1);
        state.calY = base.getFullYear();
        state.calM = base.getMonth();
      }

      var cal = el("div", "acpw-cal");
      cal.setAttribute("role", "group");
      cal.setAttribute("aria-label", "Choose a date. Saturdays are unavailable.");
      wrap.appendChild(cal);
      var selLine = el("p", "acpw-hint");
      wrap.appendChild(selLine);

      function paintSel() {
        if (state.date) {
          var q = state.date.split("-");
          var d = new Date(+q[0], +q[1] - 1, +q[2]);
          selLine.textContent = "Selected: " +
            ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][d.getDay()] +
            ", " + MONTHS[d.getMonth()] + " " + d.getDate();
        } else {
          selLine.textContent = "Pick any day \— Saturdays are greyed out because we\’re closed.";
        }
      }

      function paintCal() {
        cal.innerHTML = "";
        var head = el("div", "acpw-cal-head");
        var prev = el("button", "acpw-cal-nav");
        prev.type = "button";
        prev.innerHTML = "&#8249;";
        prev.setAttribute("aria-label", "Previous month");
        var nxt = el("button", "acpw-cal-nav");
        nxt.type = "button";
        nxt.innerHTML = "&#8250;";
        nxt.setAttribute("aria-label", "Next month");
        var title = el("div", "acpw-cal-title", MONTHS[state.calM] + " " + state.calY);
        title.setAttribute("aria-live", "polite");
        prev.disabled = state.calY === minD.getFullYear() && state.calM === minD.getMonth();
        nxt.disabled = state.calY === maxD.getFullYear() && state.calM === maxD.getMonth();
        prev.onclick = function () {
          state.calM -= 1;
          if (state.calM < 0) { state.calM = 11; state.calY -= 1; }
          paintCal();
        };
        nxt.onclick = function () {
          state.calM += 1;
          if (state.calM > 11) { state.calM = 0; state.calY += 1; }
          paintCal();
        };
        head.appendChild(prev);
        head.appendChild(title);
        head.appendChild(nxt);
        cal.appendChild(head);

        var grid = el("div", "acpw-cal-grid");
        DOWS.forEach(function (dn, i) {
          grid.appendChild(el("div", "acpw-cal-dow" + (i === 6 ? " offd" : ""), dn));
        });
        var firstDow = new Date(state.calY, state.calM, 1).getDay();
        var daysInMonth = new Date(state.calY, state.calM + 1, 0).getDate();
        for (var pad = 0; pad < firstDow; pad++) grid.appendChild(el("div"));
        for (var day = 1; day <= daysInMonth; day++) {
          (function (day) {
            var d = new Date(state.calY, state.calM, day);
            var isoStr = iso(d);
            var cell = el("button", "acpw-cal-day", String(day));
            cell.type = "button";
            if (d.getDay() === 6) {
              cell.classList.add("offd");
              cell.disabled = true;
              cell.title = "Closed Saturdays";
            } else if (isoStr < minIso || isoStr > maxIso) {
              cell.disabled = true;
            } else {
              cell.setAttribute("aria-label",
                MONTHS[state.calM] + " " + day + ", " + state.calY);
              if (state.date === isoStr) {
                cell.classList.add("sel");
                cell.setAttribute("aria-pressed", "true");
              }
              cell.onclick = function () {
                state.date = isoStr;
                setError("");
                paintCal();
                paintSel();
              };
            }
            grid.appendChild(cell);
          })(day);
        }
        cal.appendChild(grid);
      }

      paintCal();
      paintSel();

      wrap.appendChild(el("label", "acpw-label", "Preferred time window"));
      var grid = el("div", "acpw-slots");
      slots.forEach(function (s) {
        var o = el("button", "acpw-opt" + (state.time === s.value ? " sel" : ""), s.label);
        o.type = "button";
        o.onclick = function () {
          state.time = s.value;
          grid.querySelectorAll(".acpw-opt").forEach(function (n) { n.classList.remove("sel"); });
          o.classList.add("sel");
          setError("");
        };
        grid.appendChild(o);
      });
      wrap.appendChild(grid);
      wrap.appendChild(el("p", "acpw-hint", "Preferred time noted — we’ll confirm availability when we call."));
      return wrap;
    }

    /* ── step 4: contact ── */
    var uid = 0;
    function fieldLabel(wrap, text, input) {
      var lbl = el("label", "acpw-label", text);
      input.id = "acpw-f" + (++uid);
      lbl.htmlFor = input.id;
      wrap.appendChild(lbl);
      return lbl;
    }
    function labeledInput(wrap, label, type, value, placeholder, oninput, autocomplete) {
      var inp = el("input", "acpw-input");
      fieldLabel(wrap, label, inp);
      inp.type = type;
      inp.value = value;
      if (placeholder) inp.placeholder = placeholder;
      if (autocomplete) inp.setAttribute("autocomplete", autocomplete);
      inp.oninput = function () { oninput(inp.value); inp.classList.remove("bad"); setError(""); };
      wrap.appendChild(inp);
      return inp;
    }
    function renderContact() {
      var wrap = el("div", "acpw-step");
      labeledInput(wrap, "Full name", "text", state.name, "First and last name", function (v) { state.name = v; }, "name");
      labeledInput(wrap, "Phone", "tel", state.phone, "(602) 555-0123", function (v) { state.phone = v; }, "tel");
      labeledInput(wrap, "Email", "email", state.email, "you@example.com", function (v) { state.email = v; }, "email");
      wrap.appendChild(el("p", "acpw-hint", "Never shared. We’ll email a confirmation and call to lock in the time."));
      return wrap;
    }

    /* ── step 5: address (mockup layout) ── */

    function photonSearch(q, cb) {
      var url = PHOTON + "?q=" + encodeURIComponent(q) +
        "&lat=" + GEO_BIAS.lat + "&lon=" + GEO_BIAS.lon + "&limit=6&lang=en";
      var ctl = typeof AbortController !== "undefined" ? new AbortController() : null;
      var t = setTimeout(function () { if (ctl) ctl.abort(); }, 5000);
      fetch(url, ctl ? { signal: ctl.signal } : {})
        .then(function (r) { return r.json(); })
        .then(function (d) {
          clearTimeout(t);
          var seen = {}, out = [];
          (d.features || []).forEach(function (f) {
            var p = f.properties || {};
            if (p.countrycode !== "US") return;
            if (p.state && p.state !== "Arizona" && p.state !== "AZ") return;
            var line = [p.housenumber, p.street || p.name].filter(Boolean).join(" ");
            if (!line) return;
            var city = p.city || p.district || "";
            var full = line + ", " + [city, "AZ", p.postcode].filter(Boolean).join(" ");
            if (seen[full]) return;
            seen[full] = 1;
            out.push({
              line: line, city: city, zip: p.postcode || "", county: p.county || "",
              hasNumber: !!p.housenumber, display: full,
            });
          });
          cb(null, out);
        })
        .catch(function (e) { clearTimeout(t); cb(e); });
    }

    function inServiceArea(city, county) {
      if (county === "Maricopa") return true;
      for (var i = 0; i < SERVICE_CITIES.length; i++) {
        if (city && city.toLowerCase() === SERVICE_CITIES[i].toLowerCase()) return true;
      }
      return false;
    }

    function composedAddress() {
      var a = state.addr;
      var line = a.street.trim();
      if (a.apt.trim()) line += " " + a.apt.trim();
      return line + ", " + a.city.trim() + ", AZ " + a.zip.trim();
    }

    function renderAddress() {
      var wrap = el("div", "acpw-step");
      var cols = el("div", "acpw-addr2");
      wrap.appendChild(cols);
      var left = el("div");
      var right = el("div");
      cols.appendChild(left);
      cols.appendChild(right);

      /* left: search + apt */
      left.appendChild(el("label", "acpw-label", "Search address"));
      var aw = el("div", "acpw-addrwrap");
      var sw = el("div", "acpw-searchwrap");
      var sic = el("span", "sic");
      sic.innerHTML = ICONS.search;
      sw.appendChild(sic);
      var inp = el("input", "acpw-input");
      inp.type = "text";
      inp.placeholder = "Start typing your street address…";
      inp.setAttribute("autocomplete", "off");
      inp.setAttribute("role", "combobox");
      inp.setAttribute("aria-expanded", "false");
      inp.setAttribute("aria-controls", "acpw-sugg-list");
      inp.setAttribute("aria-autocomplete", "list");
      inp.setAttribute("aria-label", "Search address");
      inp.value = state.addr.search;
      sw.appendChild(inp);
      var clr = el("button", "acpw-clear", "×");
      clr.type = "button";
      clr.setAttribute("aria-label", "Clear address");
      sw.appendChild(clr);
      aw.appendChild(sw);
      var sugg = el("div", "acpw-sugg");
      sugg.id = "acpw-sugg-list";
      sugg.setAttribute("role", "listbox");
      sugg.style.display = "none";
      aw.appendChild(sugg);
      left.appendChild(aw);

      var apt = el("input", "acpw-input");
      fieldLabel(left, "Apt, suite, unit (optional)", apt);
      apt.type = "text";
      apt.placeholder = "Ste 410";
      apt.value = state.addr.apt;
      apt.oninput = function () { state.addr.apt = apt.value; };
      left.appendChild(apt);

      /* right: banner + structured fields */
      var banner = el("div");
      right.appendChild(banner);
      var fStreet, fCity, fZip;

      function paintBanner() {
        banner.innerHTML = "";
        if (state.addressVerified) {
          var ok = state.inArea !== false;
          var b = el("div", "acpw-vbanner" + (ok ? "" : " warn"));
          var vc = el("span", "vc");
          vc.innerHTML = ICONS.check;
          b.appendChild(vc);
          var tx = el("div");
          tx.innerHTML = ok
            ? "<b>Address verified</b><span>Within our service area.</span>"
            : "<b>Address verified</b><span>A bit outside our usual area — send it and we’ll confirm by phone.</span>";
          b.appendChild(tx);
          banner.appendChild(b);
        } else {
          banner.appendChild(el("p", "acpw-hint", "Pick your address from the suggestions — or fill in the fields below."));
        }
      }

      function syncFields() {
        fStreet.value = state.addr.street;
        fCity.value = state.addr.city;
        fZip.value = state.addr.zip;
      }

      fStreet = el("input", "acpw-input");
      fieldLabel(right, "Street address", fStreet);
      fStreet.type = "text";
      fStreet.setAttribute("autocomplete", "street-address");
      fStreet.oninput = function () { state.addr.street = fStreet.value; fromPick = false; setError(""); };
      right.appendChild(fStreet);

      fCity = el("input", "acpw-input");
      fieldLabel(right, "City", fCity);
      fCity.type = "text";
      fCity.setAttribute("autocomplete", "address-level2");
      fCity.oninput = function () { state.addr.city = fCity.value; fromPick = false; setError(""); };
      right.appendChild(fCity);

      var two = el("div", "acpw-cols2");
      var stWrap = el("div");
      stWrap.appendChild(el("label", "acpw-label", "State"));
      var stBox = el("div", "acpw-selectlike", "Arizona");
      stBox.setAttribute("aria-disabled", "true");
      stWrap.appendChild(stBox);
      var zipWrap = el("div");
      fZip = el("input", "acpw-input");
      fieldLabel(zipWrap, "ZIP code", fZip);
      fZip.type = "text";
      fZip.inputMode = "numeric";
      fZip.maxLength = 5;
      fZip.setAttribute("autocomplete", "postal-code");
      fZip.oninput = function () { state.addr.zip = fZip.value.replace(/\D/g, ""); fZip.value = state.addr.zip; fromPick = false; setError(""); };
      zipWrap.appendChild(fZip);
      two.appendChild(stWrap);
      two.appendChild(zipWrap);
      right.appendChild(two);

      paintBanner();
      syncFields();

      /* autocomplete behaviour */
      var timer = null, hl = -1, current = [], seq = 0;
      function closeSugg() {
        sugg.style.display = "none";
        sugg.innerHTML = "";
        inp.setAttribute("aria-expanded", "false");
        inp.removeAttribute("aria-activedescendant");
        hl = -1;
        current = [];
      }
      var fromPick = false;
      function pick(s) {
        if (s.hasNumber) {
          fromPick = true;
          state.addr.search = s.display;
          state.addr.street = s.line;
          state.addr.city = s.city;
          state.addr.zip = s.zip;
          state.addressVerified = true;
          state.inArea = inServiceArea(s.city, s.county);
          inp.value = s.display;
          setError("");
          apt.focus();
        } else {
          state.addressVerified = false;
          inp.value = s.line + ", " + s.city;
          state.addr.search = inp.value;
          state.addr.street = s.line;
          state.addr.city = s.city;
          state.addr.zip = s.zip;
          setError("Almost — add your house number to that street.");
          inp.focus();
        }
        closeSugg();
        paintBanner();
        syncFields();
      }
      function showSugg(list) {
        current = list;
        hl = -1;                                   // a refreshed list has no highlight
        inp.removeAttribute("aria-activedescendant");
        sugg.innerHTML = "";
        if (!list.length) { closeSugg(); return; }
        list.forEach(function (s, idx) {
          var b = el("button");
          b.type = "button";
          b.id = "acpw-opt-" + idx;
          b.setAttribute("role", "option");
          b.innerHTML = "<span class='pi'>" + ICONS.pin + "</span><span>" +
            esc(s.hasNumber ? s.line : s.line + " (street)") +
            "<span class='sub'>" + esc([s.city, "AZ", s.zip].filter(Boolean).join(" ")) + "</span></span>";
          b.onclick = function () { pick(s); };
          sugg.appendChild(b);
        });
        sugg.style.display = "block";
        inp.setAttribute("aria-expanded", "true");
      }
      inp.oninput = function () {
        state.addr.search = inp.value;
        state.addressVerified = false;
        state.inArea = null;
        if (fromPick) {
          // The structured fields came from a suggestion the user is now
          // abandoning - never submit a stale picked address under new text.
          fromPick = false;
          state.addr.street = "";
          state.addr.city = "";
          state.addr.zip = "";
          syncFields();
        }
        setError("");
        paintBanner();
        clearTimeout(timer);
        seq++;                                  // invalidates any in-flight lookup
        var q = inp.value.trim();
        if (q.length < 4) { closeSugg(); return; }
        timer = setTimeout(function () {
          var my = seq;
          photonSearch(q, function (err, list) {
            if (my !== seq) return;             // a newer query superseded this one
            if (err) { closeSugg(); return; }   // degrade silently to manual fields
            showSugg(list);
          });
        }, 300);
      };
      inp.onkeydown = function (e) {
        var items = sugg.querySelectorAll("button");
        if (!items.length) return;
        if (e.key === "ArrowDown" || e.key === "ArrowUp") {
          e.preventDefault();
          hl = e.key === "ArrowDown" ? Math.min(hl + 1, items.length - 1) : Math.max(hl - 1, 0);
          items.forEach(function (n, i) { n.classList.toggle("hl", i === hl); });
          if (items[hl]) inp.setAttribute("aria-activedescendant", items[hl].id);
        } else if (e.key === "Enter") {
          e.preventDefault();
          if (hl >= 0 && current[hl]) pick(current[hl]);
        } else if (e.key === "Escape") closeSugg();
      };
      clr.onclick = function () {
        inp.value = "";
        state.addr = { search: "", apt: state.addr.apt, street: "", city: "", zip: "" };
        state.addressVerified = false;
        state.inArea = null;
        closeSugg();
        paintBanner();
        syncFields();
        inp.focus();
      };
      document.addEventListener("click", function (e) {
        if (!aw.contains(e.target)) closeSugg();
      });

      return wrap;
    }

    /* ── step 6: review ── */
    function renderReview() {
      var wrap = el("div", "acpw-step");
      var box = el("div", "acpw-review");
      var svcLabel = "";
      services.forEach(function (s) { if (s.value === state.service) svcLabel = s.label; });
      var timeLabel = "";
      slots.forEach(function (s) { if (s.value === state.time) timeLabel = s.label; });
      var noteBits = state.issues.slice();
      if (state.notes.trim()) noteBits.push(state.notes.trim());
      var rows = [
        ["Service", svcLabel, 0],
        ["When", state.date + "\n" + timeLabel, 2],
        ["Name", state.name, 3],
        ["Phone", state.phone, 3],
        ["Email", state.email, 3],
        ["Address", composedAddress(), 4],
      ];
      if (noteBits.length) rows.push(["Notes", noteBits.join(" — "), 1]);
      rows.forEach(function (r) {
        var row = el("div", "acpw-row");
        row.appendChild(el("span", "k", r[0]));
        var right = el("span", "v", r[1]);
        var edit = el("button", "e", "edit");
        edit.type = "button";
        edit.onclick = function () { go(r[2]); };
        right.appendChild(edit);
        row.appendChild(right);
        box.appendChild(row);
      });
      wrap.appendChild(box);
      wrap.appendChild(el("p", "acpw-hint", "By submitting you agree we may call, text or email you about this request."));
      return wrap;
    }

    /* ── validation ── */

    function validate(step) {
      if (step === 0 && !state.service) return "Choose the service you need.";
      if (step === 2) {
        if (!state.date) return "Pick a preferred date.";
        var p = state.date.split("-");
        var wd = new Date(+p[0], +p[1] - 1, +p[2]).getDay();
        if (wd === 6) return "We’re closed on Saturdays — pick another day.";
        if (!state.time) return "Choose a time window.";
      }
      if (step === 3) {
        if (state.name.trim().length < 2) return "Enter your name.";
        if (state.phone.replace(/\D/g, "").length < 10) return "Enter a valid phone number (10 digits).";
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(state.email.trim())) return "Enter a valid email address.";
      }
      if (step === 4) {
        var a = state.addr;
        if (!/\d+\s+\S+/.test(a.street.trim())) return "Enter the street address, including the house number.";
        if (a.city.trim().length < 3) return "Enter the city.";
        if (!/^\d{5}$/.test(a.zip.trim())) return "Enter the 5-digit ZIP code.";
      }
      return "";
    }

    /** Leaving the address step unverified: quietly try to verify what was typed. */
    function finishAddress(cb) {
      if (state.addressVerified) { cb(); return; }
      photonSearch(state.addr.street + ", " + state.addr.city + " AZ " + state.addr.zip, function (err, list) {
        if (!err && list) {
          var typedNum = (state.addr.street.match(/\d+/) || [""])[0];
          for (var i = 0; i < list.length; i++) {
            if (list[i].hasNumber && typedNum && list[i].line.indexOf(typedNum) !== -1) {
              state.addr.street = list[i].line;
              state.addr.city = list[i].city || state.addr.city;
              state.addr.zip = list[i].zip || state.addr.zip;
              state.addressVerified = true;
              state.inArea = inServiceArea(list[i].city, list[i].county);
              break;
            }
          }
        }
        cb(); // structured fields already validated — proceed either way
      });
    }

    /* ── submit into the real Jetpack form ── */

    /* ── mirror the lead into the estimator CRM ────────────────────────────
     * Fire-and-forget on purpose: the booking itself already succeeded via
     * Jetpack, so a CRM outage must never surface an error to the customer or
     * block their confirmation. keepalive lets it finish even as the page
     * changes underneath it.
     */
    var CRM_ENDPOINT = "https://acp-platform-green.vercel.app/api/leads";

    function sendToCrm() {
      try {
        var notes = state.notes.trim();
        var payload = {
          name: state.name.trim(),
          phone: state.phone.trim(),
          email: state.email.trim(),
          address: composedAddress(),
          service: state.service,
          date: state.date,
          time: state.time,
          issues: state.issues.join(", "),
          notes: notes
        };
        fetch(CRM_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          keepalive: true,
          mode: "cors"
        })["catch"](function () { /* customer already booked; nothing to show */ });
      } catch (e) { /* never let CRM mirroring break the booking */ }
    }

    /* ── API mode (static hosting, no WordPress) ─────────────────────────
     * Opt-in via window.ACP_BOOKING_ENDPOINT. The server validates, files the
     * CRM lead with its secret and sends both emails, so the wizard does NOT
     * also call sendToCrm() here — that would append the notes twice.
     * The live WordPress page never sets the global and keeps the Jetpack path.
     */
    var ATTR_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "gclid", "fbclid"];

    /** First-touch attribution stored by acp-attr.js on the visitor's landing page,
     *  falling back to whatever is on the current URL. */
    function storedAttr() {
      try { return JSON.parse(sessionStorage.getItem("acp_attr") || "{}") || {}; } catch (e) { return {}; }
    }

    function utmParams() {
      var out = {}, stored = storedAttr();
      try {
        var q = new URLSearchParams(location.search);
        ATTR_KEYS.forEach(function (k) {
          var v = q.get(k) || stored[k];
          if (v) out[k] = v;
        });
      } catch (e) {
        ATTR_KEYS.forEach(function (k) { if (stored[k]) out[k] = stored[k]; });
      }
      return out;
    }

    var sending = false;

    function submitViaApi() {
      if (sending) return;              // one intentional submit = one POST
      sending = true;
      nextBtn.disabled = true;
      backBtn.disabled = true;
      nextBtn.textContent = "Sending…";
      var payload = {
        service: state.service,
        issues: state.issues,
        notes: state.notes.trim(),
        date: state.date,
        time: state.time,
        name: state.name.trim(),
        phone: state.phone.trim(),
        email: state.email.trim(),
        address: {
          street: state.addr.street.trim(),
          apt: state.addr.apt.trim(),
          city: state.addr.city.trim(),
          zip: state.addr.zip.trim(),
          verified: state.addressVerified,
          inArea: state.inArea
        },
        page: location.href,
        landing_page: storedAttr().landing_page || location.href,
        submitted_at: new Date().toISOString(),
        referrer: document.referrer,
        utm: utmParams(),
        startedAt: startedAt,
        company: honeypot.value
      };
      function fail(msg) {
        sending = false;
        nextBtn.disabled = false;
        backBtn.disabled = false;
        nextBtn.textContent = "Request Free Estimate";
        setError(msg || ("Something went wrong sending your request — please try again or call us at " + PHONE_DISPLAY + "."));
      }
      fetch(window.ACP_BOOKING_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).then(function (r) {
        return r.json()["catch"](function () { return { ok: false }; }).then(function (d) {
          if (r.ok && d.ok) {
            if (!root.parentNode) return;
            var card = successCard();
            root.parentNode.replaceChild(card, root);
            card.scrollIntoView({ behavior: "smooth", block: "center" });
          } else {
            fail(d.error);
          }
        });
      })["catch"](function () { fail(); });
    }

    function submitReal() {
      if (window.ACP_BOOKING_ENDPOINT) { submitViaApi(); return; }
      nextBtn.disabled = true;
      nextBtn.textContent = "Sending…";
      var notes = state.issues.join(", ");
      if (state.notes.trim()) notes += (notes ? " — " : "") + state.notes.trim();

      setField(F.service, state.service);
      setField(F.date, state.date);
      setField(F.time, state.time);
      setField(F.name, state.name.trim());
      setField(F.phone, state.phone.trim());
      setField(F.email, state.email.trim());
      setField(F.address, composedAddress());
      if (F.notes) setField(F.notes, notes);

      var container = form.parentNode;
      if (pendingMo) { pendingMo.disconnect(); pendingMo = null; }
      if (pendingTimer) { clearTimeout(pendingTimer); pendingTimer = null; }
      var done = false;
      function settle() {
        done = true;
        if (pendingMo) { pendingMo.disconnect(); pendingMo = null; }
        if (pendingTimer) { clearTimeout(pendingTimer); pendingTimer = null; }
      }
      function onSuccess() {
        if (done) return;
        settle();
        sendToCrm();
        // The wizard replaces Jetpack's own confirmation, so hide it.
        var jm = container.querySelector(".contact-form-submission");
        if (jm) jm.style.display = "none";
        if (!root.parentNode) return;
        var card = successCard();
        root.parentNode.replaceChild(card, root);
        card.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      function onFailure(msg) {
        if (done) return;
        settle();
        nextBtn.disabled = false;
        nextBtn.textContent = "Request Free Estimate";
        setError(msg);
      }
      var mo = new MutationObserver(function () {
        if (!document.body.contains(form)) { onSuccess(); return; }
        // Jetpack pre-renders the confirmation div hidden and flips a class on
        // it when the AJAX submit truly succeeds - match the class, never the div.
        var ok = container.querySelector(".contact-form-submission.submission-success");
        if (ok) { onSuccess(); return; }
        var errNode = form.querySelector(".contact-form__error");
        // Jetpack pre-renders generic error text with display:none — only a
        // VISIBLE error is a real failure.
        if (errNode && errNode.offsetHeight > 0 && errNode.textContent.replace(/\s+/g, "")) {
          onFailure("The form reported: " + errNode.textContent.trim() + " — or call us at " + PHONE_DISPLAY + ".");
        }
      });
      pendingMo = mo;
      mo.observe(container, { childList: true, subtree: true, attributes: true, attributeFilter: ["class"] });

      var submitBtn = form.querySelector("button[type='submit']");
      if (form.requestSubmit) form.requestSubmit(submitBtn || undefined);
      else form.submit();

      pendingTimer = setTimeout(function () {
        if (done || !document.body.contains(root)) return;
        nextBtn.disabled = false;
        nextBtn.textContent = "Request Free Estimate";
        setError("Taking longer than expected — if this doesn’t go through, call us at " + PHONE_DISPLAY + ".");
      }, 15000);
    }

    /* ── navigation ── */

    var pendingMo = null;
    var pendingTimer = null;
    var booted = false;
    var renderers = [renderService, renderIssue, renderSchedule, renderContact, renderAddress, renderReview];

    function go(step) {
      state.step = step;
      setError("");
      body.innerHTML = "";
      body.appendChild(renderers[step]());
      stepNodes.forEach(function (n, i) {
        n.classList.toggle("cur", i === step);
        n.classList.toggle("done", i < step);
        n.querySelector(".c").textContent = i < step ? "\u2713" : String(i + 1);
        if (i === step) n.setAttribute("aria-current", "step");
        else n.removeAttribute("aria-current");
      });
      mbarFill.style.width = Math.round(((step + 1) / STEPS.length) * 100) + "%";
      connNodes.forEach(function (c, i) { c.classList.toggle("done", i < step); });
      var s = STEPS[step];
      stepHead.innerHTML = "<span class='ic'>" + s.icon + "</span><div><h4><b>Step " + (step + 1) + " of " + STEPS.length +
        "</b> <span>· " + esc(s.title) + "</span></h4><p>" + esc(s.sub) + "</p></div>";
      backBtn.style.visibility = step === 0 ? "hidden" : "visible";
      nextBtn.innerHTML = step === STEPS.length - 1
        ? "Request Free Estimate"
        : "Next: " + esc(STEPS[step + 1].label) + " &nbsp;&#8250;";
      nextBtn.disabled = false;
      backBtn.disabled = false;
      if (booted) stepHead.focus({ preventScroll: false });
      booted = true;
    }

    backBtn.onclick = function () { if (state.step > 0) go(state.step - 1); };
    nextBtn.onclick = function () {
      var msg = validate(state.step);
      if (msg) { setError(msg); return; }
      if (state.step === 4 && !state.addressVerified) {
        nextBtn.disabled = true;
        backBtn.disabled = true;
        finishAddress(function () {
          nextBtn.disabled = false;
          backBtn.disabled = false;
          if (state.step !== 4) return; // user navigated away while we looked it up
          go(5);
        });
        return;
      }
      if (state.step === STEPS.length - 1) { submitReal(); return; }
      go(state.step + 1);
    };

    root.addEventListener("keydown", function (e) {
      if (e.key !== "Enter") return;
      var t = e.target;
      if (t.tagName === "TEXTAREA") return;
      if (t.tagName === "INPUT" && t.getAttribute("role") === "combobox") return;
      if (t.tagName === "INPUT") { e.preventDefault(); nextBtn.click(); }
    });

    go(0);
    return root;
  }

  /* ── boot ─────────────────────────────────────────────────────────── */

  function boot() {
    try {
      var style = document.createElement("style");
      style.textContent = CSS;
      document.head.appendChild(style);

      var mount = document.getElementById("acp-wizard-mount");

      // Returning from a classic (non-AJAX) submit: premium success card.
      if (/contact-form-sent/.test(location.search)) {
        var doneMsg = document.querySelector(".contact-form-submission");
        var card = successCard();
        if (mount) {
          mount.appendChild(card);
          if (doneMsg) doneMsg.style.display = "none";
        } else if (doneMsg) {
          doneMsg.parentNode.insertBefore(card, doneMsg);
          doneMsg.style.display = "none";
        }
        return;
      }

      var form = getRealForm();
      if (!form) return;

      var wizard = buildWizard(form);
      if (!wizard) return;

      // Park the real form off-screen but focusable, so its native validation
      // and Jetpack's own submit flow keep working when the wizard drives it.
      form.style.position = "absolute";
      form.style.left = "-9999px";
      form.style.width = "1px";
      form.style.height = "1px";
      form.style.overflow = "hidden";
      form.setAttribute("aria-hidden", "true");
      // aria-hidden alone leaves the parked fields keyboard-focusable.
      form.querySelectorAll("input, select, textarea, button, a[href]").forEach(function (n) {
        n.setAttribute("tabindex", "-1");
      });

      if (mount) {
        mount.appendChild(wizard);
      } else {
        var slot = document.createElement("div");
        form.parentNode.insertBefore(slot, form);
        slot.appendChild(wizard);
      }
    } catch (e) {
      try {
        var f = getRealForm();
        if (f) {
          f.style.position = "";
          f.style.left = "";
          f.style.width = "";
          f.style.height = "";
          f.style.overflow = "";
          f.removeAttribute("aria-hidden");
          f.querySelectorAll("[tabindex='-1']").forEach(function (n) { n.removeAttribute("tabindex"); });
        }
        var w = document.querySelector("[data-acpw]");
        if (w) w.style.display = "none";
      } catch (e2) { /* nothing more we can do */ }
      if (window.console) console.error("[acp-wizard]", e);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
