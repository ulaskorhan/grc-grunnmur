/*
  data.js: export and import on the Data page (v7, incidents from v8). Loaded in both versions.

  Flask:        the server does the work (backup.py). This script only asks
                "are you sure?" before "Erstatt alt" deletes what is saved.
  GitHub Pages: there is no server, so this script does it all in the browser:
                  1. export: builds the JSON file from localStorage and downloads it,
                  2. import: checks the file with the same rules as backup.py
                     (read from #backup-rules), then replaces or merges the data,
                  3. counts what is saved.
  The file format is described at the top of backup.py.
*/

const DATA_KEYS = {
  progress: "grunnmur-progress", measures: "grunnmur-measures",
  isms: "grunnmur-isms", soa: "grunnmur-soa", risks: "grunnmur-risks",
  incidents: "grunnmur-incidents",
};
// The risk fields in the file (the same list as db.RISK_FIELDS)
const RISK_TEXT = ["title", "description", "treatment", "actions", "principle_id", "status", "review_date"];
const RISK_NUMBERS = ["likelihood", "impact", "residual_likelihood", "residual_impact"];
const RISK_FIELDS = RISK_TEXT.concat(RISK_NUMBERS, ["gdpr"]);
// v8: the incident fields in the file (the same list as backup.INCIDENT_TEXT, plus risk and gdpr)
const INCIDENT_TEXT = ["date", "title", "description", "severity", "status", "principle_id", "lessons"];

const importForm = document.getElementById("import-form");
const isStatic = importForm.hasAttribute("data-static");
const rules = JSON.parse(document.getElementById("backup-rules").textContent);

// ---------- Small helpers ----------

// A plain {...} object (not null, not a list)
function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

// Read one storage key. try/catch because storage can be blocked (e.g. private browsing).
function readKey(key, empty) {
  try {
    return JSON.parse(localStorage.getItem(key)) || empty;
  } catch (error) {
    return empty;
  }
}

// Today as YYYY-MM-DD in local time, for the file name
function today() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}

// A row's values in a fixed order, as text: two rows with the same text are exact copies
function fingerprint(row, fields) {
  return JSON.stringify(fields.map(function (field) {
    return row[field] === undefined ? null : row[field];
  }));
}

function showMessage(text, isError) {
  const ok = document.getElementById("import-result");
  const bad = document.getElementById("import-error");
  ok.hidden = isError;
  bad.hidden = !isError;
  (isError ? bad : ok).textContent = text;     // textContent: text from the file is never run as HTML
  (isError ? bad : ok).scrollIntoView({ block: "center" });
}

// ---------- 1. Export ----------

function exportData() {
  const data = { app: rules.app, format: rules.format, exported: today() };
  ["progress", "measures", "isms", "soa"].forEach(function (name) {
    data[name] = readKey(DATA_KEYS[name], {});
  });
  // Risks without their browser id (see backup.py), and with every field present
  data.risks = readKey(DATA_KEYS.risks, []).map(function (risk) {
    const item = {};
    RISK_TEXT.forEach(function (field) { item[field] = risk[field] || ""; });
    RISK_NUMBERS.forEach(function (field) { item[field] = risk[field] || null; });
    item.gdpr = Boolean(risk.gdpr);
    return item;
  });
  // v8: incidents, with the linked risk as its place in the risk list above (see backup.py)
  const place = {};
  readKey(DATA_KEYS.risks, []).forEach(function (risk, index) { place[risk.id] = index; });
  data.incidents = readKey(DATA_KEYS.incidents, []).map(function (incident) {
    const item = {};
    INCIDENT_TEXT.forEach(function (field) { item[field] = incident[field] || ""; });
    item.risk = incident.risk_id in place ? place[incident.risk_id] : null;
    item.gdpr = Boolean(incident.gdpr);
    return item;
  });

  // A temporary link to the file, clicked once, so the browser downloads it
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "grunnmur-" + data.exported + ".json";
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
}

