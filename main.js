/* Le suivi des conversions est géré par GTM (déclencheurs natifs Form Submit et clic tel:).
   Ce fichier : bouton d'envoi, et origine des visites
   (Google Ads, SEO, accès direct…) transmise au formulaire pour le CRM. */
(function () {
  "use strict";
  /* Bouton d'envoi : état "Envoi…" après validation HTML5 (aucun effet sur GTM) */
  document.querySelectorAll("form").forEach(function (f) {
    f.addEventListener("submit", function () {
      if (!f.checkValidity()) return;
      var b = f.querySelector("button[type=submit]"); if (b) { b.disabled = true; b.textContent = b.getAttribute("data-sending") || "Envoi…"; }
    });
  });

  /* Consentement aux cookies (Mode Consentement v2). Valeur par défaut posée dans le <head>, avant GTM. */
  var CKEY = "fdt_consent", CTTL = 182 * 864e5;
  var consent = null;
  try { consent = JSON.parse(localStorage.getItem(CKEY) || "null"); } catch (e) {}
  if (consent && (!consent.ts || Date.now() - consent.ts > CTTL)) consent = null;
  var granted = !!(consent && consent.v === "granted");
  var banner = document.getElementById("cookie-banner");
  function showBanner(on) { if (banner) banner.hidden = !on; }
  function setConsent(v) {
    try { localStorage.setItem(CKEY, JSON.stringify({ v: v, ts: Date.now() })); } catch (e) {}
    var g = v === "granted" ? "granted" : "denied";
    if (typeof window.gtag === "function") {
      window.gtag("consent", "update", { ad_storage: g, ad_user_data: g, ad_personalization: g, analytics_storage: g });
    }
    (window.dataLayer = window.dataLayer || []).push({ event: "consent_update", consent_state: g });
    granted = g === "granted";
    if (granted) saveOrigin(); else { forgetOrigin(); clearAdCookies(); st = cur; fillForms(); }
    showBanner(false);
  }
  /* Retrait du consentement : suppression des cookies Google Ads déjà déposés */
  function clearAdCookies() {
    var host = location.hostname.replace(/^www\./, "");
    document.cookie.split(";").forEach(function (c) {
      var n = c.split("=")[0].trim();
      if (!/^(_gcl_|_gac_|_ga|FPGCL)/.test(n)) return;
      ["", "; domain=" + host, "; domain=." + host, "; domain=" + location.hostname].forEach(function (d) {
        document.cookie = n + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/" + d;
      });
    });
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest("[data-consent],[data-consent-open]") : null;
    if (!t) return;
    if (t.hasAttribute("data-consent-open")) { e.preventDefault(); showBanner(true); return; }
    setConsent(t.getAttribute("data-consent"));
  });
  if (!consent) showBanner(true);

  /* Origine de la visite : modèle « dernier clic non direct », mémorisé 90 jours (fenêtre de conversion Google Ads),
     uniquement si le visiteur a accepté les cookies. Sans accord, seule la page en cours est prise en compte.
     - identifiant de clic (gclid, gbraid, wbraid, fbclid, msclkid) ou paramètres utm → nouvelle origine ;
     - arrivée depuis un autre site (moteur de recherche, lien) → nouvelle origine ;
     - navigation interne ou accès direct → on garde l'origine mémorisée. */
  var KEY = "fdt_origine", TTL = 90 * 864e5;
  var PARAMS = ["gclid", "gbraid", "wbraid", "fbclid", "msclkid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"];
  var FIELDS = PARAMS.concat(["referrer", "landing_page"]);
  var q, cur = {}, has = false, ref = "", st = null;
  try { q = new URLSearchParams(location.search); } catch (e) { q = null; }
  if (q) PARAMS.forEach(function (k) { var v = q.get(k); if (v) { cur[k] = v.slice(0, 300); has = true; } });
  try {
    if (document.referrer) {
      var h = new URL(document.referrer).hostname;
      if (h && h !== location.hostname && h.indexOf("laferblanteriedethomas") === -1) ref = document.referrer.slice(0, 300);
    }
  } catch (e) {}
  cur.referrer = ref; cur.landing_page = location.pathname; cur.ts = Date.now();
  if (granted) {
    try { st = JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { st = null; }
    if (st && (!st.ts || Date.now() - st.ts > TTL)) st = null;
  }
  if (has || ref || !st) st = cur;
  function saveOrigin() { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
  function forgetOrigin() { try { localStorage.removeItem(KEY); } catch (e) {} }
  if (granted) saveOrigin(); else forgetOrigin();
  function fillForms() {
    var o = st;
    /* Repli : identifiant de clic laissé par le Conversion Linker (cookie _gcl_aw, posé seulement avec accord), pour un accès direct */
    if (granted && !o.gclid && !o.gbraid && !o.wbraid && !o.referrer && !o.utm_source) {
      var m = document.cookie.match(/(?:^|; )_gcl_aw=([^;]+)/);
      if (m) { var parts = decodeURIComponent(m[1]).split("."); if (parts.length >= 3) o.gclid = parts.slice(2).join("."); }
    }
    document.querySelectorAll("form").forEach(function (f) {
      FIELDS.forEach(function (k) {
        var i = f.querySelector('input[name="' + k + '"]');
        if (i) i.value = o[k] || "";
      });
    });
  }
  fillForms();
  document.addEventListener("submit", fillForms, true);

  /* Passage d'URL (équivalent du url_passthrough de Google) : sans accord, aucun cookie, donc l'identifiant de clic
     et les utm présents dans l'adresse suivent dans les liens internes. Google Ads et le formulaire les relisent sur la page suivante. */
  function passthrough(e) {
    if (granted || !has) return;
    var a = e.target.closest ? e.target.closest("a[href]") : null;
    if (!a || a.target === "_blank") return;
    var u;
    try { u = new URL(a.getAttribute("href"), location.href); } catch (err) { return; }
    if (u.hostname !== location.hostname || !/^https?:$/.test(u.protocol)) return;
    if (u.pathname === location.pathname && u.hash) return;
    PARAMS.forEach(function (k) { if (cur[k] && !u.searchParams.get(k)) u.searchParams.set(k, cur[k]); });
    a.href = u.toString();
  }
  document.addEventListener("mousedown", passthrough, true);
  document.addEventListener("touchstart", passthrough, { capture: true, passive: true });
  document.addEventListener("keydown", function (e) { if (e.key === "Enter") passthrough(e); }, true);
})();
