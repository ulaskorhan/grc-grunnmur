/*
  report.js: fills the report (v6, /rapport/) on the GitHub Pages version.

  Flask fills the report from the database. On GitHub Pages it is built with
  empty data, and this script fills each line from the visitor's browser instead.
  It uses storeOf() and loadData() from static-mode.js, which is loaded first,
  so every section reads the same storage key as the page where it was saved.
  Rings, bars and counts are already updated by static-mode.js (data-ids),
  and the risk register by static-risks.js.
*/

const LABELS = JSON.parse(document.getElementById("report-labels").textContent);

// Every report line has data-row="<id>": set its status pill and notes.
document.querySelectorAll("[data-row]").forEach(function (line) {
  const store = storeOf(line);
  const saved = loadData(store.key)[line.dataset.row] || {};
  const status = saved.status || store.fallback;

  const pill = line.querySelector('[data-show="status"]');
  pill.className = "status status-" + status;
  pill.textContent = LABELS[status];

  const notes = line.querySelector('[data-show="notes"]');
  notes.textContent = saved.notes || "";          // textContent: notes are shown as text, never run
  notes.hidden = !saved.notes;

  // E.g. SoA controls that are not assessed yet are left out of the report
  line.hidden = line.dataset.hideIf === status;
});

// "Ingen kontroller er vurdert ennå" only when a list has no visible lines
document.querySelectorAll("[data-rows]").forEach(function (list) {
  const empty = list.parentElement.querySelector("[data-empty]");
  if (empty) empty.hidden = list.querySelector("[data-row]:not([hidden])") !== null;
});

// The date the report is looked at (the static page was built on another day), as dd.mm.yyyy
const today = new Date();
const twoDigits = function (n) { return String(n).padStart(2, "0"); };
document.querySelector("[data-today]").textContent =
  twoDigits(today.getDate()) + "." + twoDigits(today.getMonth() + 1) + "." + today.getFullYear();