// ---------- 2. Checking a file: the same rules and messages as backup.clean() ----------

// Returns [cleanData, null] or [null, "Norwegian message"]
function cleanBackup(data) {
  if (!isObject(data) || data.app !== rules.app) return [null, "Filen er ikke en eksport fra Grunnmur."];
  if (!rules.reads.includes(data.format)) return [null, "Filen har et format denne versjonen av Grunnmur ikke kjenner."];

  const result = {};
  for (const name of Object.keys(rules.sections)) {
    const label = rules.labels[name];
    const section = rules.sections[name];
    const rows = data[name] === undefined ? {} : data[name];   // a missing part counts as empty
    if (!isObject(rows)) return [null, label + ": feil oppbygning i filen."];
    result[name] = {};
    for (const id of Object.keys(rows)) {
      const row = rows[id];
      if (!section.ids.includes(id)) return [null, label + ": ukjent nummer «" + id + "»."];
      if (!isObject(row) || !section.statuses.includes(row.status)) return [null, label + " " + id + ": ugyldig status."];
      const notes = row.notes === undefined ? "" : row.notes;
      if (typeof notes !== "string") return [null, label + " " + id + ": notatet må være tekst."];
      const clean = { status: row.status, notes: notes.trim() };
      if (name === "progress") {               // principles also have an ISO reference and a GDPR flag
        const isoRef = row.iso_ref === undefined ? "" : row.iso_ref;
        if (typeof isoRef !== "string") return [null, label + " " + id + ": ISO-referansen må være tekst."];
        clean.iso_ref = isoRef.trim();
        clean.gdpr = row.gdpr === true;
      }
      result[name][id] = clean;
    }
  }

  const items = data.risks === undefined ? [] : data.risks;
  if (!Array.isArray(items)) return [null, "Risikoer: feil oppbygning i filen."];
  result.risks = [];
  for (let i = 0; i < items.length; i++) {
    const [risk, error] = cleanRisk(items[i]);
    if (error) return [null, "Risiko nr. " + (i + 1) + ": " + error];
    result.risks.push(risk);
  }

  // v8: incidents. A format 1 file has none, so a missing list counts as empty.
  const incidents = data.incidents === undefined ? [] : data.incidents;
  if (!Array.isArray(incidents)) return [null, "Avvik: feil oppbygning i filen."];
  result.incidents = [];
  for (let i = 0; i < incidents.length; i++) {
    const [incident, error] = cleanIncident(incidents[i], result.risks.length);
    if (error) return [null, "Avvik nr. " + (i + 1) + ": " + error];
    result.incidents.push(incident);
  }
  return [result, null];
}

// One incident, with the same checks as incidents.read_form() in Python
function cleanIncident(item, riskCount) {
  if (!isObject(item)) return [null, "feil oppbygning i filen."];
  const incident = {};
  for (const field of INCIDENT_TEXT) {
    const value = item[field] === undefined ? "" : item[field];
    if (typeof value !== "string") return [null, "«" + field + "» må være tekst."];
    incident[field] = value;
  }
  const risk = item.risk === undefined ? null : item.risk;
  if (risk !== null && !Number.isInteger(risk)) return [null, "«risk» må være et tall eller null."];
  incident.risk = risk;
  incident.title = incident.title.trim().slice(0, 200);
  incident.date = incident.date.trim();
  incident.description = incident.description.trim();
  incident.lessons = incident.lessons.trim();
  incident.gdpr = item.gdpr === true;

  if (!incident.title) return [null, "Avviket må ha en tittel."];
  const day = new Date(incident.date + "T00:00:00Z");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(incident.date) || isNaN(day) ||
      day.toISOString().slice(0, 10) !== incident.date) {
    return [null, "Velg datoen avviket ble oppdaget."];
  }
  if (!rules.incident.severities.includes(incident.severity)) return [null, "Velg en gyldig alvorlighet."];
  if (!rules.incident.statuses.includes(incident.status)) return [null, "Velg en gyldig status."];
  if (incident.principle_id && !rules.risk.principles.includes(incident.principle_id)) return [null, "Ukjent NSM-prinsipp."];
  if (risk !== null && (risk < 0 || risk >= riskCount)) return [null, "Ukjent risiko."];
  return [incident, null];
}

