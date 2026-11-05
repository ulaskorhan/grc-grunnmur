/*
  static-history.js: progress history (v9) on the GitHub Pages version. Loaded on every page.

  Notes today's numbers in localStorage ("grunnmur-history"), with the same rule as
  db.record_history() in Python: at most one row per day, and no row for a day whose
  numbers are the same as on the last earlier day. So the graph only gets a point
  on days when something changed.

  Flask notes the numbers after each saved form. Here there is no server, so the
  numbers are noted when a page opens and when it is left, which catches every save.
  A visitor who has saved nothing gets no history.
*/

(function () {
  const HISTORY_KEY = "grunnmur-history";
  const ids = JSON.parse(document.getElementById("history-ids").textContent);
  const SCORE = { ikke_startet: 0, delvis: 0.5, implementert: 1 };   // the same as app.SCORE

  function read(key, empty) {
    try {
      return JSON.parse(localStorage.getItem(key)) || empty;
    } catch (error) {
      return empty;
    }
  }

  // Like app.percent_done(): 0-100 over a list of ids
  function percentDone(list, rows) {
    const points = list.reduce(function (sum, id) { return sum + (rows[id] ? SCORE[rows[id].status] || 0 : 0); }, 0);
    return Math.round((100 * points) / list.length);
  }

  // Like app.progress_snapshot()
  function snapshot() {
    const soa = read("grunnmur-soa", {});
    const assessed = ids.soa.filter(function (id) { return soa[id] && soa[id].status !== "ikke_vurdert"; }).length;
    const open = function (item) { return item.status !== "lukket"; };
    return {
      principles: percentDone(ids.principles, read("grunnmur-progress", {})),
      measures: percentDone(ids.measures, read("grunnmur-measures", {})),
      isms: percentDone(ids.isms, read("grunnmur-isms", {})),
      soa: Math.round((100 * assessed) / ids.soa.length),
      open_risks: read("grunnmur-risks", []).filter(open).length,
      open_incidents: read("grunnmur-incidents", []).filter(open).length,
    };
  }

  function hasData() {
    return ["grunnmur-progress", "grunnmur-measures", "grunnmur-isms", "grunnmur-soa",
            "grunnmur-risks", "grunnmur-incidents"].some(function (key) {
      const value = read(key, null);
      return value && Object.keys(value).length > 0;
    });
  }

  function record() {
    if (!hasData()) return;
    const now = new Date();
    const today = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" +
                  String(now.getDate()).padStart(2, "0");
    const values = snapshot();
    // The same rule as db.record_history()
    const history = read(HISTORY_KEY, []).filter(function (row) { return row.date !== today; });
    const earlier = history.filter(function (row) { return row.date < today; });
    const last = earlier[earlier.length - 1];
    const same = last && Object.keys(values).every(function (key) { return last[key] === values[key]; });
    if (!same) history.push(Object.assign({ date: today }, values));
    history.sort(function (a, b) { return a.date < b.date ? -1 : 1; });
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    } catch (error) { /* storage blocked or full: no history today */ }
  }

  record();
  // Saves on the same page (e.g. a principle's status) happen without reloading
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") record();
  });
  window.addEventListener("pagehide", record);
})();
