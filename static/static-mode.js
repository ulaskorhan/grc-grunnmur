/*
  static-mode.js: only loaded on the GitHub Pages version of Grunnmur.

  GitHub Pages cannot run Python, so there is no Flask and no database there.
  Instead this script:
    1. saves each visitor's answers in their own browser (localStorage),
    2. fills the forms and updates rings, bars and counts from that saved data.
  Nothing is ever sent to a server.

  The same script serves four kinds of items, each with its own storage key:
    - NSM principles        "grunnmur-progress"  (homepage and category pages)
    - ISO 27001 clauses     "grunnmur-isms"      (v4, the styringssystem page)
    - SoA per ISO control   "grunnmur-soa"       (v4, the ISO 27002 page)
    - NSM measures          "grunnmur-measures"  (v5, the Tiltak page and under each principle)
  The nearest element with data-store="..." (and data-default="...") chooses the key.
  Usually that is <main>, but the measure list inside a principle has its own, so one
  page can show two kinds of items.

  Saved data looks like this:
    { "2.6": { "status": "implementert", "notes": "...", "iso_ref": "A.5.15", "gdpr": true } }
*/

const SCORE = { ikke_startet: 0, delvis: 0.5, implementert: 1 };   // only used for rings and bars

// The storage key and default status for an element, from the nearest data-store.
function storeOf(element) {
  const box = element.closest("[data-store]");
  return {
    key: (box && box.dataset.store) || "grunnmur-progress",
    fallback: (box && box.dataset.default) || "ikke_startet",
  };
}

// Read saved data. try/catch because storage can be blocked (e.g. private browsing).
function loadData(key) {
  try {
    return JSON.parse(localStorage.getItem(key)) || {};
  } catch (error) {
    return {};
  }
}

function saveData(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data));
    return true;
  } catch (error) {
    alert("Kunne ikke lagre. Nettleseren blokkerer lokal lagring.");
    return false;
  }
}

function statusOf(data, id, fallback) {
  return (data[id] && data[id].status) || fallback;
}

// The item's own form and summary. A principle holds measures (with forms) inside it,
// so "the first form inside" is not enough: it must belong to this item, not a nested one.
function ownForm(details) {
  return Array.from(details.querySelectorAll("form")).find(function (form) {
    return form.closest("details.item") === details;
  });
}

// "p2.6" -> "2.6", "c6.1.2" -> "6.1.2", "k8.13" -> "8.13", "t2.6.4" -> "2.6.4":
// the first letter is only there for the HTML id
function itemId(details) {
  return details.id.slice(1);
}

// Update every block marked with data-ids="1.1 1.2 ...": rings, bars, % and counts.
function updateSummaries() {
  document.querySelectorAll("[data-ids]").forEach(function (block) {
    const store = storeOf(block);
    const data = loadData(store.key);
    const ids = block.dataset.ids.trim().split(/\s+/);
    const counts = {};
    let points = 0;
    ids.forEach(function (id) {
      const status = statusOf(data, id, store.fallback);
      counts[status] = (counts[status] || 0) + 1;
      points += SCORE[status] || 0;
    });
    const percent = Math.round((100 * points) / ids.length);

    block.querySelectorAll(".ring").forEach(function (ring) {
      ring.style.setProperty("--p", percent);
    });
    block.querySelectorAll(".bar-fill").forEach(function (bar) {
      bar.style.width = percent + "%";
    });
    block.querySelectorAll(".js-pct").forEach(function (el) {
      el.textContent = percent;
    });
    block.querySelectorAll("[data-count]").forEach(function (el) {
      el.textContent = counts[el.dataset.count] || 0;
    });
  });
}

// Show one item's saved values: every form field by its name, plus the status label and stripe.
function updateItem(details) {
  const store = storeOf(details);
  const data = loadData(store.key);
  const row = data[itemId(details)] || {};
  const status = statusOf(data, itemId(details), store.fallback);
  const form = ownForm(details);

  Array.from(form.elements).forEach(function (field) {
    if (!field.name || ["radio", "submit", "hidden"].includes(field.type)) return;
    if (field.type === "checkbox") field.checked = Boolean(row[field.name]);
    else field.value = row[field.name] || "";
  });
  form.elements.status.value = status;

  // Swap the old "is-<status>" class for the new one (it colours the stripe on the left)
  Array.from(details.classList).forEach(function (name) {
    if (name.startsWith("is-")) details.classList.remove(name);
  });
  details.classList.add("is-" + status);

  // The label comes from the chosen radio button, so it is always the same text as in the form
  const pill = details.querySelector(":scope > summary .status");
  const checked = form.querySelector('input[name="status"]:checked');
  pill.className = "status status-" + status;
  pill.textContent = checked.nextElementSibling.textContent;

  const tag = details.querySelector(":scope > summary .tag");      // "Personvern", principles only
  if (tag) tag.hidden = !row.gdpr;
}

function renderAll() {
  document.querySelectorAll("details.item").forEach(updateItem);
  updateSummaries();
}

// Save an item when its form is submitted, instead of sending it to a server.
document.querySelectorAll("details.item form").forEach(function (form) {
  form.addEventListener("submit", function (event) {
    event.preventDefault();                 // stop the normal POST request
    const details = form.closest("details.item");

    // Collect every named field: text as trimmed text, checkboxes as true/false.
    // Hidden fields only tell Flask where to go back to, so they are not saved.
    const row = { status: form.elements.status.value };
    Array.from(form.elements).forEach(function (field) {
      if (!field.name || ["radio", "submit", "hidden"].includes(field.type)) return;
      row[field.name] = field.type === "checkbox" ? field.checked : field.value.trim();
    });

    const key = storeOf(details).key;
    const data = loadData(key);
    data[itemId(details)] = row;
    if (!saveData(key, data)) return;
    renderAll();

    // Show "✓ Lagret" for two seconds
    const saved = form.querySelector(".saved");
    saved.hidden = false;
    setTimeout(function () { saved.hidden = true; }, 2000);
  });
});

// "Slett mine data" in the footer removes everything this site saved.
const clearButton = document.getElementById("clear-data");
if (clearButton) {
  clearButton.addEventListener("click", function () {
    if (confirm("Slette alt du har lagret i denne nettleseren (fremdrift, tiltak, risikoer, styringssystem og SoA)?")) {
      try {
        ["grunnmur-progress", "grunnmur-measures", "grunnmur-risks", "grunnmur-isms", "grunnmur-soa"].forEach(function (key) {
          localStorage.removeItem(key);
        });
      } catch (error) { /* nothing saved */ }
      location.reload();                    // redraw the page with empty data
    }
  });
}

renderAll();