// One risk, with the same checks as risks.read_form() in Python
function cleanRisk(item) {
  if (!isObject(item)) return [null, "feil oppbygning i filen."];
  const risk = {};
  for (const field of RISK_TEXT) {
    const value = item[field] === undefined ? "" : item[field];
    if (typeof value !== "string") return [null, "«" + field + "» må være tekst."];
    risk[field] = value;
  }
  for (const field of RISK_NUMBERS) {
    const value = item[field] === undefined ? null : item[field];
    if (value !== null && !Number.isInteger(value)) return [null, "«" + field + "» må være et tall fra 1 til 5."];
    risk[field] = value;
  }
  risk.title = risk.title.trim().slice(0, 200);
  risk.description = risk.description.trim();
  risk.actions = risk.actions.trim();
  risk.review_date = risk.review_date.trim();
  risk.gdpr = item.gdpr === true;

  const inScale = function (n) { return Number.isInteger(n) && n >= 1 && n <= 5; };
  if (!risk.title) return [null, "Risikoen må ha en tittel."];
  if (!inScale(risk.likelihood) || !inScale(risk.impact)) return [null, "Velg sannsynlighet og konsekvens fra 1 til 5."];
  if ((risk.residual_likelihood !== null && !inScale(risk.residual_likelihood)) ||
      (risk.residual_impact !== null && !inScale(risk.residual_impact))) {
    return [null, "Restrisiko må være fra 1 til 5, eller ikke vurdert."];
  }
  if ((risk.residual_likelihood === null) !== (risk.residual_impact === null)) {
    return [null, "Velg både sannsynlighet og konsekvens etter tiltak, eller ingen av dem."];
  }
  if (risk.residual_likelihood !== null &&
      risk.residual_likelihood * risk.residual_impact > risk.likelihood * risk.impact) {
    return [null, "Restrisikoen kan ikke være høyere enn risikoen før tiltak."];
  }
  if (!rules.risk.treatments.includes(risk.treatment)) return [null, "Velg en gyldig behandling."];
  if (!rules.risk.statuses.includes(risk.status)) return [null, "Velg en gyldig status."];
  if (risk.principle_id && !rules.risk.principles.includes(risk.principle_id)) return [null, "Ukjent NSM-prinsipp."];
  if (risk.review_date) {
    // YYYY-MM-DD, and a real day (new Date("2026-02-30") rolls over to March)
    const day = new Date(risk.review_date + "T00:00:00Z");
    if (!/^\d{4}-\d{2}-\d{2}$/.test(risk.review_date) || isNaN(day) ||
        day.toISOString().slice(0, 10) !== risk.review_date) {
      return [null, "Datoen for neste gjennomgang er ugyldig."];
    }
  }
  return [risk, null];
}

// ---------- 3. Saving an imported file: the same rules as db.import_all() ----------

