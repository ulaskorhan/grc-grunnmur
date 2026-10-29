/*
  static-risks.js: the risk register (v2) on the GitHub Pages version.

  Like static-mode.js, everything is saved in the visitor's own browser
  (localStorage) and nothing is sent to a server. This file handles two pages:
    - the list   (/risikoer/):    builds one row per saved risk
    - the form   (/risikoer/ny/): creates a risk, or edits one with ?id=...

  Saved data looks like this (a list of risks):
    [ { "id": "lq3k9x2a", "title": "...", "likelihood": 3, "impact": 4, ... } ]
*/

const RISKS_KEY = "grunnmur-risks";

// ---------- Storage ----------

function loadRisks() {
  try {
    return JSON.parse(localStorage.getItem(RISKS_KEY)) || [];
  } catch (error) {
    return [];
  }
}

function saveRisks(list) {
  try {
    localStorage.setItem(RISKS_KEY, JSON.stringify(list));
    return true;
  } catch (error) {
    alert("Kunne ikke lagre. Nettleseren blokkerer lokal lagring.");
    return false;
  }
}

// A short unique id, e.g. "lq3k9x2a7f": time + a random part.
function newId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

// ---------- The list page ----------

// The level rules, sent by Python (risks.config_for_browser) inside the page.
function readConfig() {
  const element = document.getElementById("risk-config");
  return element ? JSON.parse(element.textContent) : null;
}

// Same calculation as risks.enrich() in Python.
function enrich(risk, config) {
  const score = risk.likelihood * risk.impact;
  // config.levels is highest first, e.g. ["kritisk", "Kritisk", 20]
  const level = config.levels.find(function (lvl) { return score >= lvl[2]; });
  const today = new Date().toISOString().slice(0, 10);   // "YYYY-MM-DD"
  return Object.assign({}, risk, {
    score: score,
    level: level[0],
    level_label: level[1],
    treatment_label: config.treatments[risk.treatment],
    status_label: config.statuses[risk.status],
    // Dates as "YYYY-MM-DD" text can be compared directly.
    overdue: Boolean(risk.review_date && risk.status !== "lukket" && risk.review_date < today),
  });
}

// Same order as risks.sort_key(): closed last, then highest score, then title.
function compareRisks(a, b) {
  const closedA = a.status === "lukket" ? 1 : 0;
  const closedB = b.status === "lukket" ? 1 : 0;
  if (closedA !== closedB) return closedA - closedB;
  if (a.score !== b.score) return b.score - a.score;
  return a.title.toLowerCase().localeCompare(b.title.toLowerCase(), "no");
}

// Copy the empty row from <template> and fill in one risk.
function buildRow(risk, editUrl) {
  const template = document.getElementById("risk-row-template");
  const row = template.content.firstElementChild.cloneNode(true);

  row.className = "risk level-" + risk.level + (risk.status === "lukket" ? " is-closed" : "");
  // The form page is a folder on GitHub Pages (risikoer/ny/), so the link ends with "/".
  const formUrl = editUrl.endsWith("/") ? editUrl : editUrl + "/";
  row.querySelector("a").href = formUrl + "?id=" + encodeURIComponent(risk.id);

  // textContent (not innerHTML) so a title like "<script>" is shown as text, never run.
  row.querySelector('[data-field="score"]').textContent = risk.score;
  row.querySelector('[data-field="title"]').textContent = risk.title;
  row.querySelector('[data-field="level_label"]').textContent = risk.level_label;
  row.querySelector('[data-field="treatment_label"]').textContent = risk.treatment_label;
  row.querySelector('[data-field="status_label"]').textContent = risk.status_label;

  const principle = row.querySelector('[data-field="principle"]');
  principle.textContent = "NSM " + risk.principle_id;
  principle.hidden = !risk.principle_id;
  row.querySelector('[data-field="gdpr"]').hidden = !risk.gdpr;
  row.querySelector('[data-field="overdue"]').hidden = !risk.overdue;
  return row;
}

function renderList() {
  const list = document.getElementById("risk-list");
  const config = readConfig();
  if (!list || !config) return;

  const items = loadRisks().map(function (risk) { return enrich(risk, config); });
  items.sort(compareRisks);

  list.replaceChildren();   // remove old rows
  items.forEach(function (risk) {
    list.appendChild(buildRow(risk, list.dataset.editUrl));
  });

  // Counts per level, and the "no risks yet" message
  document.querySelectorAll("[data-level-count]").forEach(function (box) {
    const key = box.dataset.levelCount;
    box.textContent = items.filter(function (risk) { return risk.level === key; }).length;
  });
  document.getElementById("empty-state").hidden = items.length > 0;
}

// ---------- The form page ----------

function setupForm() {
  const form = document.getElementById("risk-form");
  if (!form) return;

  const editId = new URLSearchParams(location.search).get("id");
  const risks = loadRisks();
  const existing = risks.find(function (risk) { return risk.id === editId; });

  // Editing: fill the form with the saved values and show the delete button.
  if (existing) {
    document.getElementById("form-heading").textContent = "Rediger risiko";
    document.title = "Rediger risiko · Grunnmur";
    ["title", "description", "actions", "principle_id", "review_date"].forEach(function (name) {
      form.elements[name].value = existing[name] || "";
    });
    ["likelihood", "impact", "treatment", "status"].forEach(function (name) {
      form.elements[name].value = String(existing[name]);
    });
    form.elements.gdpr.checked = Boolean(existing.gdpr);
    document.getElementById("delete-form").hidden = false;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();                      // no server: save in the browser instead
    const risk = {
      id: existing ? existing.id : newId(),
      title: form.elements.title.value.trim().slice(0, 200),
      description: form.elements.description.value.trim(),
      likelihood: Number(form.elements.likelihood.value),
      impact: Number(form.elements.impact.value),
      treatment: form.elements.treatment.value,
      actions: form.elements.actions.value.trim(),
      principle_id: form.elements.principle_id.value,
      status: form.elements.status.value,
      review_date: form.elements.review_date.value,
      gdpr: form.elements.gdpr.checked,
    };
    if (!risk.title) {
      alert("Risikoen må ha en tittel.");
      return;
    }

    const list = loadRisks().filter(function (item) { return item.id !== risk.id; });
    list.push(risk);
    if (saveRisks(list)) location.href = form.dataset.listUrl;
  });

  // The delete form already asks "Slette denne risikoen?" (onsubmit in the HTML).
  // If the user said no, the event is cancelled and we do nothing.
  document.getElementById("delete-form").addEventListener("submit", function (event) {
    if (event.defaultPrevented) return;
    event.preventDefault();
    const list = loadRisks().filter(function (item) { return item.id !== editId; });
    if (saveRisks(list)) location.href = form.dataset.listUrl;
  });
}

renderList();
setupForm();
