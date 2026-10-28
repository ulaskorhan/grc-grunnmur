/*
  static-mode.js: only loaded on the GitHub Pages version of Grunnmur.

  GitHub Pages cannot run Python, so there is no Flask and no database there.
  Instead this script:
    1. saves each visitor's answers in their own browser (localStorage),
    2. fills the forms and updates rings, bars and counts from that saved data.
  Nothing is ever sent to a server.

  Saved data looks like this:
    { "2.6": { "status": "implementert", "notes": "...", "iso_ref": "A.5.15", "gdpr": true } }
*/

const STORAGE_KEY = "grunnmur-progress";
const SCORE = { ikke_startet: 0, delvis: 0.5, implementert: 1 };
const LABELS = { ikke_startet: "Ikke startet", delvis: "Delvis", implementert: "Implementert" };

// Read saved data. try/catch because storage can be blocked (e.g. private browsing).
function loadData() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch (error) {
    return {};
  }
}

function saveData(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    return true;
  } catch (error) {
    alert("Kunne ikke lagre. Nettleseren blokkerer lokal lagring.");
    return false;
  }
}

function statusOf(data, id) {
  return (data[id] && data[id].status) || "ikke_startet";
}

// Update every block marked with data-ids="1.1 1.2 ...": rings, bars, % and counts.
function updateSummaries(data) {
  document.querySelectorAll("[data-ids]").forEach(function (block) {
    const ids = block.dataset.ids.trim().split(/\s+/);
    const counts = { ikke_startet: 0, delvis: 0, implementert: 0 };
    let points = 0;
    ids.forEach(function (id) {
      const status = statusOf(data, id);
      counts[status] += 1;
      points += SCORE[status];
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
      el.textContent = counts[el.dataset.count];
    });
  });
}

// Show one principle's saved values: form fields, status label, stripe and GDPR tag.
function updatePrinciple(details, data) {
  const id = details.id.slice(1);          // "p2.6" -> "2.6"
  const row = data[id] || {};
  const status = statusOf(data, id);
  const form = details.querySelector("form");

  form.elements.status.value = status;
  form.elements.notes.value = row.notes || "";
  form.elements.iso_ref.value = row.iso_ref || "";
  form.elements.gdpr.checked = Boolean(row.gdpr);

  details.className = "principle is-" + status;
  const pill = details.querySelector(".status");
  pill.className = "status status-" + status;
  pill.textContent = LABELS[status];
  details.querySelector(".tag").hidden = !row.gdpr;
}

function renderAll() {
  const data = loadData();
  document.querySelectorAll("details.principle").forEach(function (details) {
    updatePrinciple(details, data);
  });
  updateSummaries(data);
}

// Save a principle when its form is submitted, instead of sending it to a server.
document.querySelectorAll("details.principle form").forEach(function (form) {
  form.addEventListener("submit", function (event) {
    event.preventDefault();                 // stop the normal POST request
    const details = form.closest("details.principle");
    const id = details.id.slice(1);

    const data = loadData();
    data[id] = {
      status: form.elements.status.value,
      notes: form.elements.notes.value.trim(),
      iso_ref: form.elements.iso_ref.value.trim(),
      gdpr: form.elements.gdpr.checked,
    };
    if (!saveData(data)) return;
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
    if (confirm("Slette all fremdrift som er lagret i denne nettleseren?")) {
      try { localStorage.removeItem(STORAGE_KEY); } catch (error) { /* nothing saved */ }
      renderAll();
    }
  });
}

renderAll();
