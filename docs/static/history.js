/*
  history.js: the "Utvikling over tid" graph and table in the report (v9). Loaded in both versions.

  The rows come from Flask (#history-data, from the database) or, on GitHub Pages,
  from the browser ("grunnmur-history", written by static-history.js).
  One row per day with changes:  { date: "2026-11-05", principles: 40, measures: 12, ... }

  The graph is a plain SVG line chart, drawn here so both versions share one drawing:
    - four lines in percent (0-100) on one axis, time along the bottom
    - a legend, and a label at the end of each line on wider screens
    - hover (or arrow keys) shows the values for one day
    - the same numbers as a table under "Vis som tabell", for screen readers and print
  The open risks and incidents are counts, not percentages, so they are only in the
  table and the tooltip, never on the percent axis.
*/

(function () {
  const section = document.getElementById("history");
  if (!section) return;
  const config = JSON.parse(document.getElementById("history-data").textContent);
  let rows = config.rows;
  if (section.hasAttribute("data-static")) {
    try {
      rows = JSON.parse(localStorage.getItem("grunnmur-history")) || [];
    } catch (error) {
      rows = [];
    }
  }

  const chart = document.getElementById("history-chart");
  const tooltip = document.getElementById("history-tooltip");
  const SVG = "http://www.w3.org/2000/svg";
  const dateLabel = function (text) { return text.split("-").reverse().join("."); };   // dd.mm.yyyy
  const dayNumber = function (text) { return Date.parse(text + "T00:00:00Z") / 86400000; };

  document.getElementById("history-empty").hidden = rows.length > 0;
  section.querySelector(".history-body").hidden = rows.length === 0;
  if (!rows.length) return;

  // ---------- The table ----------
  const body = document.querySelector("#history-table tbody");
  rows.slice().reverse().forEach(function (row) {       // newest first
    const tr = document.createElement("tr");
    const cells = [dateLabel(row.date)]
      .concat(config.series.map(function (s) { return row[s[0]] + " %"; }))
      .concat(config.counts.map(function (c) { return row[c[0]]; }));
    cells.forEach(function (text, index) {
      const cell = document.createElement(index === 0 ? "th" : "td");
      if (index === 0) cell.scope = "row";
      cell.textContent = text;
      tr.appendChild(cell);
    });
    body.appendChild(tr);
  });

  // ---------- The graph ----------
  function el(name, attrs, parent) {
    const node = document.createElementNS(SVG, name);
    Object.keys(attrs).forEach(function (key) { node.setAttribute(key, attrs[key]); });
    if (parent) parent.appendChild(node);
    return node;
  }

  let active = rows.length - 1;    // the day the tooltip shows (keyboard)
  let points = [];                 // x position of each day, for hover

  function draw() {
    chart.replaceChildren();
    const width = chart.clientWidth;
    const wide = width >= 560;                          // room for labels at the line ends
    const height = wide ? 260 : 220;
    const pad = { top: 12, right: wide ? 120 : 12, bottom: 28, left: 40 };
    const plotW = width - pad.left - pad.right;
    const plotH = height - pad.top - pad.bottom;
    const svg = el("svg", { width: width, height: height, viewBox: "0 0 " + width + " " + height,
                            "aria-hidden": "true", focusable: "false" }, chart);

    // Time along the bottom: days are placed by date, so a gap of a month looks like a month
    const first = dayNumber(rows[0].date);
    const span = dayNumber(rows[rows.length - 1].date) - first;
    const x = function (row) { return pad.left + (span ? ((dayNumber(row.date) - first) / span) * plotW : plotW / 2); };
    const y = function (value) { return pad.top + plotH - (value / 100) * plotH; };
    points = rows.map(x);

    // Gridlines and the percent axis: thin and quiet
    [0, 25, 50, 75, 100].forEach(function (value) {
      el("line", { x1: pad.left, x2: pad.left + plotW, y1: y(value), y2: y(value), class: "h-grid" }, svg);
      el("text", { x: pad.left - 8, y: y(value) + 4, class: "h-axis", "text-anchor": "end" }, svg).textContent = value + " %";
    });
    // First and last day under the axis
    el("text", { x: points[0], y: height - 8, class: "h-axis", "text-anchor": rows.length > 1 ? "start" : "middle" }, svg)
      .textContent = dateLabel(rows[0].date);
    if (rows.length > 1) {
      el("text", { x: points[points.length - 1], y: height - 8, class: "h-axis", "text-anchor": "end" }, svg)
        .textContent = dateLabel(rows[rows.length - 1].date);
    }

    // The crosshair, moved by hover and the arrow keys
    const cross = el("line", { y1: pad.top, y2: pad.top + plotH, class: "h-cross", visibility: "hidden" }, svg);

    // One line per series, with a dot on each day (dots only while there are few days)
    const ends = [];
    config.series.forEach(function (series, index) {
      const key = series[0];
      const color = "var(--series-" + (index + 1) + ")";
      const path = rows.map(function (row, i) { return (i ? "L" : "M") + points[i] + " " + y(row[key]); }).join(" ");
      if (rows.length > 1) el("path", { d: path, class: "h-line", stroke: color }, svg);
      rows.forEach(function (row, i) {
        if (rows.length <= 30 || i === rows.length - 1) {
          el("circle", { cx: points[i], cy: y(row[key]), r: 4, class: "h-dot", fill: color }, svg);
        }
      });
      ends.push({ label: series[2], value: rows[rows.length - 1][key], y: y(rows[rows.length - 1][key]), color: color });
    });

    // Labels at the line ends (wide screens). Lines that end close together would
    // overlap, so labels are pushed apart and joined to their line with a thin leader.
    if (wide) {
      ends.sort(function (a, b) { return a.y - b.y; });
      const gap = 16;
      ends.forEach(function (end, i) {
        end.labelY = i ? Math.max(end.y, ends[i - 1].labelY + gap) : end.y;
      });
      const overflow = ends[ends.length - 1].labelY - (pad.top + plotH);      // keep inside the chart
      if (overflow > 0) ends.forEach(function (end) { end.labelY -= overflow; });
      const lastX = points[points.length - 1];
      ends.forEach(function (end) {
        el("line", { x1: lastX + 6, y1: end.y, x2: lastX + 18, y2: end.labelY, class: "h-leader" }, svg);
        el("rect", { x: lastX + 20, y: end.labelY - 4, width: 10, height: 3, rx: 1.5, fill: end.color }, svg);
        el("text", { x: lastX + 34, y: end.labelY + 4, class: "h-label" }, svg).textContent = end.label + " " + end.value + " %";
      });
    }

    // ---------- Hover and keyboard: show one day ----------
    function show(i) {
      active = i;
      const row = rows[i];
      cross.setAttribute("x1", points[i]);
      cross.setAttribute("x2", points[i]);
      cross.setAttribute("visibility", "visible");
      tooltip.replaceChildren();
      const title = document.createElement("strong");
      title.textContent = dateLabel(row.date);
      tooltip.appendChild(title);
      config.series.forEach(function (series, index) {
        const line = document.createElement("span");
        const key = document.createElement("i");
        key.style.background = "var(--series-" + (index + 1) + ")";
        line.append(key, series[1] + ": " + row[series[0]] + " %");
        tooltip.appendChild(line);
      });
      config.counts.forEach(function (count) {
        const line = document.createElement("span");
        line.className = "muted";
        line.textContent = count[1] + ": " + row[count[0]];
        tooltip.appendChild(line);
      });
      tooltip.hidden = false;
      // Next to the crosshair, flipped to the left near the right edge
      const left = points[i] + 12 + tooltip.offsetWidth > width ? points[i] - 12 - tooltip.offsetWidth : points[i] + 12;
      tooltip.style.left = Math.max(0, left) + "px";
      tooltip.style.top = pad.top + "px";
    }
    function hide() {
      cross.setAttribute("visibility", "hidden");
      tooltip.hidden = true;
    }
    // The whole plot is the hover target, so a day is easy to hit
    const target = el("rect", { x: pad.left, y: 0, width: plotW, height: height, fill: "transparent" }, svg);
    target.addEventListener("pointermove", function (event) {
      const at = event.clientX - svg.getBoundingClientRect().left;
      let nearest = 0;
      points.forEach(function (px, i) { if (Math.abs(px - at) < Math.abs(points[nearest] - at)) nearest = i; });
      show(nearest);
    });
    target.addEventListener("pointerleave", hide);
    chart.onfocus = function () { show(active); };
    chart.onblur = hide;
    chart.onkeydown = function (event) {
      if (event.key === "ArrowLeft" && active > 0) show(active - 1);
      else if (event.key === "ArrowRight" && active < rows.length - 1) show(active + 1);
      else return;
      event.preventDefault();
    };
  }

  draw();
  // Redraw when the width changes (phone turned, window resized)
  let lastWidth = chart.clientWidth;
  window.addEventListener("resize", function () {
    if (chart.clientWidth !== lastWidth) {
      lastWidth = chart.clientWidth;
      draw();
    }
  });
})();
