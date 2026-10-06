/**
 * First-touch attribution. Runs on every page: the first page of a visit stores
 * its URL and any campaign parameters, so a lead submitted later on /contact/
 * still reports where the visitor actually came from.
 */
(function () {
  try {
    var KEY = "acp_attr";
    if (sessionStorage.getItem(KEY)) return;          // first touch wins
    var q = new URLSearchParams(location.search);
    var attr = { landing_page: location.href, referrer: document.referrer || "" };
    ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "gclid", "fbclid"]
      .forEach(function (k) { if (q.get(k)) attr[k] = q.get(k); });
    sessionStorage.setItem(KEY, JSON.stringify(attr));
  } catch (e) { /* private mode or storage disabled: attribution is best-effort */ }
})();
