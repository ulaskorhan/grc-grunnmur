/*
  static-incidents.js: the incident log (v8) on the GitHub Pages version.

  Works like static-risks.js: everything is saved in the visitor's own browser
  (localStorage), and nothing is sent to a server. This file handles:
    - the list   (/avvik/ and the report): builds one row per saved incident
    - the form   (/avvik/ny/): creates an incident, or edits one with ?id=...

  Saved data looks like this (a list of incidents):
    [ { "id": "lq3k9x2a", "date": "2026-11-01", "title": "...", "severity": "hoy",
        "status": "apen", "principle_id": "2.7", "risk_id": "lq2a8c1d", "gdpr": false,
        "lessons": "..." } ]
  risk_id is the browser id of a risk in "grunnmur-risks", or null.

  Everything is inside one function, so its names (buildRow, ...) never clash with
  static-risks.js, which the report page loads too.
*/

(function () {
const INCIDENTS_KEY = "grunnmur-incidents";

function loadList(key) {
  try {
    return JSON.parse(localStorage.getItem(key)) || [];
  } catch (error) {
    return [];
  }
}

function saveIncidents(list) {
  try {
    localStorage.setItem(INCIDENTS_KEY, JSON.stringify(list));
    return true;
  } catch (error) {
    alert("Kunne ikke lagre. Nettleseren blokkerer lokal lagring.");
    return false;
  }
}

// "2026-11-01" -> "01.11.2026", like incidents.enrich() in Python
function dateLabel(text) {
  return text.split("-").reverse().join(".");
}

// ---------- The list (incident page and report) ----------

// Same order as incidents.sort_key(): open first, then newest, then title
function compareIncidents(a, b) {
  const closedA = a.status === "lukket" ? 1 : 0;
  const closedB = b.status === "lukket" ? 1 : 0;
  if (closedA !== closedB) return closedA - closedB;
  if (a.date !== b.date) return a.date < b.date ? 1 : -1;
  return a.title.toLowerCase().localeCompare(b.title.toLowerCase(), "no");
}

function buildRow(item, editUrl, config, riskTitles) {
  const template = document.getElementById("incident-row-template");
  const row = template.content.firstElementChild.cloneNode(true);
  row.className = "risk incident level-" + item.severity + (item.status === "lukket" ? " is-closed" : "");
  const formUrl = editUrl.endsWith("/") ? editUrl : editUrl + "/";
  row.querySelector("a").href = formUrl + "?id=" + encodeURIComponent(item.id);

  // textContent (not innerHTML) so a title like "<script>" is shown as text, never run
  row.querySelector('[data-field="date_label"]').textContent = dateLabel(item.date);
  row.querySelector('[data-field="title"]').textContent = item.title;
  row.querySelector('[data-field="severity_label"]').textContent = config.severities[item.severity];
  row.querySelector('[data-field="status_label"]').textContent = config.statuses[item.status];

  const principle = row.querySelector('[data-field="principle"]');
  principle.textContent = "NSM " + item.principle_id;
  principle.hidden = !item.principle_id;
  const risk = row.querySelector('[data-field="risk_title"]');
  const riskTitle = riskTitles[item.risk_id] || "";
  risk.textContent = "Risiko: " + riskTitle;
  risk.hidden = !riskTitle;
  row.querySelector('[data-field="gdpr"]').hidden = !item.gdpr;
  const lessons = row.querySelector('[data-field="lessons"]');
  lessons.textContent = "Tiltak og læring: " + (item.lessons || "");
  lessons.hidden = !item.lessons;
  return row;
}

function renderIncidents() {
  const list = document.getElementById("incident-list");
  const configElement = document.getElementById("incident-config");
  if (!list || !configElement) return;
  const config = JSON.parse(configElement.textContent);

  const riskTitles = {};
  loadList("grunnmur-risks").forEach(function (risk) { riskTitles[risk.id] = risk.title; });
  const items = loadList(INCIDENTS_KEY).sort(compareIncidents);

  list.replaceChildren();
  items.forEach(function (item) {
    list.appendChild(buildRow(item, list.dataset.editUrl, config, riskTitles));
  });
  const empty = document.getElementById("incident-empty") || document.getElementById("empty-state");
  if (empty) empty.hidden = items.length > 0;
}

// ---------- The form page ----------

function setupIncidentForm() {
  const form = document.getElementById("incident-form");
  if (!form) return;

  // The risks saved in this browser, as options in "Koblet risiko"
  const risks = loadList("grunnmur-risks");
  risks.forEach(function (risk) {
    const option = document.createElement("option");
    option.value = risk.id;
    option.textContent = risk.title;
    form.elements.risk_id.appendChild(option);
  });

  const editId = new URLSearchParams(location.search).get("id");
  const existing = loadList(INCIDENTS_KEY).find(function (item) { return item.id === editId; });

  if (existing) {
    document.getElementById("form-heading").textContent = "Rediger avvik";
    document.title = "Rediger avvik · Grunnmur";
    ["date", "title", "description", "principle_id", "lessons", "severity", "status"].forEach(function (name) {
      form.elements[name].value = existing[name] || "";
    });
    form.elements.risk_id.value = existing.risk_id || "";
    form.elements.gdpr.checked = Boolean(existing.gdpr);
    document.getElementById("delete-form").hidden = false;
  } else {
    // A new incident starts with today's local date (the built page would have the build date)
    const now = new Date();
    form.elements.date.value = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") +
                               "-" + String(now.getDate()).padStart(2, "0");
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();                      // no server: save in the browser instead
    const item = {
      id: existing ? existing.id : Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      date: form.elements.date.value,
      title: form.elements.title.value.trim().slice(0, 200),
      description: form.elements.description.value.trim(),
      severity: form.elements.severity.value,
      status: form.elements.status.value,
      principle_id: form.elements.principle_id.value,
      risk_id: form.elements.risk_id.value || null,
      gdpr: form.elements.gdpr.checked,
      lessons: form.elements.lessons.value.trim(),
    };
    // The same checks as incidents.read_form() in Python (the menus only offer valid values)
    if (!item.title) {
      alert("Avviket må ha en tittel.");
      return;
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(item.date)) {
      alert("Velg datoen avviket ble oppdaget.");
      return;
    }
    const list = loadList(INCIDENTS_KEY).filter(function (other) { return other.id !== item.id; });
    list.push(item);
    if (saveIncidents(list)) location.href = form.dataset.listUrl;
  });

  // The delete form already asks "Slette dette avviket?" (onsubmit in the HTML)
  document.getElementById("delete-form").addEventListener("submit", function (event) {
    if (event.defaultPrevented) return;
    event.preventDefault();
    const list = loadList(INCIDENTS_KEY).filter(function (item) { return item.id !== editId; });
    if (saveIncidents(list)) location.href = form.dataset.listUrl;
  });
}

renderIncidents();
setupIncidentForm();
})();
