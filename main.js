/* Optionnel — le tracking est géré par GTM (déclencheurs natifs Form Submit et clic tel:). */
(function () {
  "use strict";
  var y = document.getElementById("year"); if (y) y.textContent = new Date().getFullYear();
  /* Comparateur avant / après : <div data-ba style="--pos:50%"><img avant><img après><input type=range class=ba-range></div> */
  document.querySelectorAll("[data-ba]").forEach(function (ba) {
    var r = ba.querySelector(".ba-range"); if (!r) return;
    var set = function () { ba.style.setProperty("--pos", r.value + "%"); }; set(); r.addEventListener("input", set);
  });
  /* Bouton d'envoi : état "Envoi…" après validation HTML5 (aucun effet sur GTM) */
  document.querySelectorAll("form").forEach(function (f) {
    f.addEventListener("submit", function () {
      if (!f.checkValidity()) return;
      var b = f.querySelector("button[type=submit]"); if (b) { b.disabled = true; b.textContent = b.getAttribute("data-sending") || "Envoi…"; }
    });
  });
})();