// Returns {risks, incidents}: how many were added, or null if the browser would not save
function importData(data, replace) {
  const updates = {};                          // storage key -> new value
  ["progress", "measures", "isms", "soa"].forEach(function (name) {
    // Merge: rows in the file overwrite the same id, the rest stays
    updates[DATA_KEYS[name]] = Object.assign(replace ? {} : readKey(DATA_KEYS[name], {}), data[name]);
  });
  const newId = function (n) { return Date.now().toString(36) + Math.random().toString(36).slice(2, 6) + n; };
  const list = replace ? [] : readKey(DATA_KEYS.risks, []);
  const saved = {};                            // fingerprint -> id of a saved risk
  list.forEach(function (risk) { saved[fingerprint(risk, RISK_FIELDS)] = risk.id; });
  const riskIds = [];                          // the browser id of each risk in the file, in order
  let added = 0;
  data.risks.forEach(function (risk) {
    const key = fingerprint(risk, RISK_FIELDS);
    if (key in saved) {                        // exactly like a risk that is already saved
      riskIds.push(saved[key]);
      return;
    }
    const id = newId(added);
    riskIds.push(id);
    list.push(Object.assign({ id: id }, risk));
    added += 1;
  });
  updates[DATA_KEYS.risks] = list;

  // v8: incidents, with the link turned from a place in the file into a browser id
  const INCIDENT_FIELDS = INCIDENT_TEXT.concat(["risk_id", "gdpr"]);
  const incidents = replace ? [] : readKey(DATA_KEYS.incidents, []);
  const savedIncidents = new Set(incidents.map(function (item) { return fingerprint(item, INCIDENT_FIELDS); }));
  let addedIncidents = 0;
  data.incidents.forEach(function (incident) {
    const item = Object.assign({}, incident, { risk_id: incident.risk === null ? null : riskIds[incident.risk] });
    delete item.risk;
    if (savedIncidents.has(fingerprint(item, INCIDENT_FIELDS))) return;
    incidents.push(Object.assign({ id: newId("i" + addedIncidents) }, item));
    addedIncidents += 1;
  });
  updates[DATA_KEYS.incidents] = incidents;

  // Write all six keys. If one fails (storage full or blocked), put the old values back,
  // so the import is never left half done.
  const before = {};
  try {
    Object.keys(updates).forEach(function (key) { before[key] = localStorage.getItem(key); });
    Object.keys(updates).forEach(function (key) { localStorage.setItem(key, JSON.stringify(updates[key])); });
  } catch (error) {
    try {
      Object.keys(before).forEach(function (key) {
        if (before[key] === null) localStorage.removeItem(key);
        else localStorage.setItem(key, before[key]);
      });
    } catch (ignored) { /* storage is blocked, nothing was saved */ }
    return null;
  }
  return { risks: added, incidents: addedIncidents };
}

// ---------- 4. What is saved now ----------

function updateCounts() {
  document.querySelectorAll("[data-saved]").forEach(function (el) {
    const name = el.dataset.saved;
    const value = readKey(DATA_KEYS[name], name === "risks" ? [] : {});
    el.textContent = Array.isArray(value) ? value.length : Object.keys(value).length;
  });
}

// ---------- Wiring ----------

importForm.addEventListener("submit", function (event) {
  const replace = importForm.elements.mode.value === "erstatt";
  if (isStatic) event.preventDefault();       // no server: the browser does the import below
  if (replace && !confirm("Slette alt du har lagret nå og erstatte det med innholdet i filen?")) {
    event.preventDefault();
    return;
  }
  if (!isStatic) return;                       // Flask: send the form to /data/import

  const file = importForm.elements.file.files[0];
  if (file.size > rules.max_bytes) {
    showMessage("Filen er for stor (over 1 MB). Ingenting er endret.", true);
    return;
  }
  file.text().then(function (text) {
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch (error) {
      showMessage("Filen er ikke gyldig JSON.", true);
      return;
    }
    const [data, error] = cleanBackup(parsed);
    if (error) {
      showMessage(error + " Ingenting er endret.", true);
      return;
    }
    const added = importData(data, replace);
    if (added === null) {
      showMessage("Kunne ikke lagre. Nettleseren blokkerer lokal lagring. Ingenting er endret.", true);
      return;
    }
    showMessage(replace
      ? "✓ Importert. Dataene er erstattet med innholdet i filen."
      : "✓ Importert og slått sammen. " + added.risks + (added.risks === 1 ? " ny risiko" : " nye risikoer") +
        " og " + added.incidents + " nye avvik lagt til.", false);
    importForm.reset();
    updateCounts();
  });
});

if (isStatic) {
  document.getElementById("export-data").addEventListener("click", exportData);
  updateCounts();
}
