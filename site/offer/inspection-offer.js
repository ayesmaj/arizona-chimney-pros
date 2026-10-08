/* Arizona Chimney Pros — $99 inspection offer: runtime behaviour.
 * Everything visible is server-rendered by tools/apply_inspection_offer.py;
 * this file only adds the floating card, the fee-details modal, entrance
 * animations and analytics events. */
(function () {
  "use strict";
  var OFFER = window.ACP_OFFER || {};
  var doc = document;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── analytics (gtag already on every page) — never any customer data ── */
  function device() {
    var w = window.innerWidth;
    return w < 768 ? "mobile" : w < 1024 ? "tablet" : "desktop";
  }
  function track(name, placement, serviceType) {
    try {
      if (typeof window.gtag !== "function") return;
      window.gtag("event", name, {
        pagePath: location.pathname,
        serviceType: serviceType || doc.body.getAttribute("data-offer-service") || "general",
        placement: placement || "",
        deviceCategory: device()
      });
    } catch (e) { /* analytics must never break the page */ }
  }
  window.ACP_OFFER_TRACK = track;

  doc.addEventListener("click", function (e) {
    var t = e.target.closest && e.target.closest("[data-offer-event]");
    if (!t) return;
    track(t.getAttribute("data-offer-event"), t.getAttribute("data-offer-placement") || "");
  });

  /* ── one-time entrance animations + offer_view ── */
  var seen = {};
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("is-in");
        var pl = en.target.getAttribute("data-offer-view");
        if (pl && !seen[pl]) { seen[pl] = true; track("inspection_offer_view", pl); }
        io.unobserve(en.target);
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -8% 0px" });
    doc.querySelectorAll(".acp-offer-anim, [data-offer-view]").forEach(function (n) { io.observe(n); });
  } else {
    doc.querySelectorAll(".acp-offer-anim").forEach(function (n) { n.classList.add("is-in"); });
  }

  /* ── fee-details modal (accessible: focus trap, Esc, restore focus) ── */
  var modal = doc.getElementById("acp-offer-modal");
  var lastFocus = null;
  function focusables() {
    return modal ? Array.prototype.slice.call(modal.querySelectorAll(
      "a[href],button:not([disabled]),[tabindex]:not([tabindex='-1'])")) : [];
  }
  function openModal(placement) {
    if (!modal) return;
    lastFocus = doc.activeElement;
    modal.hidden = false;
    doc.body.classList.add("acp-offer-modal-open");
    var f = focusables();
    (f[0] || modal).focus();
    track("inspection_credit_details_open", placement || "");
  }
  function closeModal() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    doc.body.classList.remove("acp-offer-modal-open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  window.ACP_OFFER_MODAL = { open: openModal, close: closeModal };
  doc.addEventListener("click", function (e) {
    var o = e.target.closest && e.target.closest("[data-offer-modal-open]");
    if (o) { e.preventDefault(); openModal(o.getAttribute("data-offer-placement") || ""); return; }
    if (e.target.closest && e.target.closest("[data-offer-modal-close]")) closeModal();
  });
  doc.addEventListener("keydown", function (e) {
    if (!modal || modal.hidden) return;
    if (e.key === "Escape") { closeModal(); return; }
    if (e.key !== "Tab") return;
    var f = focusables();
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  /* ── desktop floating card: after the hero, dismissable for the session ── */
  var fl = doc.getElementById("acp-offer-float");
  if (fl) {
    var KEY = "acp_offer_float_dismissed";
    var dismissed = false;
    try { dismissed = sessionStorage.getItem(KEY) === "1"; } catch (e) { /* storage off */ }
    var shown = false;
    function maybeShow() {
      if (dismissed || shown) return;
      if (window.innerWidth < 1024 || window.scrollY < 640) return;
      shown = true;
      fl.hidden = false;
      requestAnimationFrame(function () { fl.classList.add("is-in"); });
    }
    window.addEventListener("scroll", maybeShow, { passive: true });
    fl.addEventListener("click", function (e) {
      if (e.target.closest("[data-offer-float-close]")) {
        dismissed = true;
        fl.hidden = true;
        try { sessionStorage.setItem(KEY, "1"); } catch (e2) { /* ignore */ }
      }
    });
  }

  /* ── mobile dock: step aside while the keyboard is open ── */
  var dock = doc.getElementById("acp-offer-dock");
  if (dock) {
    doc.addEventListener("focusin", function (e) {
      if (e.target.matches && e.target.matches("input,textarea,select")) dock.classList.add("is-hidden");
    });
    doc.addEventListener("focusout", function () {
      setTimeout(function () {
        var a = doc.activeElement;
        if (!(a && a.matches && a.matches("input,textarea,select"))) dock.classList.remove("is-hidden");
      }, 50);
    });
  }

  /* ── phone clicks anywhere count as inspection_phone_click ── */
  doc.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href^='tel:']");
    if (a && !a.hasAttribute("data-offer-event")) track("inspection_phone_click", "page");
  });

  if (location.pathname.replace(/\/+$/, "") === (OFFER.learnUrl || "/inspection").replace(/\/+$/, "")) {
    track("inspection_page_view", "page");
  }
  if (reduce) doc.documentElement.classList.add("acp-offer-reduce");
})();
