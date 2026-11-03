/*
  risk-tools.js: small helpers for the risk pages (v5), used in both versions
  (Flask and GitHub Pages). Without JavaScript the pages still work, they just
  show every risk and the suggestions for the principle that was saved.

    1. Heat maps (/risikoer): click a cell to show only the risks in it.
    2. Risk form (/risikoer/ny): show NSM's measures for the chosen principle.
*/

// ---------- 1. Heat map filter ----------

function setupHeatMaps() {
  const list = document.getElementById("risk-list");
  const bar = document.getElementById("heat-filter");
  if (!list || !bar) return;
  const MAP_NAMES = { before: "før tiltak", after: "etter tiltak" };

  // Show every row again and un-press every cell.
  function clearFilter() {
    list.querySelectorAll(".risk").forEach(function (row) { row.hidden = false; });
    document.querySelectorAll(".cell").forEach(function (cell) { cell.setAttribute("aria-pressed", "false"); });
    bar.hidden = true;
  }

  // Event delegation: one listener for all 50 cells.
  document.querySelector(".heat-maps").addEventListener("click", function (event) {
    const cell = event.target.closest(".cell");
    if (!cell) return;
    if (cell.getAttribute("aria-pressed") === "true") {   // a second click undoes the filter
      clearFilter();
      return;
    }
    clearFilter();
    cell.setAttribute("aria-pressed", "true");

    // Each row has data-before="3-4" and data-after="2-4" (see _risk_row.html)
    const map = cell.dataset.map;
    list.querySelectorAll(".risk").forEach(function (row) {
      row.hidden = row.dataset[map] !== cell.dataset.cell;
    });
    const [likelihood, impact] = cell.dataset.cell.split("-");
    document.getElementById("heat-filter-text").textContent =
      "Viser risikoer med sannsynlighet " + likelihood + " og konsekvens " + impact +
      " (" + MAP_NAMES[map] + ").";
    bar.hidden = false;
  });

  document.getElementById("heat-filter-clear").addEventListener("click", clearFilter);
}

// ---------- 2. Suggestions on the risk form ----------

function setupSuggestions() {
  const select = document.querySelector('select[name="principle_id"]');
  if (!select) return;

  // Every block has data-principle="2.6"; the empty one ("") is the "choose a principle" text.
  function show() {
    document.querySelectorAll(".suggestions [data-principle]").forEach(function (block) {
      block.hidden = block.dataset.principle !== select.value;
    });
  }
  select.addEventListener("change", show);
  show();   // on GitHub Pages, static-risks.js may already have filled in a saved principle
}

setupHeatMaps();
setupSuggestions();
