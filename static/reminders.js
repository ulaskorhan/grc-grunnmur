/*
  reminders.js: "Trenger oppfølging" on the homepage, GitHub Pages version only.

  The same rules as risks.reminders() in Python: open risks whose review date
  has passed, or is within data-days days, soonest first. The risks come from
  the visitor's own browser (localStorage), like in static-risks.js.
*/

(function () {
  const box = document.getElementById("reminders");
  if (!box) return;

  let risks = [];
  try {
    risks = JSON.parse(localStorage.getItem("grunnmur-risks")) || [];
  } catch (error) { /* storage blocked: no reminders */ }

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

  const found = risks
    .filter(function (risk) { return risk.review_date && risk.status !== "lukket"; })
    .map(function (risk) { return { id: risk.id, title: risk.title, days: daysUntil(risk.review_date) }; })
    .filter(function (item) { return item.days <= Number(box.dataset.days); })
    .sort(function (a, b) { return a.days - b.days; });
  if (!found.length) return;          // nothing to follow up: the box stays hidden

  // One row per risk, built with textContent so a title is never run as HTML
  const list = box.querySelector(".reminder-list");
  const max = Number(box.dataset.max);
  const formUrl = box.dataset.editUrl.endsWith("/") ? box.dataset.editUrl : box.dataset.editUrl + "/";
  found.slice(0, max).forEach(function (item) {
    const li = document.createElement("li");
    if (item.days < 0) li.className = "is-overdue";
    const link = document.createElement("a");
    link.href = formUrl + "?id=" + encodeURIComponent(item.id);
    const title = document.createElement("strong");
    title.textContent = item.title;
    const when = document.createElement("span");
    when.textContent = reminderText(item.days);
    link.append(title, " ", when);
    li.appendChild(link);
    list.appendChild(li);
  });

  const more = box.querySelector(".reminder-more");
  if (found.length > max) {
    more.textContent = "Se alle " + found.length + " i risikoregisteret →";
    more.hidden = false;
  }
  box.hidden = false;
})();
