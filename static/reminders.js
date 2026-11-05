/*
  reminders.js: "Trenger oppfølging" on the homepage, GitHub Pages version only.

  The same rules as Python, with the data from the visitor's own browser (localStorage):
    - risks.reminders(): open risks whose review date has passed, or is within
      data-days days, soonest first
    - incidents.open_incidents() (v8): incidents that are not closed,
      most severe first, then newest
  At most data-max of each are listed.
*/

(function () {
  const box = document.getElementById("reminders");
  if (!box) return;

  function readList(key) {
    try {
      return JSON.parse(localStorage.getItem(key)) || [];
    } catch (error) {
      return [];                    // storage blocked: nothing to show
    }
  }

  // Whole days from today (local date) to a "YYYY-MM-DD" date. Negative = in the past.
  const now = new Date();
  const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  function daysUntil(text) {
    const [year, month, day] = text.split("-").map(Number);
    return Math.round((Date.UTC(year, month - 1, day) - today) / 86400000);
  }

  // The same text as risks.reminder_text()
  function reminderText(days) {
    if (days < 0) return "Forfalt for " + -days + (days === -1 ? " dag" : " dager") + " siden";
    if (days === 0) return "Gjennomgås i dag";
    if (days === 1) return "Gjennomgås i morgen";
    return "Gjennomgås om " + days + " dager";
  }

  // The same text as incidents.reminder_text()
  const SEVERITIES = { lav: "Lav", middels: "Middels", hoy: "Høy" };
  function incidentText(item) {
    return (item.status === "apen" ? "Åpent avvik" : "Avvik under behandling") + " · " + SEVERITIES[item.severity];
  }

  const risks = readList("grunnmur-risks")
    .filter(function (risk) { return risk.review_date && risk.status !== "lukket"; })
    .map(function (risk) { return { id: risk.id, title: risk.title, days: daysUntil(risk.review_date) }; })
    .filter(function (item) { return item.days <= Number(box.dataset.days); })
    .sort(function (a, b) { return a.days - b.days; });

  const order = Object.keys(SEVERITIES);              // lav, middels, hoy
  const incidents = readList("grunnmur-incidents")
    .filter(function (item) { return item.status !== "lukket"; })
    .sort(function (a, b) {
      const bySeverity = order.indexOf(b.severity) - order.indexOf(a.severity);
      return bySeverity || (a.date < b.date ? 1 : a.date > b.date ? -1 : 0);   // then newest first
    });

  if (!risks.length && !incidents.length) return;     // nothing to follow up: the box stays hidden

  // One row, built with textContent so a title is never run as HTML
  const list = box.querySelector(".reminder-list");
  function addRow(url, id, title, text, urgent) {
    const li = document.createElement("li");
    if (urgent) li.className = "is-overdue";
    const link = document.createElement("a");
    link.href = (url.endsWith("/") ? url : url + "/") + "?id=" + encodeURIComponent(id);
    const strong = document.createElement("strong");
    strong.textContent = title;
    const when = document.createElement("span");
    when.textContent = text;
    link.append(strong, " ", when);
    li.appendChild(link);
    list.appendChild(li);
  }

  const max = Number(box.dataset.max);
  risks.slice(0, max).forEach(function (item) {
    addRow(box.dataset.editUrl, item.id, item.title, reminderText(item.days), item.days < 0);
  });
  incidents.slice(0, max).forEach(function (item) {
    addRow(box.dataset.incidentUrl, item.id, item.title, incidentText(item), item.severity === "hoy");
  });

  // "Se alle ..." when a list is longer than max
  const [riskMore, incidentMore] = box.querySelectorAll(".reminder-more");
  if (risks.length > max) {
    riskMore.textContent = "Se alle " + risks.length + " i risikoregisteret →";
    riskMore.hidden = false;
  }
  if (incidents.length > max) {
    incidentMore.textContent = "Se alle " + incidents.length + " åpne avvik →";
    incidentMore.hidden = false;
  }
  box.hidden = false;
})();
