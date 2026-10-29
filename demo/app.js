/*
 * Demo ECG — trang chính (mục 01–07).
 *
 * Dữ liệu: window.DEMO_DATA (data/demo_data.js, sinh bởi build_data.py).
 * Mỗi mục đăng ký một hàm render; mục "record" được vẽ lại khi đổi record,
 * còn khi đổi theme chỉ vẽ lại màu của biểu đồ (không dựng lại DOM).
 *
 * Dùng script thường (không phải ES module) để mở index.html bằng file:// vẫn chạy.
 */
(function () {
  "use strict";

  var D = window.DEMO_DATA;
  var HAS_PLOTLY = typeof window.Plotly !== "undefined";
  var THEME_KEY = "ecg-demo-theme";
  var RECORD_KEY = "ecg-demo-record";
  var root = document.documentElement;

  // ======================================================================
  // Tiện ích
  // ======================================================================

  /** Tạo phần tử DOM. Chữ luôn đi qua textContent (không dùng innerHTML). */
  function el(tag, attrs) {
    var node = document.createElement(tag);
    var children = Array.prototype.slice.call(arguments, 2);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v == null || v === false) return;
        if (k === "class") node.className = v;
        else if (k === "text") node.textContent = v;
        else if (k.slice(0, 2) === "on") node.addEventListener(k.slice(2), v);
        else node.setAttribute(k, v === true ? "" : v);
      });
    }
    children.forEach(function (c) {
      if (c == null || c === false) return;
      node.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
    });
    return node;
  }

  function storeGet(key) {
    try { return window.localStorage.getItem(key); } catch (e) { return null; }
  }

  function storeSet(key, value) {
    try {
      if (value == null) window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, value);
    } catch (e) { /* chế độ riêng tư / bị chặn: bỏ qua */ }
  }

  function fmt(v, digits) {
    if (v == null || !isFinite(v)) return "—";
    var d = digits == null ? 0 : digits;
    return Number(v).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }

  function pct(v, digits) {
    return fmt(v * 100, digits == null ? 1 : digits) + "%";
  }

  /** Giải mã mảng int đã nhân scale trong build_data.py. */
  function decode(arr, scale) {
    var s = scale || 1000;
    var out = new Array(arr.length);
    for (var i = 0; i < arr.length; i++) out[i] = arr[i] / s;
    return out;
  }

  function isNarrow() {
    return window.matchMedia("(max-width: 760px)").matches;
  }

  // ======================================================================
  // Màu & biểu đồ
  // ======================================================================

  function palette() {
    var cs = getComputedStyle(root);
    var v = function (name) { return cs.getPropertyValue(name).trim(); };
    var series = [];
    for (var i = 1; i <= 8; i++) series.push(v("--series-" + i));
    return {
      page: v("--page"),
      surface: v("--surface"),
      surface2: v("--surface-2"),
      ink: v("--ink"),
      ink2: v("--ink-2"),
      muted: v("--muted"),
      grid: v("--grid"),
      axis: v("--axis"),
      border: v("--border"),
      accent: v("--accent"),
      other: v("--series-other"),
      series: series,
      status: {
        good: v("--status-good"),
        warning: v("--status-warning"),
        serious: v("--status-serious"),
        critical: v("--status-critical"),
      },
    };
  }

  // Màu theo loại beat: thứ tự slot cố định, các loại còn lại gom vào "khác"
  var SYMBOL_SLOT = { N: 1, V: 2, A: 3, L: 4, R: 5, F: 6, "/": 7 };
  var BEAT_SYMBOLS = ["N", "L", "R", "A", "a", "J", "S", "V", "F", "e", "j", "E", "/", "f", "Q"];

  function symbolColor(sym, P) {
    var slot = SYMBOL_SLOT[sym];
    return slot ? P.series[slot - 1] : P.other;
  }

  function symbolName(sym) {
    var s = D && D.symbols && D.symbols[sym];
    return s ? s.vi : sym;
  }

  function isBeat(sym) {
    return BEAT_SYMBOLS.indexOf(sym) !== -1;
  }

  /** "(B" → "(B · Nhịp đôi thất" */
  function rhythmName(aux) {
    var name = aux && D && D.rhythms && D.rhythms[aux];
    return name ? aux + " · " + name : aux || "";
  }

  function merge(target) {
    for (var i = 1; i < arguments.length; i++) {
      var src = arguments[i];
      if (!src) continue;
      Object.keys(src).forEach(function (k) {
        var sv = src[k];
        if (sv && typeof sv === "object" && !Array.isArray(sv) && target[k] && typeof target[k] === "object") {
          target[k] = merge({}, target[k], sv);
        } else {
          target[k] = sv;
        }
      });
    }
    return target;
  }

  function axisStyle(P, extra) {
    return merge({
      color: P.muted,
      gridcolor: P.grid,
      gridwidth: 1,
      linecolor: P.axis,
      zerolinecolor: P.axis,
      zeroline: false,
      tickfont: { color: P.muted, size: 11 },
      title: { font: { color: P.ink2, size: 12 }, standoff: 8 },
      automargin: true,
      showspikes: false,
    }, extra);
  }

  function baseLayout(P, extra) {
    var narrow = isNarrow();
    return merge({
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: { family: getComputedStyle(document.body).fontFamily, size: 12, color: P.ink2 },
      margin: { l: narrow ? 44 : 56, r: 12, t: 8, b: 40 },
      xaxis: axisStyle(P),
      yaxis: axisStyle(P),
      showlegend: false,
      legend: {
        orientation: "h", x: 0, xanchor: "left", y: 1.02, yanchor: "bottom",
        font: { color: P.ink2, size: 12 }, bgcolor: "rgba(0,0,0,0)", itemclick: "toggle", itemdoubleclick: "toggleothers",
      },
      hovermode: "closest",
      hoverlabel: {
        bgcolor: P.surface, bordercolor: P.border,
        font: { color: P.ink, size: 12, family: getComputedStyle(document.body).fontFamily },
      },
      dragmode: "zoom",
    }, extra);
  }

  var PLOT_CONFIG = {
    responsive: true,
    displaylogo: false,
    scrollZoom: false,
    modeBarButtonsToRemove: ["select2d", "lasso2d", "autoScale2d", "toggleSpikelines", "hoverCompareCartesian", "hoverClosestCartesian"],
    toImageButtonOptions: { format: "png", scale: 2 },
  };

  // Mỗi biểu đồ đăng ký build(P) → {data, layout}; đổi theme chỉ cần chạy lại build
  var charts = {};

  function plot(sectionId, div, build) {
    var entry = { div: div, build: build };
    (charts[sectionId] = charts[sectionId] || []).push(entry);
    // Div chưa gắn vào trang thì Plotly không đo được độ rộng (mặc định 700 px) → vẽ ở frame sau
    if (div.isConnected) drawEntry(entry);
    else window.setTimeout(function () { if (div.isConnected) drawEntry(entry); }, 0);
    return entry;
  }

  function drawEntry(entry) {
    if (!HAS_PLOTLY) return;
    var out = entry.build(palette());
    window.Plotly.react(entry.div, out.data, out.layout, PLOT_CONFIG);
  }

  function redrawCharts() {
    Object.keys(charts).forEach(function (k) { charts[k].forEach(drawEntry); });
  }

  function purgeCharts(sectionId) {
    (charts[sectionId] || []).forEach(function (e) { if (HAS_PLOTLY) window.Plotly.purge(e.div); });
    charts[sectionId] = [];
  }

  // ======================================================================
  // Thành phần giao diện
  // ======================================================================

  /**
   * Card biểu đồ, có nút chuyển sang dạng bảng.
   * opts: {title, sub, foot, tall, actions: [Node], table: () => {columns, rows}}
   * columns: [{label, num}] ; rows: [[...]]
   */
  function chartCard(opts) {
    var chart = el("div", { class: "chart" + (opts.tall ? " chart-tall" : ""), role: "img", "aria-label": opts.title });
    var tableBox = el("div", { class: "table-wrap", hidden: true });
    var actions = el("div", { class: "card-actions" });
    (opts.actions || []).forEach(function (a) { actions.appendChild(a); });

    if (opts.table) {
      var btn = el("button", { class: "btn", type: "button", "aria-pressed": "false", text: "Bảng" });
      btn.addEventListener("click", function () {
        var showTable = btn.getAttribute("aria-pressed") !== "true";
        btn.setAttribute("aria-pressed", String(showTable));
        if (showTable && !tableBox.firstChild) tableBox.appendChild(dataTable(opts.table()));
        tableBox.hidden = !showTable;
        chart.hidden = showTable;
        if (!showTable && HAS_PLOTLY) window.Plotly.Plots.resize(chart);
      });
      actions.appendChild(btn);
    }

    var card = el("figure", { class: "card", style: "margin:0" },
      el("div", { class: "card-head" },
        el("div", null,
          el("figcaption", { class: "card-title", text: opts.title }),
          opts.sub ? el("p", { class: "card-sub", text: opts.sub }) : null),
        actions),
      chart,
      tableBox,
      opts.foot ? el("p", { class: "card-foot", text: opts.foot }) : null);
    return { card: card, chart: chart };
  }

  function dataTable(spec) {
    var thead = el("thead");
    var hr = el("tr");
    spec.columns.forEach(function (c) { hr.appendChild(el("th", { class: c.num ? "num" : null, scope: "col", text: c.label })); });
    thead.appendChild(hr);
    var tbody = el("tbody");
    spec.rows.forEach(function (row) {
      var tr = el("tr");
      row.forEach(function (cell, i) {
        tr.appendChild(el("td", { class: spec.columns[i].num ? "num" : null, text: cell == null ? "—" : String(cell) }));
      });
      tbody.appendChild(tr);
    });
    return el("table", { class: "data" }, thead, tbody);
  }

  function tile(label, value, unit, note) {
    return el("div", { class: "tile" },
      el("p", { class: "tile-label", text: label }),
      el("p", { class: "tile-value" }, value, unit ? el("span", { class: "tile-unit", text: unit }) : null),
      note ? el("p", { class: "tile-note", text: note }) : null);
  }

  function placeholder(title, items) {
    var ul = el("ul");
    items.forEach(function (t) { ul.appendChild(el("li", { text: t })); });
    return el("div", { class: "placeholder" }, el("strong", { text: title }), ul);
  }

  function segmented(options, current, onChange) {
    var group = el("div", { class: "card-actions", role: "group" });
    options.forEach(function (o) {
      var b = el("button", { class: "btn", type: "button", "aria-pressed": String(o.value === current), text: o.label });
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(group.children, function (c) { c.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        onChange(o.value);
      });
      group.appendChild(b);
    });
    return group;
  }

  // ======================================================================
  // Trạng thái: record đang chọn
  // ======================================================================

  var state = { record: null };

  function recordById(id) {
    for (var i = 0; i < D.records.length; i++) if (D.records[i].id === id) return D.records[i];
    return null;
  }

  function currentRecord() {
    return recordById(state.record);
  }

  var SPLIT_LABEL = { train: "train", val: "validation", test: "test" };

  function setupRecordControls() {
    var saved = storeGet(RECORD_KEY);
    state.record = recordById(saved) ? saved : D.records[0].id;

    var select = document.getElementById("record-select");
    D.records.forEach(function (r) {
      select.appendChild(el("option", { value: r.id, text: r.id }));
    });
    select.value = state.record;
    select.addEventListener("change", function () { setRecord(select.value); });

    var chips = document.getElementById("record-chips");
    D.records.forEach(function (r) {
      chips.appendChild(el("button", {
        class: "record-chip", type: "button", "data-record": r.id, "aria-pressed": String(r.id === state.record),
        onclick: function () { setRecord(r.id); },
      },
        el("span", { class: "rc-id", text: "Record " + r.id }),
        el("span", { class: "rc-desc", text: r.description })));
    });
    updateRecordLabels();
  }

  function updateRecordLabels() {
    var r = currentRecord();
    document.getElementById("record-select").value = r.id;
    Array.prototype.forEach.call(document.querySelectorAll(".record-chip"), function (c) {
      c.setAttribute("aria-pressed", String(c.getAttribute("data-record") === r.id));
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-record-label]"), function (n) {
      n.textContent = "record " + r.id + " (" + r.lead + ", tập " + SPLIT_LABEL[r.split] + ")";
    });
  }

  function setRecord(id) {
    if (id === state.record || !recordById(id)) return;
    state.record = id;
    storeSet(RECORD_KEY, id);
    updateRecordLabels();
    renderSections("record");
  }

  // ======================================================================
  // Theme sáng / tối / theo hệ thống
  // ======================================================================

  var THEME_MODES = ["auto", "light", "dark"];
  var THEME_LABEL = { auto: "Tự động", light: "Sáng", dark: "Tối" };
  // Mỗi icon là danh sách nét [d, có tô đặc hay không]
  var THEME_ICON = {
    auto: [["M10 2.5a7.5 7.5 0 1 0 0 15a7.5 7.5 0 1 0 0-15Z", false], ["M10 2.5a7.5 7.5 0 0 0 0 15Z", true]],
    light: [["M10 6a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z M10 1v2 M10 17v2 M1 10h2 M17 10h2 M3.6 3.6l1.4 1.4 M15 15l1.4 1.4 M3.6 16.4 5 15 M15 5l1.4-1.4", false]],
    dark: [["M16.5 12.5A7 7 0 0 1 7.5 3.5a7 7 0 1 0 9 9Z", true]],
  };

  function themeMode() {
    var t = storeGet(THEME_KEY);
    return t === "light" || t === "dark" ? t : "auto";
  }

  function renderThemeButton(mode) {
    var btn = document.getElementById("theme-toggle");
    btn.textContent = "";
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 20 20");
    svg.setAttribute("aria-hidden", "true");
    THEME_ICON[mode].forEach(function (p) {
      var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", p[0]);
      path.setAttribute("fill", p[1] ? "currentColor" : "none");
      path.setAttribute("stroke", "currentColor");
      path.setAttribute("stroke-width", "1.6");
      path.setAttribute("stroke-linecap", "round");
      path.setAttribute("stroke-linejoin", "round");
      svg.appendChild(path);
    });
    btn.appendChild(svg);
    btn.appendChild(el("span", { text: THEME_LABEL[mode] }));
    btn.setAttribute("aria-label", "Giao diện: " + THEME_LABEL[mode] + ". Nhấn để đổi.");
    btn.title = "Giao diện: " + THEME_LABEL[mode];
  }

  function applyTheme(mode) {
    if (mode === "light" || mode === "dark") root.setAttribute("data-theme", mode);
    else root.removeAttribute("data-theme");
    storeSet(THEME_KEY, mode === "auto" ? null : mode);
    renderThemeButton(mode);
    redrawCharts();
  }

  function setupTheme() {
    renderThemeButton(themeMode());
    document.getElementById("theme-toggle").addEventListener("click", function () {
      var next = THEME_MODES[(THEME_MODES.indexOf(themeMode()) + 1) % THEME_MODES.length];
      applyTheme(next);
    });
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var onChange = function () { if (themeMode() === "auto") redrawCharts(); };
    if (mq.addEventListener) mq.addEventListener("change", onChange);
    else if (mq.addListener) mq.addListener(onChange);
  }

  // ======================================================================
  // Điều hướng: đánh dấu mục đang xem
  // ======================================================================

  function setupNav() {
    var links = {};
    Array.prototype.forEach.call(document.querySelectorAll(".nav a"), function (a) {
      links[a.getAttribute("href").slice(1)] = a;
    });
    if (!("IntersectionObserver" in window)) return;
    var visible = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
      var active = null;
      Array.prototype.some.call(document.querySelectorAll("main .section"), function (s) {
        if (visible[s.id]) { active = s.id; return true; }
        return false;
      });
      Object.keys(links).forEach(function (id) {
        if (id === active) {
          links[id].setAttribute("aria-current", "true");
          links[id].scrollIntoView({ block: "nearest", inline: "nearest" });
        } else {
          links[id].removeAttribute("aria-current");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Array.prototype.forEach.call(document.querySelectorAll("main .section"), function (s) { io.observe(s); });
  }

  // ======================================================================
  // Các mục
  // ======================================================================

  var sections = [];

  /** scope: "static" (vẽ một lần) hoặc "record" (vẽ lại khi đổi record) */
  function registerSection(id, scope, render) {
    sections.push({ id: id, scope: scope, render: render });
  }

  function renderSections(scope) {
    sections.forEach(function (s) {
      if (scope && s.scope !== scope) return;
      var body = document.getElementById(s.id + "-body");
      purgeCharts(s.id);
      body.textContent = "";
      try {
        s.render(body, s.id);
      } catch (err) {
        body.appendChild(el("div", { class: "banner", text: "Lỗi khi hiển thị mục này: " + err.message }));
        if (window.console) console.error(err);
      }
    });
  }

  // ---------- Thành phần dùng chung cho các mục ----------

  function card(title, sub) {
    var body = el("div", { class: "card-body" });
    var node = el("section", { class: "card" },
      el("div", { class: "card-head" },
        el("div", null,
          el("h3", { class: "card-title", text: title }),
          sub ? el("p", { class: "card-sub", text: sub }) : null)),
      body);
    return { card: node, body: body };
  }

  function miniTile(label, value, note) {
    return el("div", { class: "mini-tile" },
      el("p", { class: "mt-label", text: label }),
      el("p", { class: "mt-value", text: value }),
      note ? el("p", { class: "mt-note", text: note }) : null);
  }

  function kv(pairs) {
    var dl = el("dl", { class: "kv" });
    pairs.forEach(function (p) {
      if (p == null) return;
      dl.appendChild(el("dt", { text: p[0] }));
      dl.appendChild(el("dd", null, p[1]));
    });
    return dl;
  }

  function minibars(rows, max) {
    var box = el("div", { class: "minibars" });
    rows.forEach(function (r) {
      box.appendChild(el("div", { class: "mb-row" },
        el("span", { class: "mb-label" },
          r.color ? el("span", { class: "dot", style: "width:8px;height:8px;border-radius:50%;flex:none;background:" + r.color }) : null,
          r.label),
        el("span", { class: "mb-track" },
          el("span", { class: "mb-fill", style: "display:block;width:" + Math.max(0.5, r.value / max * 100) + "%;background:" + (r.color || "var(--accent)") })),
        el("span", { class: "mb-val", text: r.text })));
    });
    return box;
  }

  /** Confusion matrix 2×2: cm = [[TN, FP], [FN, TP]] (hàng = nhãn thật, cột = dự đoán). */
  function cmBlock(title, sub, cm) {
    var total = cm[0][0] + cm[0][1] + cm[1][0] + cm[1][1];
    var rowSum = [cm[0][0] + cm[0][1], cm[1][0] + cm[1][1]];
    var t = el("div", { class: "cm-table", role: "table", "aria-label": "Confusion matrix " + title });
    t.appendChild(el("span", { role: "columnheader" }));
    t.appendChild(el("span", { class: "cm-head", role: "columnheader", text: "Dự đoán Normal" }));
    t.appendChild(el("span", { class: "cm-head", role: "columnheader", text: "Dự đoán Abnormal" }));
    ["Thật Normal", "Thật Abnormal"].forEach(function (rh, i) {
      t.appendChild(el("span", { class: "cm-rowhead", role: "rowheader", text: rh }));
      [0, 1].forEach(function (j) {
        var share = rowSum[i] ? cm[i][j] / rowSum[i] : 0;
        var pctMix = Math.round(8 + share * 80);
        t.appendChild(el("span", {
          class: "cm-cell" + (pctMix > 55 ? " on-strong" : ""), role: "cell",
          style: "background:color-mix(in srgb, var(--cm-hi) " + pctMix + "%, var(--surface-2))",
          title: fmt(cm[i][j]) + " cửa sổ (" + pct(share) + " của hàng)",
        }, el("b", { text: fmt(cm[i][j]) }), pct(share)));
      });
    });
    return el("div", null,
      el("p", { class: "cm-title", text: title }),
      el("p", { class: "cm-sub", text: sub + " · " + fmt(total) + " cửa sổ" }),
      t);
  }

  function arrowSvg() {
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 20 20");
    svg.setAttribute("aria-hidden", "true");
    var p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", "M3 10h13M11 5l5 5-5 5");
    p.setAttribute("fill", "none");
    p.setAttribute("stroke", "currentColor");
    p.setAttribute("stroke-width", "1.8");
    p.setAttribute("stroke-linecap", "round");
    p.setAttribute("stroke-linejoin", "round");
    svg.appendChild(p);
    return svg;
  }

  function stmemResults() {
    return D.stmem && D.stmem.results ? D.stmem.results : null;
  }

  function stmemChosen() {
    var r = stmemResults();
    if (!r) return null;
    var e = r.experiments.filter(function (x) { return x.experiment === r.chosen_experiment; })[0];
    var cal = r.calibration && r.calibration.test_chosen;
    return { exp: e, test: cal || e.test, threshold: r.threshold };
  }

  function range(n, f) {
    var out = new Array(n);
    for (var i = 0; i < n; i++) out[i] = f(i);
    return out;
  }

  // ---------- 01. Tổng quan ----------
  registerSection("overview", "static", function (body) {
    var ds = D.dataset;
    var best = D.classification.models.reduce(function (a, m) { return m.f1 > a.f1 ? m : a; });
    var fc = D.forecast.record_100;
    var nNormal = ds.labels.filter(function (l) { return l.symbol === "N"; })[0].count;
    var st = stmemChosen();

    body.appendChild(el("div", { class: "tiles" },
      tile("Record MIT-BIH", fmt(ds.n_records), null, ds.duration_min + " phút mỗi record · " + ds.fs + " Hz · 2 lead"),
      tile("Beat có nhãn", fmt(ds.n_beats), null, ds.labels.length + " loại annotation · " + pct(nNormal / ds.n_beats) + " là nhịp N"),
      tile("F1 cao nhất", fmt(best.f1, 3), null, best.name + ", cửa sổ " + best.window + " · tập test 5 record"),
      fc ? tile("Sai số dự báo HR", fmt(fc.arima.mae, 2), "bpm",
        "MAE · ARIMA(" + fc.arima.order.join(",") + ") · 50 s cuối record " + fc.record) : null));

    // Sơ đồ pipeline: hai nhánh dùng chung hai bước đầu
    var c = card("Quy trình", "Bấm vào từng bước để tới mục tương ứng.");
    var pipe = el("div", { class: "pipeline", role: "list" });
    var lanes = [
      ["Dự báo", [
        ["#explore", "Tín hiệu thô", "MIT-BIH, 360 Hz, nhãn beat của chuyên gia"],
        ["#preprocess", "Tiền xử lý", "Band-pass 0.5–40 Hz, khử baseline, notch 60 Hz"],
        ["#hrv", "R-peak → RR → HR", "HR nội suy 1 Hz, RMSSD, STL"],
        ["#forecast", "ARIMA / SARIMA", "Dự báo rolling 1-step 50 s cuối"],
      ]],
      ["Phân loại", [
        ["#explore", "Tín hiệu thô", "Chia train/val/test theo record"],
        ["#preprocess", "Tiền xử lý", "Lọc + z-score từng cửa sổ"],
        ["#classification", "Cắt cửa sổ", "0.75 s · 4.5 s · 9 s, gán nhãn Normal/Abnormal"],
        ["#classification", "Mô hình cây · CNN · ST-MEM", "Đánh giá trên 5 record test"],
      ]],
    ];
    lanes.forEach(function (lane) {
      lane[1].forEach(function (n, i) {
        if (i) pipe.appendChild(el("span", { class: "pipe-arrow", "aria-hidden": "true" }, arrowSvg()));
        pipe.appendChild(el("a", { class: "pipe-node", href: n[0], role: "listitem" },
          i === 0 ? el("span", { class: "pn-lane", text: lane[0] }) : null,
          el("span", { class: "pn-title", text: n[1] }),
          el("span", { class: "pn-text", text: n[2] })));
      });
    });
    c.body.appendChild(pipe);
    body.appendChild(c.card);

    // Điểm chính
    var cmp = D.forecast.compare_2xx;
    var arimaWins = cmp.per_record.filter(function (r) { return r[1] < r[4]; }).length;
    var mlBest = D.classification.models.filter(function (m) { return m.family === "ml"; })
      .reduce(function (a, m) { return m.f1 > a.f1 ? m : a; });
    var ex = D.label_examples.counts.both;
    var nEx = Object.keys(ex).reduce(function (a, k) { return a + ex[k]; }, 0);
    var nDis = (ex["01"] || 0) + (ex["10"] || 0);
    var f = card("Điểm chính");
    var ul = el("ul", { class: "findings" });
    function li() { ul.appendChild(el.apply(null, ["li", null].concat(Array.prototype.slice.call(arguments)))); }
    li(el("strong", { text: "1D CNN cửa sổ 9 s đạt F1 " + fmt(best.f1, 3) }),
      ", còn mô hình đặc trưng thủ công tốt nhất (" + mlBest.name + ", cửa sổ " + mlBest.window + ") đạt " + fmt(mlBest.f1, 3) + ". Hai nhóm dùng quy tắc gán nhãn khác nhau nên không so sánh trực tiếp được (xem mục 06).");
    if (st) li(el("strong", { text: "ST-MEM Semi-finetune (lead embedding + head) đạt F1 " + fmt(st.test.f1, 3) + ", AUC " + fmt(st.test.auc, 3) }),
      " trên cùng tập test và cùng quy tắc nhãn với CNN, thấp hơn CNN 9 s (" + fmt(best.f1, 3) + ").");
    li(el("strong", { text: "ARIMA thắng SARIMA ở " + arimaWins + "/" + cmp.per_record.length + " record 2xx" }),
      " (MAE trung bình " + fmt(cmp.mean.ARIMA.mae, 2) + " so với " + fmt(cmp.mean.SARIMA.mae, 2) + " bpm). Thành phần mùa vụ không giúp ích cho HR ngắn hạn.");
    li(el("strong", { text: "Quy tắc gán nhãn thay đổi kết quả rất nhiều" }),
      ": ở record " + D.label_examples.record + ", hai quy tắc cho nhãn khác nhau ở " + nDis + "/" + nEx + " cửa sổ " + D.label_examples.window_s + " s.");
    li(el("strong", { text: pct(nNormal / ds.n_beats) + " số beat là nhịp N" }),
      ", nên dữ liệu lệch lớp; các mô hình dùng class weight hoặc SMOTE để bù.");
    f.body.appendChild(ul);
    f.body.appendChild(el("p", { class: "card-foot" },
      "Muốn xem nhịp tim chạy như trên máy theo dõi, kèm cảnh báo bất thường? ",
      el("a", { href: "monitor.html", text: "Mở màn hình theo dõi →" })));
    body.appendChild(f.card);
  });

  // ---------- 02. Dữ liệu & tín hiệu ----------
  registerSection("explore", "record", function (body, sid) {
    var r = currentRecord();
    var seg = r.segment;
    var y = decode(seg.raw, seg.scale);
    var t = new Array(y.length);
    for (var i = 0; i < y.length; i++) t[i] = seg.start_s + i / r.fs;

    var ann = seg.annotations.map(function (a) {
      return { t: seg.start_s + a[0] / r.fs, sym: a[1], aux: a[2] || "" };
    });
    var view = isNarrow() ? 5 : 10;
    var entry;

    var rangeCtl = segmented(
      [{ label: (isNarrow() ? 5 : 10) + " s", value: view }, { label: "30 s", value: seg.seconds }],
      view,
      function (v) {
        view = v;
        if (HAS_PLOTLY) window.Plotly.relayout(entry.div, { "xaxis.range": [seg.start_s, seg.start_s + v] });
      });

    var c = chartCard({
      title: "ECG thô · record " + r.id + " · lead " + r.lead,
      sub: "Đoạn " + fmt(seg.start_s, 0) + "–" + fmt(seg.start_s + seg.seconds, 0) + " s. Chữ phía trên là nhãn beat của chuyên gia. Kéo ngang để xem tiếp, nhấp đúp để về khung ban đầu.",
      actions: [rangeCtl],
      table: function () {
        return {
          columns: [{ label: "Thời gian (s)", num: true }, { label: "Ký hiệu" }, { label: "Ý nghĩa" }, { label: "Ghi chú nhịp" }],
          rows: ann.map(function (a) { return [fmt(a.t, 3), a.sym, symbolName(a.sym), rhythmName(a.aux)]; }),
        };
      },
    });
    body.appendChild(c.card);

    var yMin = Math.min.apply(null, y);
    var yMax = Math.max.apply(null, y);
    var span = yMax - yMin || 1;
    var labelY = yMax + span * 0.12;

    entry = plot(sid, c.chart, function (P) {
      var data = [{
        type: "scatter", mode: "lines", x: t, y: y, name: "ECG",
        line: { color: P.ink, width: 1.25 },
        hovertemplate: "%{y:.3f} mV<extra></extra>",
      }];

      var groups = {};
      ann.forEach(function (a) {
        var key = isBeat(a.sym) ? a.sym : "_note";
        (groups[key] = groups[key] || []).push(a);
      });
      Object.keys(groups).sort(function (a, b) { return groups[b].length - groups[a].length; }).forEach(function (key) {
        var g = groups[key];
        var note = key === "_note";
        data.push({
          type: "scatter", mode: "markers+text",
          x: g.map(function (a) { return a.t; }),
          y: g.map(function () { return labelY; }),
          text: g.map(function (a) { return note ? (a.aux || a.sym) : a.sym; }),
          textposition: "top center",
          textfont: { color: P.ink2, size: 11 },
          cliponaxis: false,
          name: note ? "Ghi chú nhịp / chất lượng" : key + " · " + symbolName(key),
          marker: note
            ? { symbol: "triangle-down", size: 8, color: P.muted, line: { color: P.surface, width: 2 } }
            : { size: 9, color: symbolColor(key, P), line: { color: P.surface, width: 2 } },
          customdata: g.map(function (a) { return note ? symbolName(a.sym) + (a.aux ? ": " + rhythmName(a.aux) : "") : symbolName(a.sym); }),
          hovertemplate: (note ? "%{customdata}" : "<b>" + key + "</b> · %{customdata}") + "<extra></extra>",
        });
      });

      return {
        data: data,
        layout: baseLayout(P, {
          height: 340,
          showlegend: true,
          margin: { t: 36 },
          hovermode: "x unified",
          dragmode: "pan",
          xaxis: axisStyle(P, {
            title: { text: "Thời gian (s)" },
            range: [seg.start_s, seg.start_s + view],
            hoverformat: ".2f",
            dtick: 1,
            minor: { dtick: 0.2, gridcolor: P.grid, gridwidth: 0.5, showgrid: true },
            showspikes: true, spikemode: "across", spikethickness: 1, spikecolor: P.axis, spikedash: "solid", spikesnap: "cursor",
          }),
          yaxis: axisStyle(P, {
            title: { text: "mV" },
            fixedrange: true,
            range: [yMin - span * 0.06, labelY + span * 0.16],
          }),
        }),
      };
    });

    // Thông tin record + beat trung bình
    var grid = el("div", { class: "grid-2" });
    var info = card("Record " + r.id, r.description);
    var beatCounts = Object.keys(r.symbol_counts).filter(isBeat)
      .map(function (k) { return [k, r.symbol_counts[k]]; })
      .sort(function (a, b) { return b[1] - a[1]; });
    var nBeats = beatCounts.reduce(function (a, b) { return a + b[1]; }, 0);
    var P0 = palette();
    info.body.appendChild(kv([
      ["Lead", r.leads.join(", ")],
      ["Thời lượng", fmt(r.duration_s / 60, 1) + " phút · " + fmt(r.fs) + " Hz"],
      ["Tập (phân loại)", SPLIT_LABEL[r.split]],
      ["Số beat", fmt(nBeats)],
      ["Nhịp", Object.keys(r.rhythms).map(rhythmName).join(" · ") || "—"],
    ]));
    info.body.appendChild(el("p", { class: "subhead", style: "font-size:14px", text: "Beat theo loại" }));
    info.body.appendChild(minibars(beatCounts.map(function (b) {
      return { label: b[0] + " · " + symbolName(b[0]), value: b[1], text: fmt(b[1]) + " · " + pct(b[1] / nBeats), color: symbolColor(b[0], P0) };
    }), beatCounts.length ? beatCounts[0][1] : 1));
    grid.appendChild(info.card);

    var mb = r.mean_beats;
    var mbLabels = Object.keys(mb.labels);
    var mc = chartCard({
      title: "Hình dạng beat trung bình",
      sub: "Trung bình ± 1 độ lệch chuẩn, căn theo đỉnh R (" + mb.pre_ms + " ms trước, " + mb.post_ms + " ms sau). Tín hiệu đã lọc.",
      table: function () {
        return {
          columns: [{ label: "Loại" }, { label: "Ý nghĩa" }, { label: "Số beat", num: true }, { label: "Biên độ đỉnh (mV)", num: true }],
          rows: mbLabels.map(function (k) {
            var m = decode(mb.labels[k].mean, mb.scale);
            return [k, symbolName(k), fmt(mb.labels[k].n), fmt(Math.max.apply(null, m), 3)];
          }),
        };
      },
    });
    grid.appendChild(mc.card);
    body.appendChild(grid);
    plot(sid, mc.chart, function (P) {
      var data = [];
      mbLabels.forEach(function (k) {
        var m = decode(mb.labels[k].mean, mb.scale);
        var s = decode(mb.labels[k].std, mb.scale);
        var x = range(m.length, function (i) { return -mb.pre_ms + i * (mb.pre_ms + mb.post_ms) / m.length; });
        var col = symbolColor(k, P);
        data.push({
          type: "scatter", mode: "lines", x: x.concat(x.slice().reverse()),
          y: m.map(function (v, i) { return v + s[i]; }).concat(m.map(function (v, i) { return v - s[i]; }).reverse()),
          fill: "toself", fillcolor: col, opacity: 0.14, line: { width: 0 }, hoverinfo: "skip", showlegend: false,
        });
        data.push({
          type: "scatter", mode: "lines", x: x, y: m, name: k + " · " + symbolName(k) + " (" + fmt(mb.labels[k].n) + ")",
          line: { color: col, width: 2 },
          hovertemplate: "<b>" + k + "</b> %{x:.0f} ms: %{y:.3f} mV<extra></extra>",
        });
      });
      return {
        data: data,
        layout: baseLayout(P, {
          height: 300, showlegend: true, margin: { t: 30 },
          xaxis: axisStyle(P, { title: { text: "ms so với đỉnh R" }, zeroline: true }),
          yaxis: axisStyle(P, { title: { text: "mV" } }),
        }),
      };
    });

    // Toàn bộ dữ liệu: phân bố nhãn + tỉ lệ bất thường theo record
    var ds = D.dataset;
    var g2 = el("div", { class: "grid-2" });
    var labels = ds.labels.slice().sort(function (a, b) { return a.count - b.count; });
    var MAP_NAME = { normal: "Normal (N)", abnormal: "Abnormal", dropped: "Bỏ qua (không phải beat)" };
    var lc = chartCard({
      title: "Phân bố nhãn trên 48 record",
      sub: "Trục log. Màu theo cách gán vào bài toán phân loại: Normal, Abnormal, hoặc bị bỏ qua.",
      table: function () {
        return {
          columns: [{ label: "Ký hiệu" }, { label: "Ý nghĩa" }, { label: "1xx", num: true }, { label: "2xx", num: true }, { label: "Tổng", num: true }, { label: "Gán thành" }],
          rows: ds.labels.map(function (l) { return [l.symbol, l.name_vi, fmt(l.count_1xx), fmt(l.count_2xx), fmt(l.count), MAP_NAME[l.mapped_to]]; }),
        };
      },
    });
    g2.appendChild(lc.card);
    plot(sid, lc.chart, function (P) {
      var colorOf = { normal: P.series[0], abnormal: P.series[1], dropped: P.other };
      return {
        data: ["normal", "abnormal", "dropped"].map(function (m) {
          var ls = labels.filter(function (l) { return l.mapped_to === m; });
          return {
            type: "bar", orientation: "h", name: MAP_NAME[m],
            y: ls.map(function (l) { return l.symbol + " · " + l.name_vi; }),
            x: ls.map(function (l) { return l.count; }),
            marker: { color: colorOf[m] },
            customdata: ls.map(function (l) { return [l.count_1xx, l.count_2xx]; }),
            hovertemplate: "%{y}<br>%{x:,} (1xx %{customdata[0]:,} · 2xx %{customdata[1]:,})<extra></extra>",
          };
        }),
        layout: baseLayout(P, {
          height: 640, showlegend: true, margin: { t: 30, l: 8 }, bargap: 0.25,
          xaxis: axisStyle(P, { type: "log", title: { text: "Số annotation (log)" } }),
          yaxis: axisStyle(P, { categoryorder: "array", categoryarray: labels.map(function (l) { return l.symbol + " · " + l.name_vi; }), tickfont: { size: 11 } }),
        }),
      };
    });

    var recs = ds.records.map(function (x) {
      return { id: x.id, split: x.split, abn: x.n_beats ? 1 - x.n_normal / x.n_beats : 0, n: x.n_beats };
    }).sort(function (a, b) { return b.abn - a.abn; });
    var SPLIT_SLOT = { train: 0, val: 2, test: 6 };
    var rc = chartCard({
      title: "Tỉ lệ beat bất thường theo record",
      sub: "Màu theo tập dùng cho phân loại. Record đang chọn được viền đậm.",
      table: function () {
        return {
          columns: [{ label: "Record" }, { label: "Tập" }, { label: "Số beat", num: true }, { label: "% bất thường", num: true }],
          rows: recs.map(function (x) { return [x.id, SPLIT_LABEL[x.split], fmt(x.n), pct(x.abn)]; }),
        };
      },
    });
    g2.appendChild(rc.card);
    body.appendChild(g2);
    plot(sid, rc.chart, function (P) {
      return {
        data: ["train", "val", "test"].map(function (sp) {
          var xs = recs.filter(function (x) { return x.split === sp; });
          return {
            type: "bar", orientation: "h", name: SPLIT_LABEL[sp],
            y: xs.map(function (x) { return x.id; }), x: xs.map(function (x) { return x.abn * 100; }),
            marker: {
              color: P.series[SPLIT_SLOT[sp]],
              line: { color: xs.map(function (x) { return x.id === r.id ? P.ink : "rgba(0,0,0,0)"; }), width: 2 },
            },
            hovertemplate: "Record %{y}: %{x:.1f}% bất thường<extra>" + SPLIT_LABEL[sp] + "</extra>",
          };
        }),
        layout: baseLayout(P, {
          height: 640, showlegend: true, margin: { t: 30 }, bargap: 0.2,
          xaxis: axisStyle(P, { title: { text: "% beat bất thường" }, range: [0, 100] }),
          yaxis: axisStyle(P, { type: "category", categoryorder: "array", categoryarray: recs.map(function (x) { return x.id; }).reverse(), tickfont: { size: 10 } }),
        }),
      };
    });
  });

  // ---------- 03. Tiền xử lý ----------
  var STAGES = [
    { key: "raw", label: "Thô", desc: "Tín hiệu gốc, còn trôi nền và nhiễu." },
    { key: "bandpass", label: "Band-pass", desc: "Butterworth 0.5–40 Hz (sosfiltfilt): bỏ trôi nền chậm và nhiễu cao tần." },
    { key: "baseline_removed", label: "Khử baseline", desc: "Trừ đường nền ước lượng bằng median filter 0.2 s rồi 0.6 s (đường nét đứt ở tầng trước)." },
    { key: "notch", label: "Notch", desc: "Notch 60 Hz và 120 Hz (Q = 30) cho nhiễu điện lưới." },
    { key: "zscore", label: "Z-score", desc: "Chuẩn hoá về trung bình 0, độ lệch chuẩn 1 (đơn vị: độ lệch chuẩn)." },
  ];
  var preState = { stage: "baseline_removed" };

  registerSection("preprocess", "record", function (body, sid) {
    var r = currentRecord();
    var seg = r.segment;
    var n = seg.raw.length;
    var t = range(n, function (i) { return seg.start_s + i / r.fs; });
    var view = isNarrow() ? 5 : 10;
    var entry;
    var descEl = el("p", { class: "card-foot" });

    function stageInfo(k) { return STAGES.filter(function (s) { return s.key === k; })[0]; }
    var ctl = segmented(STAGES.map(function (s) { return { label: s.label, value: s.key }; }), preState.stage, function (v) {
      preState.stage = v;
      drawEntry(entry);
      descEl.textContent = stageInfo(v).desc;
    });
    var c = chartCard({
      title: "Từng tầng lọc · record " + r.id,
      sub: "Đường mờ là tín hiệu thô để so sánh. Kéo ngang để xem hết 30 s.",
      actions: [ctl],
    });
    descEl.textContent = stageInfo(preState.stage).desc;
    c.card.appendChild(descEl);
    body.appendChild(c.card);

    var cache = {};
    function get(k) { return cache[k] || (cache[k] = decode(seg[k], seg.scale)); }
    entry = plot(sid, c.chart, function (P) {
      var k = preState.stage;
      var z = k === "zscore";
      var data = [];
      if (!z) data.push({ type: "scatter", mode: "lines", x: t, y: get("raw"), name: "Thô", line: { color: P.other, width: 1 }, opacity: 0.6, hoverinfo: "skip" });
      if (k === "baseline_removed") {
        data.push({ type: "scatter", mode: "lines", x: t, y: get("bandpass"), name: "Sau band-pass", line: { color: P.series[0], width: 1 }, opacity: 0.45, hoverinfo: "skip" });
        data.push({ type: "scatter", mode: "lines", x: t, y: get("baseline"), name: "Baseline ước lượng", line: { color: P.series[1], width: 1.5, dash: "dash" }, hovertemplate: "%{y:.3f} mV<extra>baseline</extra>" });
      }
      data.push({ type: "scatter", mode: "lines", x: t, y: get(k), name: stageInfo(k).label, line: { color: P.ink, width: 1.3 }, hovertemplate: "%{y:.3f}<extra></extra>" });
      return {
        data: data,
        layout: baseLayout(P, {
          height: 320, showlegend: true, margin: { t: 30 }, dragmode: "pan", hovermode: "x unified",
          xaxis: axisStyle(P, { title: { text: "Thời gian (s)" }, range: [seg.start_s, seg.start_s + view], hoverformat: ".2f" }),
          yaxis: axisStyle(P, { title: { text: z ? "z" : "mV" }, fixedrange: true }),
        }),
      };
    });

    var g = el("div", { class: "grid-2" });
    var pc = chartCard({
      title: "Phổ công suất (Welch)",
      sub: "Trước và sau toàn bộ chuỗi lọc. Vạch dọc: 0.5 Hz, 40 Hz (dải thông) và 60 Hz (điện lưới).",
    });
    g.appendChild(pc.card);
    plot(sid, pc.chart, function (P) {
      var f = r.psd.f;
      var shapes = [0.5, 40, 60].map(function (x) {
        return { type: "line", x0: x, x1: x, yref: "paper", y0: 0, y1: 1, line: { color: P.axis, width: 1, dash: "dot" } };
      });
      return {
        data: [
          { type: "scatter", mode: "lines", x: f, y: r.psd.raw_db, name: "Thô", line: { color: P.other, width: 1.4 }, hovertemplate: "%{x:.1f} Hz: %{y:.1f} dB<extra>thô</extra>" },
          { type: "scatter", mode: "lines", x: f, y: r.psd.final_db, name: "Sau lọc", line: { color: P.series[0], width: 1.6 }, hovertemplate: "%{x:.1f} Hz: %{y:.1f} dB<extra>sau lọc</extra>" },
        ],
        layout: baseLayout(P, {
          height: 300, showlegend: true, margin: { t: 30 }, shapes: shapes,
          xaxis: axisStyle(P, { title: { text: "Tần số (Hz)" }, range: [0, 100] }),
          yaxis: axisStyle(P, { title: { text: "dB" } }),
        }),
      };
    });

    var qc = card("Chỉ số chất lượng tín hiệu", "Tính trên toàn bộ 30 phút của từng record. Cột đang chọn được tô.");
    var QC = [
      ["Độ lệch chuẩn baseline (mV)", "baseline_std", 3],
      ["Biên độ baseline (mV)", "baseline_ptp", 3],
      ["Tỉ lệ năng lượng 60 Hz", "powerline_60_ratio", 4],
      ["Tỉ lệ năng lượng 50 Hz", "powerline_50_ratio", 4],
      ["Nhiễu cao tần 20–40 Hz", "hf_noise_ratio_20_40", 3],
      ["RR nhỏ nhất (s)", "rr_min", 3],
      ["RR lớn nhất (s)", "rr_max", 3],
      ["% RR bất thường", "bad_rr_pct", 2],
    ];
    var thead = el("tr", null, el("th", { scope: "col", text: "Chỉ số" }));
    D.records.forEach(function (x) {
      thead.appendChild(el("th", { class: "num" + (x.id === r.id ? " is-current" : ""), scope: "col", text: x.id }));
    });
    var tbody = el("tbody");
    QC.forEach(function (q) {
      var tr = el("tr", null, el("td", { text: q[0] }));
      D.records.forEach(function (x) {
        tr.appendChild(el("td", { class: "num" + (x.id === r.id ? " is-current" : ""), text: fmt(x.qc[q[1]], q[2]) }));
      });
      tbody.appendChild(tr);
    });
    qc.body.appendChild(el("div", { class: "table-wrap" }, el("table", { class: "data" }, el("thead", null, thead), tbody)));
    g.appendChild(qc.card);
    body.appendChild(g);
  });

  // ---------- 04. Nhịp tim & HRV ----------
  registerSection("hrv", "record", function (body, sid) {
    var r = currentRecord();
    var h = r.hr;
    var s = h.summary;
    body.appendChild(el("div", { class: "mini-tiles" },
      miniTile("HR trung bình", fmt(s.mean_hr, 1) + " bpm", "min " + fmt(s.min_hr, 0) + " · max " + fmt(s.max_hr, 0)),
      miniTile("Nhịp nhanh > 120", fmt(s.tachy_seconds) + " s", "tổng thời gian"),
      miniTile("Nhịp chậm < 50", fmt(s.brady_seconds) + " s", "tổng thời gian"),
      miniTile("Beat kiểu PVC", fmt(s.pvc_like), "RR ngắn rồi bù dài"),
      miniTile("RR outlier", fmt(s.rr_outliers), "lệch xa trung vị"),
      miniTile("Beat không đều", fmt(s.irregular_beats), "RMSSD > " + fmt(h.rmssd_threshold_ms) + " ms"),
      miniTile("Đột biến STL", fmt(s.resid_spikes), "|residual| > " + fmt(h.stl.resid_threshold, 1))));

    var tHr = range(h.hr_1hz.length, function (i) { return (h.hr_1hz_t0 + i) / 60; });
    var c1 = chartCard({
      title: "Nhịp tim theo thời gian · record " + r.id,
      sub: "HR nội suy 1 Hz trên toàn bộ 30 phút. Vạch đứt: ngưỡng nhịp nhanh 120 và nhịp chậm 50 bpm (02_EDA).",
    });
    body.appendChild(c1.card);
    plot(sid, c1.chart, function (P) {
      return {
        data: [{ type: "scatter", mode: "lines", x: tHr, y: h.hr_1hz, name: "HR", line: { color: P.series[0], width: 1.3 }, hovertemplate: "%{x:.2f} phút: %{y:.1f} bpm<extra></extra>" }],
        layout: baseLayout(P, {
          height: 280,
          shapes: [120, 50].map(function (v) { return { type: "line", xref: "paper", x0: 0, x1: 1, y0: v, y1: v, line: { color: P.status.critical, width: 1, dash: "dash" } }; }),
          annotations: [[120, "nhịp nhanh"], [50, "nhịp chậm"]].map(function (a) {
            return { xref: "paper", x: 1, y: a[0], text: a[1] + " " + a[0], showarrow: false, xanchor: "right", yanchor: "bottom", font: { size: 11, color: P.ink2 } };
          }),
          xaxis: axisStyle(P, { title: { text: "Phút" } }),
          yaxis: axisStyle(P, { title: { text: "bpm" }, range: [Math.min(40, Math.min.apply(null, h.hr_1hz) - 5), Math.max(130, Math.max.apply(null, h.hr_1hz) + 5)] }),
        }),
      };
    });

    var g = el("div", { class: "grid-2" });
    var tb = h.beat_t_ms.map(function (v) { return v / 60000; });
    var c2 = chartCard({ title: "Chuỗi RR theo loại beat", sub: "Mỗi chấm là một khoảng RR, màu theo nhãn beat chuyên gia. Vòng tròn rỗng: beat kiểu PVC và RR outlier do luật 02_EDA phát hiện." });
    g.appendChild(c2.card);
    plot(sid, c2.chart, function (P) {
      var bySym = {};
      for (var i = 0; i < h.rr_ms.length; i++) {
        var k = h.beat_symbols[i];
        (bySym[k] = bySym[k] || []).push(i);
      }
      var data = Object.keys(bySym).sort(function (a, b) { return bySym[b].length - bySym[a].length; }).map(function (k) {
        var idx = bySym[k];
        return {
          type: "scatter", mode: "markers", name: k + " · " + symbolName(k) + " (" + fmt(idx.length) + ")",
          x: idx.map(function (i) { return tb[i]; }), y: idx.map(function (i) { return h.rr_ms[i]; }),
          marker: { color: symbolColor(k, P), size: 4, opacity: k === "N" ? 0.55 : 0.9 },
          hovertemplate: "%{x:.2f} phút: RR %{y} ms<extra>" + k + "</extra>",
        };
      });
      [[h.pvc_like_idx, "Beat kiểu PVC (luật)", "circle-open", P.ink2], [h.rr_outlier_idx, "RR outlier", "circle-open", P.status.critical]].forEach(function (m) {
        if (!m[0].length) return;
        data.push({
          type: "scatter", mode: "markers", name: m[1],
          x: m[0].map(function (i) { return tb[i]; }), y: m[0].map(function (i) { return h.rr_ms[i]; }),
          marker: { symbol: m[2], color: m[3], size: 8, line: { width: 1.2 } },
          hovertemplate: "%{x:.2f} phút: RR %{y} ms<extra>" + m[1] + "</extra>",
        });
      });
      return {
        data: data,
        layout: baseLayout(P, {
          height: 320, showlegend: true, margin: { t: 30 },
          xaxis: axisStyle(P, { title: { text: "Phút" } }),
          yaxis: axisStyle(P, { title: { text: "RR (ms)" } }),
        }),
      };
    });

    var c3 = chartCard({ title: "RMSSD cuộn (20 beat)", sub: "Độ biến thiên giữa các nhịp liên tiếp. Vạch đứt: ngưỡng \"không đều\" " + fmt(h.rmssd_threshold_ms) + " ms." });
    g.appendChild(c3.card);
    plot(sid, c3.chart, function (P) {
      return {
        data: [{ type: "scatter", mode: "lines", x: tb, y: h.rmssd_ms, name: "RMSSD", connectgaps: false, line: { color: P.series[6], width: 1.3 }, hovertemplate: "%{x:.2f} phút: %{y} ms<extra></extra>" }],
        layout: baseLayout(P, {
          height: 320,
          shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, y0: h.rmssd_threshold_ms, y1: h.rmssd_threshold_ms, line: { color: P.status.critical, width: 1, dash: "dash" } }],
          xaxis: axisStyle(P, { title: { text: "Phút" } }),
          yaxis: axisStyle(P, { title: { text: "ms" }, rangemode: "tozero" }),
        }),
      };
    });
    body.appendChild(g);

    var c4 = chartCard({
      title: "Phân rã STL của HR (chu kỳ " + h.stl.period + " s)",
      sub: "Quan sát = xu hướng + mùa vụ + phần dư. Chấm đỏ: phần dư vượt ngưỡng " + fmt(h.stl.resid_threshold, 1) + " bpm.",
      tall: true,
    });
    body.appendChild(c4.card);
    plot(sid, c4.chart, function (P) {
      var spikes = h.stl.resid_spike_idx;
      var parts = [["Quan sát", h.hr_1hz, P.series[0]], ["Xu hướng", h.stl.trend, P.series[1]], ["Mùa vụ", h.stl.seasonal, P.series[2]], ["Phần dư", h.stl.resid, P.other]];
      var data = parts.map(function (p, i) {
        return {
          type: "scatter", mode: "lines", x: tHr, y: p[1], name: p[0], xaxis: "x", yaxis: i ? "y" + (i + 1) : "y",
          line: { color: p[2], width: 1.2 }, hovertemplate: "%{x:.2f} phút: %{y:.2f}<extra>" + p[0] + "</extra>",
        };
      });
      data.push({
        type: "scatter", mode: "markers", name: "Đột biến", xaxis: "x", yaxis: "y4",
        x: spikes.map(function (i) { return tHr[i]; }), y: spikes.map(function (i) { return h.stl.resid[i]; }),
        marker: { color: P.status.critical, size: 6 }, hovertemplate: "%{x:.2f} phút: %{y:.1f}<extra>đột biến</extra>",
      });
      var lay = baseLayout(P, {
        height: 520, margin: { t: 8 },
        xaxis: axisStyle(P, { title: { text: "Phút" }, anchor: "y4" }),
        grid: { rows: 4, columns: 1, pattern: "independent" },
      });
      var doms = [[0.78, 1], [0.53, 0.75], [0.28, 0.5], [0, 0.25]];
      parts.forEach(function (p, i) {
        lay["yaxis" + (i ? i + 1 : "")] = axisStyle(P, { domain: doms[i], title: { text: p[0], font: { size: 11 } }, anchor: "x" });
      });
      delete lay.grid;
      return { data: data, layout: lay };
    });
  });

  // ---------- 05. Dự báo ----------
  registerSection("forecast", "static", function (body, sid) {
    var fc = D.forecast.record_100;
    if (fc) {
      body.appendChild(el("div", { class: "mini-tiles" },
        miniTile("ARIMA(" + fc.arima.order.join(",") + ") · MAE", fmt(fc.arima.mae, 3) + " bpm", "notebook: " + fmt(fc.arima.reported.mae, 3)),
        miniTile("ARIMA · RMSE", fmt(fc.arima.rmse, 3) + " bpm", "notebook: " + fmt(fc.arima.reported.rmse, 3)),
        miniTile("SARIMA · MAE", fmt(fc.sarima.mae, 3) + " bpm", "notebook: " + fmt(fc.sarima.reported.mae, 3)),
        miniTile("SARIMA · RMSE", fmt(fc.sarima.rmse, 3) + " bpm", "notebook: " + fmt(fc.sarima.reported.rmse, 3))));
      var g = el("div", { class: "grid-2" });
      [["arima", "ARIMA(" + fc.arima.order.join(",") + ")", 1], ["sarima", "SARIMA(" + fc.sarima.order.join(",") + ")(" + fc.sarima.seasonal_order.join(",") + ")", 2]].forEach(function (m) {
        var d = fc[m[0]];
        var tPred = d.t.slice(d.t.length - d.pred.length);
        var c = chartCard({
          title: m[1] + " · record " + fc.record,
          sub: d.mode + ". Nguồn HR: " + d.hr_source + ".",
          table: function () {
            return {
              columns: [{ label: "Giây", num: true }, { label: "HR thật", num: true }, { label: "Dự báo", num: true }, { label: "Sai số", num: true }],
              rows: tPred.map(function (tt, i) {
                var a = d.actual[d.actual.length - d.pred.length + i];
                return [tt, fmt(a, 2), fmt(d.pred[i], 2), fmt(d.pred[i] - a, 2)];
              }),
            };
          },
        });
        g.appendChild(c.card);
        plot(sid, c.chart, function (P) {
          return {
            data: [
              { type: "scatter", mode: "lines", x: d.t, y: d.actual, name: "HR thật", line: { color: P.ink, width: 1.5 }, hovertemplate: "%{x} s: %{y:.1f} bpm<extra>thật</extra>" },
              { type: "scatter", mode: "lines", x: tPred, y: d.pred, name: "Dự báo", line: { color: P.series[m[2] - 1], width: 2, dash: "dash" }, hovertemplate: "%{x} s: %{y:.1f} bpm<extra>dự báo</extra>" },
            ],
            layout: baseLayout(P, {
              height: 280, showlegend: true, margin: { t: 30 },
              shapes: [{ type: "rect", x0: tPred[0], x1: tPred[tPred.length - 1], yref: "paper", y0: 0, y1: 1, fillcolor: P.accent, opacity: 0.06, line: { width: 0 } }],
              xaxis: axisStyle(P, { title: { text: "Giây trong record" } }),
              yaxis: axisStyle(P, { title: { text: "bpm" } }),
            }),
          };
        });
      });
      body.appendChild(g);
    }

    var g2 = el("div", { class: "grid-2" });
    var gs = D.forecast.grid_search;
    var top = gs.top.slice().reverse();
    var c3 = chartCard({
      title: "Top 10 bậc ARIMA theo AIC",
      sub: gs.note + " Thanh ngang: ± 1 độ lệch chuẩn giữa các record — lớn hơn nhiều so với chênh lệch AIC giữa các bậc.",
      table: function () {
        return {
          columns: [{ label: "(p,d,q)" }, { label: "AIC TB", num: true }, { label: "Độ lệch", num: true }, { label: "BIC TB", num: true }],
          rows: gs.top.map(function (x) { return ["(" + x.order.join(",") + ")", fmt(x.avg_aic, 2), fmt(x.std_aic, 2), fmt(x.avg_bic, 2)]; }),
        };
      },
    });
    g2.appendChild(c3.card);
    plot(sid, c3.chart, function (P) {
      var bestKey = "(" + gs.best_order.join(",") + ")";
      var names = top.map(function (x) { return "(" + x.order.join(",") + ")"; });
      return {
        data: [{
          type: "scatter", mode: "markers", x: top.map(function (x) { return x.avg_aic; }), y: names,
          error_x: { type: "data", array: top.map(function (x) { return x.std_aic; }), color: P.muted, thickness: 1.5, width: 4 },
          marker: { size: 10, color: names.map(function (n) { return n === bestKey ? P.series[1] : P.series[0]; }) },
          hovertemplate: "%{y}: AIC %{x:.1f}<extra></extra>",
        }],
        layout: baseLayout(P, {
          height: 320,
          xaxis: axisStyle(P, { title: { text: "AIC trung bình (thấp hơn là tốt hơn)" } }),
          yaxis: axisStyle(P, { type: "category" }),
          annotations: [{ x: top[top.length - 1].avg_aic, y: bestKey, text: "tốt nhất", showarrow: false, xanchor: "left", xshift: 10, yshift: 10, font: { size: 11, color: P.ink2 } }],
        }),
      };
    });

    var cmp = D.forecast.compare_2xx;
    var rows = cmp.per_record.slice().sort(function (a, b) { return a[1] - b[1]; });
    var metric = "mae";
    var entry;
    var wins = cmp.per_record.filter(function (x) { return x[1] < x[4]; }).length;
    var c4 = chartCard({
      title: "ARIMA so với SARIMA trên " + rows.length + " record 2xx",
      sub: "ARIMA thắng " + wins + "/" + rows.length + " record. " + cmp.mode + " Trục log.",
      actions: [segmented([{ label: "MAE", value: "mae" }, { label: "RMSE", value: "rmse" }], metric, function (v) { metric = v; drawEntry(entry); })],
      table: function () {
        return {
          columns: [{ label: "Record" }, { label: "ARIMA MAE", num: true }, { label: "ARIMA RMSE", num: true }, { label: "SARIMA MAE", num: true }, { label: "SARIMA RMSE", num: true }, { label: "Tốt hơn" }],
          rows: cmp.per_record.map(function (x) { return [x[0], fmt(x[1], 2), fmt(x[3], 2), fmt(x[4], 2), fmt(x[6], 2), x[1] <= x[4] ? "ARIMA" : "SARIMA"]; }),
        };
      },
    });
    g2.appendChild(c4.card);
    body.appendChild(g2);
    entry = plot(sid, c4.chart, function (P) {
      var ia = metric === "mae" ? 1 : 3, is = metric === "mae" ? 4 : 6;
      var xs = [], ys = [];
      rows.forEach(function (x) { xs.push(x[ia], x[is], null); ys.push(x[0], x[0], null); });
      return {
        data: [
          { type: "scatter", mode: "lines", x: xs, y: ys, line: { color: P.axis, width: 2 }, hoverinfo: "skip", showlegend: false },
          { type: "scatter", mode: "markers", name: "ARIMA", x: rows.map(function (x) { return x[ia]; }), y: rows.map(function (x) { return x[0]; }), marker: { color: P.series[0], size: 9 }, hovertemplate: "%{y}: %{x:.2f}<extra>ARIMA</extra>" },
          { type: "scatter", mode: "markers", name: "SARIMA", x: rows.map(function (x) { return x[is]; }), y: rows.map(function (x) { return x[0]; }), marker: { color: P.series[1], size: 9 }, hovertemplate: "%{y}: %{x:.2f}<extra>SARIMA</extra>" },
        ],
        layout: baseLayout(P, {
          height: 560, showlegend: true, margin: { t: 30 },
          xaxis: axisStyle(P, { type: "log", title: { text: metric.toUpperCase() + " (bpm, log)" } }),
          yaxis: axisStyle(P, { type: "category", categoryorder: "array", categoryarray: rows.map(function (x) { return x[0]; }).reverse(), tickfont: { size: 11 } }),
        }),
      };
    });
  });

  // ---------- 06. Phân loại ----------
  registerSection("classification", "static", function (body, sid) {
    var C = D.classification;
    var st = stmemChosen();

    var g = el("div", { class: "grid-2" });
    ["ml", "cnn"].forEach(function (k) {
      var m = C.methods[k];
      var c = card(m.title);
      var ol = el("ol", { class: "steps" });
      m.steps.forEach(function (s) { ol.appendChild(el("li", { text: s })); });
      c.body.appendChild(ol);
      g.appendChild(c.card);
    });
    body.appendChild(g);

    // Bảng kết quả
    var models = C.models.slice();
    if (st) {
      models.push({
        id: "stmem_9s", family: "stmem", name: "ST-MEM Semi-finetune", window: "9s", window_seconds: 9, label_rule: "any_abnormal",
        accuracy: st.test.accuracy, precision: st.test.precision, recall: st.test.recall, f1: st.test.f1, auc: st.test.auc,
        specificity: st.test.specificity, confusion_matrix: st.test.confusion_matrix, source: "demo/train_stmem.py",
      });
    }
    var bestF1 = Math.max.apply(null, models.map(function (m) { return m.f1; }));
    var FAM = { ml: "Đặc trưng thủ công + cây (tốt nhất mỗi cửa sổ)", cnn: "1D CNN", stmem: "ST-MEM" };
    function modelLabel(m) {
      return m.family === "ml" ? m.name + " (đặc trưng thủ công)" : m.family === "stmem" ? "ST-MEM Semi-finetune" : m.name;
    }
    var rc = card("Kết quả trên tập test (5 record)", "Hàng tô màu: F1 cao nhất. Cột \"Quy tắc nhãn\" quyết định cửa sổ nào là Abnormal, nên chỉ so sánh trong cùng quy tắc.");
    var thead = el("tr");
    ["Mô hình", "Cửa sổ", "Quy tắc nhãn", "Accuracy", "Precision", "Recall", "Specificity", "F1", "AUC"].forEach(function (h, i) {
      thead.appendChild(el("th", { scope: "col", class: i >= 3 ? "num" : null, text: h }));
    });
    var tbody = el("tbody");
    models.forEach(function (m) {
      tbody.appendChild(el("tr", { class: m.f1 === bestF1 ? "is-best" : null },
        el("td", { text: modelLabel(m) }),
        el("td", { text: m.window }),
        el("td", { text: C.label_rules[m.label_rule].name }),
        el("td", { class: "num", text: fmt(m.accuracy, 3) }),
        el("td", { class: "num", text: fmt(m.precision, 3) }),
        el("td", { class: "num", text: fmt(m.recall, 3) }),
        el("td", { class: "num", text: fmt(m.specificity, 3) }),
        el("td", { class: "num", text: fmt(m.f1, 3) }),
        el("td", { class: "num", text: m.auc != null ? fmt(m.auc, 3) : "—" })));
    });
    rc.body.appendChild(el("div", { class: "table-wrap" }, el("table", { class: "data" }, el("thead", null, thead), tbody)));
    rc.body.appendChild(el("p", { class: "card-foot", text: "Mô hình đặc trưng thủ công và CNN 4.5 s / 9 s: số trong Final_Report_TS-3.pdf (Bảng 5.1, 5.2). CNN 0.75 s chỉ có trong notebook. Specificity và accuracy của CNN 9 s tính từ confusion matrix (accuracy 0.938; report ghi 0.9354, trùng với precision). ST-MEM Semi-finetune: chạy lại trong demo theo report (stride 4.5 s, ngưỡng 0.5), thấp hơn nhiều so với 0.9695 report công bố. Report không có AUC." }));
    body.appendChild(rc.card);

    // Mô hình đặc trưng thủ công: đủ 6 cấu hình của Bảng 5.1
    var mlAll = C.ml_all || [];
    if (mlAll.length) {
      var ac = card("Mô hình đặc trưng thủ công: cả sáu cấu hình",
        "Bảng 5.1 của report. Hàng tô màu là mô hình tốt nhất (F1) của mỗi cửa sổ. 9 s tốt hơn hẳn 4.5 s, khác với CNN.");
      var ah = el("tr");
      ["Mô hình", "Cửa sổ", "Accuracy", "Precision", "Recall", "F1", "TN", "FP", "FN", "TP", "Nguồn ma trận"].forEach(function (h, i) {
        ah.appendChild(el("th", { scope: "col", class: i >= 2 && i <= 9 ? "num" : null, text: h }));
      });
      var bestOf = {};
      mlAll.forEach(function (m) { if (!bestOf[m.window] || m.f1 > bestOf[m.window]) bestOf[m.window] = m.f1; });
      var ab = el("tbody");
      mlAll.forEach(function (m) {
        var cm = m.confusion_matrix;
        ab.appendChild(el("tr", { class: m.f1 === bestOf[m.window] ? "is-best" : null },
          el("td", { text: m.model }), el("td", { text: m.window }),
          el("td", { class: "num", text: fmt(m.accuracy, 3) }), el("td", { class: "num", text: fmt(m.precision, 3) }),
          el("td", { class: "num", text: fmt(m.recall, 3) }), el("td", { class: "num", text: fmt(m.f1, 3) }),
          el("td", { class: "num", text: fmt(cm[0][0]) }), el("td", { class: "num", text: fmt(cm[0][1]) }),
          el("td", { class: "num", text: fmt(cm[1][0]) }), el("td", { class: "num", text: fmt(cm[1][1]) }),
          el("td", { text: m.cm_source })));
      });
      ac.body.appendChild(el("div", { class: "table-wrap" }, el("table", { class: "data" }, el("thead", null, ah), ab)));
      ac.body.appendChild(el("p", { class: "card-foot", text: "Report chỉ in confusion matrix của XGBoost 4.5 s và Extra Trees 9 s (Hình 5.1). Bốn ma trận còn lại \"suy ra\" từ recall, precision và số cửa sổ mỗi lớp, và khớp lại cả accuracy, precision, recall, F1 của Bảng 5.1." }));
      body.appendChild(ac.card);
    }

    // Metric theo độ dài cửa sổ
    var metric = "f1";
    var entry;
    var mc = chartCard({
      title: "Metric theo độ dài cửa sổ",
      sub: "Đường nối các cấu hình cùng phương pháp.",
      actions: [segmented([{ label: "F1", value: "f1" }, { label: "Recall", value: "recall" }, { label: "Precision", value: "precision" }, { label: "Specificity", value: "specificity" }], metric, function (v) { metric = v; drawEntry(entry); })],
    });
    body.appendChild(mc.card);
    entry = plot(sid, mc.chart, function (P) {
      var slot = { ml: 0, cnn: 1, stmem: 6 };
      return {
        data: ["ml", "cnn", "stmem"].map(function (f) {
          var ms = models.filter(function (m) { return m.family === f; }).sort(function (a, b) { return a.window_seconds - b.window_seconds; });
          if (!ms.length) return null;
          return {
            type: "scatter", mode: "lines+markers+text", name: FAM[f],
            x: ms.map(function (m) { return m.window_seconds; }), y: ms.map(function (m) { return m[metric]; }),
            text: ms.map(function (m) { return fmt(m[metric], 3); }), textposition: f === "ml" ? "bottom center" : "top center", textfont: { size: 11, color: P.ink2 },
            line: { color: P.series[slot[f]], width: 2 }, marker: { color: P.series[slot[f]], size: 9 },
            hovertemplate: "%{x} s: %{y:.3f}<extra>" + FAM[f] + "</extra>",
          };
        }).filter(Boolean),
        layout: baseLayout(P, {
          height: 320, showlegend: true, margin: { t: 30 },
          xaxis: axisStyle(P, { title: { text: "Độ dài cửa sổ (s)" }, tickvals: [0.75, 4.5, 9], range: [0, 10] }),
          yaxis: axisStyle(P, { range: [0, 1.08], title: { text: metric } }),
        }),
      };
    });

    var cmc = card("Confusion matrix", "Hàng = nhãn thật, cột = dự đoán. Ô đậm hơn = tỉ lệ cao hơn trong hàng.");
    var cg = el("div", { class: "cm-grid" });
    models.forEach(function (m) {
      cg.appendChild(cmBlock(modelLabel(m) + " " + m.window, C.label_rules[m.label_rule].name, m.confusion_matrix));
    });
    cmc.body.appendChild(cg);
    body.appendChild(cmc.card);

    // Quy tắc gán nhãn
    var lx = D.label_examples;
    var rcards = el("div", { class: "rule-cards" });
    ["center_beat", "any_abnormal"].forEach(function (k) {
      var rule = C.label_rules[k];
      var cnt = lx.counts[k];
      rcards.appendChild(el("div", { class: "rule" },
        el("strong", { text: rule.name }),
        rule.rule + " Dùng cho: " + rule.used_by + ". Ở record " + lx.record + ": " + fmt(cnt["1"] || 0) + " Abnormal / " + fmt(cnt["0"] || 0) + " Normal."));
    });
    var lrc = card("Hai quy tắc gán nhãn cửa sổ", "Ví dụ ba cửa sổ " + lx.window_s + " s của record test " + lx.record + ". Vạch dọc: tâm cửa sổ; chấm: beat gần tâm nhất.");
    lrc.body.appendChild(rcards);
    var exBox = el("div", { class: "examples", style: "margin-top:16px" });
    lrc.body.appendChild(exBox);
    body.appendChild(lrc.card);
    lx.examples.forEach(function (ex) {
      var lbl = function (v) { return v ? "Abnormal" : "Normal"; };
      var box = el("div", { class: "example" },
        el("p", { class: "cm-title", text: ex.title }),
        el("p", { class: "cm-sub", text: "Gần tâm: " + lbl(ex.center_label) + " · Có beat bất thường: " + lbl(ex.any_label) }));
      var div = el("div", { class: "chart", role: "img", "aria-label": ex.title });
      box.appendChild(div);
      exBox.appendChild(box);
      var y = decode(ex.signal, lx.scale);
      var x = range(y.length, function (i) { return i / lx.fs; });
      plot(sid, div, function (P) {
        var ymax = Math.max.apply(null, y), ymin = Math.min.apply(null, y);
        var beats = ex.annotations.filter(function (a) { return isBeat(a[1]); });
        var center = ex.annotations.filter(function (a) { return a[0] === ex.center_beat_offset; })[0];
        return {
          data: [
            { type: "scatter", mode: "lines", x: x, y: y, line: { color: P.ink, width: 1 }, hoverinfo: "skip" },
            {
              type: "scatter", mode: "text", x: beats.map(function (a) { return a[0] / lx.fs; }), y: beats.map(function () { return ymax + (ymax - ymin) * 0.12; }),
              text: beats.map(function (a) { return a[1]; }), textfont: { size: 12, color: beats.map(function (a) { return a[1] === "N" ? P.ink2 : P.series[1]; }) },
              hovertemplate: "%{text}<extra></extra>", cliponaxis: false,
            },
            center ? { type: "scatter", mode: "markers", x: [center[0] / lx.fs], y: [ymax + (ymax - ymin) * 0.27], marker: { size: 7, color: P.accent }, hoverinfo: "skip", cliponaxis: false } : null,
          ].filter(Boolean),
          layout: baseLayout(P, {
            height: 190, margin: { l: 8, r: 8, t: 22, b: 30 },
            shapes: [{ type: "line", x0: lx.window_s / 2, x1: lx.window_s / 2, yref: "paper", y0: 0, y1: 1, line: { color: P.accent, width: 1, dash: "dot" } }],
            xaxis: axisStyle(P, { title: { text: "" }, fixedrange: true, ticksuffix: " s" }),
            yaxis: axisStyle(P, { showticklabels: false, fixedrange: true, range: [ymin - (ymax - ymin) * 0.05, ymax + (ymax - ymin) * 0.35] }),
          }),
        };
      });
    });
  });

  // ---------- 07. ST-MEM ----------
  registerSection("stmem", "static", function (body, sid) {
    var S = D.stmem;
    var R = S.results;
    var info = card("Cách làm (theo report)", S.paper);
    var e0 = S.experiments[0];
    info.body.appendChild(kv([
      ["Dữ liệu", "MIT-BIH Arrhythmia Database đọc bằng WFDB, 2 lead, chia theo record (test 102–106, val 200/208/232/233/234)"],
      ["Encoder", S.encoder + ". Dùng checkpoint pretrained có sẵn của bài báo, không tự pretrain."],
      ["Đầu vào", S.input + (R ? ", cửa sổ trượt stride " + R.config.stride_s + " s" : "")],
      ["Fine-tune", "Semi-finetune: chỉ train lead embedding của 2 lead MIT-BIH và classifier head; patch embedding, positional embedding và 12 khối Transformer giữ nguyên trọng số pretrained (đóng băng)"],
      R ? ["Huấn luyện", "Batch " + R.config.batch_size + ", tối đa " + R.config.max_epochs + " epoch, dừng sớm sau " + R.config.patience + " epoch, lr head " + R.config.lr_head + ", lr lead " + R.config.lr_lead_emb + ", ngưỡng " + R.threshold + " · " + R.device] : null,
      R ? ["Số cửa sổ", "train " + fmt(R.split.train.normal + R.split.train.abnormal) + " (" + fmt(R.split.train.normal) + " N / " + fmt(R.split.train.abnormal) + " A) · val " + fmt(R.split.val.normal + R.split.val.abnormal) + " · test " + fmt(R.split.test.normal + R.split.test.abnormal) + " (" + fmt(R.split.test.normal) + " N / " + fmt(R.split.test.abnormal) + " A)"] : null,
      ["Trạng thái", S.status_text],
    ]));
    body.appendChild(info.card);
    if (!R) return;

    var chosen = stmemChosen();
    var ce = chosen.exp;
    var cnn9 = D.classification.models.filter(function (m) { return m.id === "cnn_9s"; })[0];
    body.appendChild(el("div", { class: "mini-tiles" },
      miniTile("F1 test", fmt(chosen.test.f1, 3), "Semi-finetune · ngưỡng " + R.threshold),
      miniTile("AUC test", fmt(chosen.test.auc, 3), fmt(ce.trainable_params) + " tham số được train"),
      miniTile("Recall", fmt(chosen.test.recall, 3), "bắt được cửa sổ bất thường"),
      miniTile("Specificity", fmt(chosen.test.specificity, 3), "đúng ở cửa sổ bình thường"),
      ce.report ? miniTile("Report công bố", "F1 " + fmt(ce.report.f1, 3), "Bảng 5.3, Semi-finetune") : null,
      miniTile("1D CNN 9 s", "F1 " + fmt(cnn9.f1, 3), "cùng quy tắc nhãn, cùng record test")));

    var tc = card("Semi-finetune: chạy lại so với report",
      "Tập test (record 102–106), ngưỡng 0.5, model tốt nhất theo val loss. Đây là model dùng cho màn hình theo dõi.");
    var thead = el("tr");
    ["Cách fine-tune", "Tham số train", "Epoch tốt nhất / chạy", "Accuracy", "Precision", "Recall", "F1", "AUC", "F1 report"].forEach(function (h, i) {
      thead.appendChild(el("th", { scope: "col", class: i >= 1 ? "num" : null, text: h }));
    });
    var tbody = el("tbody");
    R.experiments.forEach(function (e) {
      tbody.appendChild(el("tr", { class: e.experiment === R.chosen_experiment ? "is-best" : null },
        el("td", { text: e.name }),
        el("td", { class: "num", text: fmt(e.trainable_params) }),
        el("td", { class: "num", text: e.best_epoch + " / " + e.epochs_run }),
        el("td", { class: "num", text: fmt(e.test.accuracy, 3) }),
        el("td", { class: "num", text: fmt(e.test.precision, 3) }),
        el("td", { class: "num", text: fmt(e.test.recall, 3) }),
        el("td", { class: "num", text: fmt(e.test.f1, 3) }),
        el("td", { class: "num", text: fmt(e.test.auc, 3) }),
        el("td", { class: "num", text: e.report ? fmt(e.report.f1, 3) : "—" })));
    });
    tc.body.appendChild(el("div", { class: "table-wrap" }, el("table", { class: "data" }, el("thead", null, thead), tbody)));
    var semi = R.experiments.filter(function (e) { return e.experiment === 2; })[0];
    if (semi && semi.report) {
      tc.body.appendChild(el("p", { class: "card-foot", text:
        "Report: Semi-finetune đạt accuracy " + fmt(semi.report.accuracy, 4) + " / F1 " + fmt(semi.report.f1, 4) + ". Chạy lại đúng như mô tả (chỉ train lead embedding của 2 lead + head) được F1 " + fmt(semi.test.f1, 3) +
        ". Chưa tái hiện được con số của report, vì report không ghi epoch, learning rate, batch hay seed, và không còn log của lần chạy gốc." }));
    }
    body.appendChild(tc.card);

    var g = el("div", { class: "grid-2" });
    var lc = chartCard({ title: "Đường huấn luyện", sub: "Loss train (nét liền) và val (nét đứt) theo epoch." });
    g.appendChild(lc.card);
    plot(sid, lc.chart, function (P) {
      var data = [];
      R.experiments.forEach(function (e, i) {
        var col = P.series[i === 0 ? 0 : 1];
        var nm = e.experiment === 1 ? "Linear probe" : "Semi-finetune";
        var ep = e.history.map(function (h) { return h.epoch; });
        data.push({ type: "scatter", mode: "lines", name: nm + " train", x: ep, y: e.history.map(function (h) { return h.train_loss; }), line: { color: col, width: 2 } });
        data.push({ type: "scatter", mode: "lines", name: nm + " val", x: ep, y: e.history.map(function (h) { return h.val_loss; }), line: { color: col, width: 2, dash: "dash" } });
      });
      return { data: data, layout: baseLayout(P, { height: 300, showlegend: true, margin: { t: 30 }, hovermode: "x unified", xaxis: axisStyle(P, { title: { text: "Epoch" } }), yaxis: axisStyle(P, { title: { text: "BCE loss" } }) }) };
    });

    if (R.roc_test) {
      var roc = chartCard({ title: "ROC trên tập test · Semi-finetune", sub: "Chấm: điểm làm việc ở ngưỡng " + R.threshold + "." });
      g.appendChild(roc.card);
      plot(sid, roc.chart, function (P) {
        return {
          data: [
            { type: "scatter", mode: "lines", x: R.roc_test.fpr, y: R.roc_test.tpr, name: "ROC (AUC " + fmt(chosen.test.auc, 3) + ")", line: { color: P.ink, width: 2 }, hovertemplate: "FPR %{x:.2f}, TPR %{y:.2f}<extra></extra>" },
            { type: "scatter", mode: "lines", x: [0, 1], y: [0, 1], line: { color: P.axis, dash: "dot", width: 1 }, hoverinfo: "skip", showlegend: false },
            { type: "scatter", mode: "markers", name: "Ngưỡng " + R.threshold, x: [1 - chosen.test.specificity], y: [chosen.test.recall], marker: { color: P.series[1], size: 11, line: { color: P.surface, width: 2 } }, hovertemplate: "FPR %{x:.2f}, TPR %{y:.2f}<extra></extra>" },
          ],
          layout: baseLayout(P, {
            height: 300, showlegend: true, margin: { t: 30 },
            xaxis: axisStyle(P, { title: { text: "FPR (1 − specificity)" }, range: [0, 1] }),
            yaxis: axisStyle(P, { title: { text: "TPR (recall)" }, range: [0, 1.02] }),
          }),
        };
      });
    }
    body.appendChild(g);

    var cmc = card("Confusion matrix trên tập test · Semi-finetune", "Ngưỡng " + R.threshold + ". Hàng = nhãn thật, cột = dự đoán.");
    var cg = el("div", { class: "cm-grid" });
    R.experiments.forEach(function (e) {
      if (e.test.confusion_matrix) cg.appendChild(cmBlock(e.experiment === 1 ? "Linear probe" : "Semi-finetune", fmt(e.trainable_params) + " tham số train", e.test.confusion_matrix));
    });
    cmc.body.appendChild(cg);
    body.appendChild(cmc.card);

    var pr = R.per_record;
    var prc = chartCard({
      title: "Độ chính xác theo record · Semi-finetune",
      sub: "Các cửa sổ 9 s không chồng lấn của từng record test/val (dùng cho màn hình theo dõi), ngưỡng " + R.threshold + ".",
      table: function () {
        return {
          columns: [{ label: "Record" }, { label: "Tập" }, { label: "Cửa sổ", num: true }, { label: "Thật bất thường", num: true }, { label: "Dự đoán bất thường", num: true }, { label: "Accuracy", num: true }],
          rows: pr.map(function (x) { return [x.record, SPLIT_LABEL[x.split], fmt(x.windows), fmt(x.truth_abnormal), fmt(x.pred_abnormal), fmt(x.accuracy, 3)]; }),
        };
      },
    });
    body.appendChild(prc.card);
    plot(sid, prc.chart, function (P) {
      return {
        data: ["test", "val"].map(function (sp) {
          var xs = pr.filter(function (x) { return x.split === sp; });
          return {
            type: "bar", name: SPLIT_LABEL[sp], x: xs.map(function (x) { return x.record; }), y: xs.map(function (x) { return x.accuracy; }),
            marker: { color: P.series[sp === "test" ? 6 : 2] },
            text: xs.map(function (x) { return fmt(x.accuracy * 100, 0) + "%"; }), textposition: "outside", textfont: { size: 11, color: P.ink2 },
            hovertemplate: "Record %{x}: %{y:.3f}<extra>" + SPLIT_LABEL[sp] + "</extra>", cliponaxis: false,
          };
        }),
        layout: baseLayout(P, {
          height: 320, showlegend: true, margin: { t: 30 },
          xaxis: axisStyle(P, { type: "category", title: { text: "Record" } }),
          yaxis: axisStyle(P, { range: [0, 1.1], tickformat: ".0%" }),
        }),
      };
    });

    body.appendChild(el("p", { class: "card-foot" },
      "Xác suất của model Semi-finetune được phát theo thời gian trên ",
      el("a", { href: "monitor.html", text: "màn hình theo dõi" }),
      ", cùng với cảnh báo theo luật nhịp."));
  });

  // ======================================================================
  // Khởi động
  // ======================================================================

  function showBanner(msg) {
    var b = document.getElementById("banner");
    b.textContent = msg;
    b.hidden = false;
  }

  function init() {
    setupTheme();
    if (!D) {
      showBanner("Không tìm thấy dữ liệu demo (data/demo_data.js). Hãy chạy: python demo/build_data.py");
      return;
    }
    if (!HAS_PLOTLY) {
      showBanner("Không tải được thư viện biểu đồ (vendor/plotly-cartesian-2.35.2.min.js). Các biểu đồ sẽ không hiển thị.");
    }
    document.getElementById("footer-meta").textContent =
      "Dữ liệu demo tạo lúc " + D.meta.generated_at.replace("T", " ") + " bởi " + D.meta.generator + ".";
    setupRecordControls();
    setupNav();
    renderSections();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
