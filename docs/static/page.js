/*
  page.js: small helpers every page needs, in both versions. Loaded before the other scripts.

  These used to be inline (onclick="...", onsubmit="...", a <script> block in base.html).
  The content security policy in base.html now only allows scripts from the site's own
  files, so inline code would be blocked. Moving it here keeps the policy strict.
*/

(function () {
  // A link like iso27002#k8.8 or kategori/beskytte#p2.3 points into closed <details>:
  // open the target and every <details> around it, so it is visible.
  // Some browsers do this on their own; this makes it work everywhere.
  function openFromHash() {
    const target = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (!target) return;
    for (let el = target; el; el = el.parentElement && el.parentElement.closest("details")) {
      if (el.tagName === "DETAILS") el.open = true;
    }
    target.scrollIntoView();
  }
  openFromHash();
  window.addEventListener("hashchange", openFromHash);

  // Forms with data-confirm="Slette ...?" ask first. Registered before the page's own
  // scripts, so they can check event.defaultPrevented and stop if the answer was no.
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  // The print button in the report
  document.querySelectorAll("[data-print]").forEach(function (button) {
    button.addEventListener("click", function () { window.print(); });
  });
})();
