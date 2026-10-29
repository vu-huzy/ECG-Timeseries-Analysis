/* Màn hình theo dõi nhịp tim — phát lại ECG như thời gian thực.
   Dữ liệu: window.MONITOR_DATA (demo/build_monitor.py). Mọi cảnh báo đã được tính trước
   chỉ từ dữ liệu quá khứ của mỗi thời điểm; trang chỉ "phát" chúng theo đồng hồ. */
(function () {
  "use strict";

  const D = window.MONITOR_DATA;
  const $ = (id) => document.getElementById(id);

  const SEV_RANK = { critical: 3, serious: 2, warning: 1 };
  const TRANSIENT_S = { pvc: 3, pause: 6, stmem: 9 };   // thời gian giữ cảnh báo tức thời trên băng
  const STATE_TYPES = ["tachy", "brady", "irregular"];
  const GROUP_S = 10;                                   // gộp cảnh báo cùng loại trong 10 s ("×N")
  const SPEEDS = [1, 2, 4];

  const RULES = {};
  (D && D.rules || []).forEach((r) => { RULES[r.type] = r; });

  function storeGet(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
  function storeSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* bỏ qua */ } }

  function el(tag, attrs, children) {
    const n = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      if (k === "class") n.className = attrs[k];
      else if (k === "text") n.textContent = attrs[k];
      else if (k === "style") n.style.cssText = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    (children || []).forEach((c) => { if (c != null) n.append(c); });
    return n;
  }
  const mmss = (s) => {
    s = Math.max(0, Math.floor(s));
    return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
  };
  const fmt2 = (x) => Number(x).toFixed(2);
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  if (!D || !D.records || !D.records.length) {
    document.querySelector(".m-banner-text").textContent =
      "Chưa có dữ liệu. Chạy: python demo/build_monitor.py";
    return;
  }

  /* ------------------------------------------------------------------ trạng thái */
  const S = {
    rec: null, sig: null, fs: D.meta.fs, dur: 0, win: D.meta.window_s,
    t: 0, playing: true, speed: 1,
    beatPtr: 0, evPtr: 0, lastBeat: null, prevBeat: null,
    log: [], states: {}, transients: [], pvcCount: 0, pauseCount: 0,
    shownWindow: -2, bannerKey: "", beep: false, audio: null,
    lastFrame: 0, lastClock: -1, lastTrend: 0,
  };

  /* ------------------------------------------------------------------ điều khiển */
  const recSel = $("m-record");
  D.records.forEach((r) => {
    recSel.append(el("option", { value: r.id, text: `${r.id} · ${r.description}` }));
  });
  recSel.addEventListener("change", () => loadRecord(recSel.value));

  const speedBox = $("m-speed");
  SPEEDS.forEach((sp) => {
    const b = el("button", { type: "button", "aria-pressed": "false", text: sp + "×", "data-speed": sp });
    b.addEventListener("click", () => setSpeed(sp));
    speedBox.append(b);
  });
  function setSpeed(sp) {
    S.speed = sp;
    storeSet("ecg-monitor-speed", String(sp));
    speedBox.querySelectorAll("button").forEach((b) =>
      b.setAttribute("aria-pressed", String(Number(b.dataset.speed) === sp)));
  }

  const ICON_PAUSE = '<path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" fill="currentColor"/>';
  const ICON_PLAY = '<path d="M7 4.5v15l12-7.5z" fill="currentColor"/>';
  function setPlaying(p) {
    S.playing = p;
    $("m-play-icon").innerHTML = p ? ICON_PAUSE : ICON_PLAY;
    $("m-play-text").textContent = p ? "Tạm dừng" : "Phát";
    $("m-play").setAttribute("aria-label", (p ? "Tạm dừng" : "Phát") + " (phím cách)");
    S.lastFrame = performance.now();
    if (!p) updateBanner(true);
  }
  $("m-play").addEventListener("click", () => setPlaying(!S.playing));

  $("m-beep").addEventListener("click", () => {
    S.beep = !S.beep;
    $("m-beep").setAttribute("aria-pressed", String(S.beep));
    if (S.beep && !S.audio) {
      try { S.audio = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { S.audio = null; }
    }
    if (S.audio && S.audio.state === "suspended") S.audio.resume();
  });
  function beep(isPvc) {
    if (!S.beep || !S.audio) return;
    const ctx = S.audio, o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.value = isPvc ? 660 : 990;
    g.gain.setValueAtTime(0.0001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.12, ctx.currentTime + 0.005);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.07);
    o.connect(g).connect(ctx.destination);
    o.start(); o.stop(ctx.currentTime + 0.08);
  }

  const annBox = $("m-show-ann");
  annBox.checked = storeGet("ecg-monitor-ann", "1") === "1";
  annBox.addEventListener("change", () => storeSet("ecg-monitor-ann", annBox.checked ? "1" : "0"));

  document.addEventListener("keydown", (e) => {
    const tag = (e.target.tagName || "").toLowerCase();
    if (tag === "select" || tag === "input" || tag === "textarea") return;
    if (e.code === "Space" && tag !== "button" && tag !== "summary") {
      e.preventDefault(); setPlaying(!S.playing);
    } else if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault(); seek(S.t + (e.key === "ArrowLeft" ? -S.win : S.win));
    }
  });

  /* ------------------------------------------------------------------ nạp bản ghi */
  function loadRecord(id) {
    const rec = D.records.find((r) => r.id === id) || D.records[0];
    S.rec = rec;
    recSel.value = rec.id;
    storeSet("ecg-monitor-record", rec.id);
    const sc = rec.scale || 1000;
    S.sig = Float32Array.from(rec.signal, (v) => v / sc);
    S.fs = rec.fs;
    S.dur = rec.signal.length / rec.fs;
    S.beatT = rec.beats.map((b) => b[0] / rec.fs);
    $("m-lead").textContent = rec.lead + " · " + rec.fs + " Hz";
    $("m-desc").textContent =
      `Bản ghi ${rec.id} (tập ${rec.split}) — ${rec.description}. Đoạn phát: giây ${Math.round(rec.start_s)}–${Math.round(rec.start_s + rec.duration_s)} của bản ghi gốc, lặp lại khi hết.`;
    prepTrend();
    seek(0);
  }

  /* ------------------------------------------------------------------ xử lý sự kiện */
  function resetState() {
    S.beatPtr = 0; S.evPtr = 0; S.lastBeat = null; S.prevBeat = null;
    S.log = []; S.states = {}; S.transients = []; S.pvcCount = 0; S.pauseCount = 0;
    S.shownWindow = -2; S.bannerKey = "";
  }

  function seek(t) {
    const rec = S.rec;
    t = Math.min(Math.max(0, t), S.dur - 0.001);
    resetState();
    S.t = 0;
    advance(t, true);
    renderLog(); renderModel(true); updateHr(); updateBanner(true);
  }

  function advance(t1, silent) {
    const rec = S.rec, beats = rec.beats, evs = rec.events;
    while (S.beatPtr < beats.length && S.beatT[S.beatPtr] <= t1) {
      const b = beats[S.beatPtr];
      S.prevBeat = S.lastBeat;
      S.lastBeat = { t: S.beatT[S.beatPtr], hr: b[1], pvc: b[2] === 1 };
      if (!silent) { pulse(S.lastBeat.pvc); beep(S.lastBeat.pvc); }
      S.beatPtr++;
    }
    let logChanged = false;
    while (S.evPtr < evs.length && evs[S.evPtr].t <= t1) {
      handleEvent(evs[S.evPtr]);
      S.evPtr++;
      logChanged = true;
    }
    S.t = t1;
    S.transients = S.transients.filter((x) => x.until > t1);
    if (logChanged && !silent) renderLog();
    return logChanged;
  }

  function handleEvent(e) {
    const base = e.type.replace(/_end$/, "");
    const isEnd = e.type.endsWith("_end");
    if (STATE_TYPES.includes(base)) {
      if (isEnd) delete S.states[base];
      else S.states[base] = { t: e.t, value: e.value };
    } else {
      S.transients.push({ type: e.type, t: e.t, value: e.value, until: e.t + (TRANSIENT_S[e.type] || 4) });
      if (e.type === "pvc") S.pvcCount++;
      if (e.type === "pause") S.pauseCount++;
    }
    const prev = S.log.find((x) => x.type === e.type);
    if (prev && e.t - prev.lastT <= GROUP_S && !STATE_TYPES.includes(e.type)) {
      prev.n++; prev.lastT = e.t; prev.value = e.value;
    } else {
      S.log.unshift({ type: e.type, t: e.t, lastT: e.t, value: e.value, n: 1, window: e.window });
      if (S.log.length > 200) S.log.pop();
    }
  }

  function describe(type, value) {
    switch (type) {
      case "pvc": return { title: "Beat sớm kiểu PVC", detail: value ? `nhịp tức thời ~${value} bpm` : "" };
      case "pause": return { title: "Ngưng nhịp", detail: `RR ${fmt2(value)} s` };
      case "tachy": return { title: "Nhịp nhanh", detail: `${value} bpm` };
      case "brady": return { title: "Nhịp chậm", detail: `${value} bpm` };
      case "irregular": return { title: "Nhịp không đều", detail: `RMSSD ${value} ms` };
      case "stmem": return { title: "ST-MEM: đoạn 9 s bất thường", detail: `p = ${fmt2(value)}` };
      case "tachy_end": return { title: "Hết nhịp nhanh", detail: `${value} bpm` };
      case "brady_end": return { title: "Hết nhịp chậm", detail: `${value} bpm` };
      case "irregular_end": return { title: "Nhịp đều trở lại", detail: `RMSSD ${value} ms` };
      default: return { title: type, detail: String(value) };
    }
  }
  const sevOf = (type) => (RULES[type] && RULES[type].severity) || "warning";

  /* ------------------------------------------------------------------ băng cảnh báo */
  const ICONS = {
    ok: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor" opacity=".25"/><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    warning: '<svg viewBox="0 0 24 24"><path d="M12 3L2 20h20L12 3z" fill="currentColor" opacity=".25"/><path d="M12 9v5M12 17.2v.1" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    serious: '<svg viewBox="0 0 24 24"><path d="M12 3L2 20h20L12 3z" fill="currentColor" opacity=".35"/><path d="M12 9v5M12 17.2v.1" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    critical: '<svg viewBox="0 0 24 24"><path d="M8 2.5h8L21.5 8v8L16 21.5H8L2.5 16V8z" fill="currentColor" opacity=".35"/><path d="M12 7v6.5M12 16.8v.1" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>',
    pause: '<svg viewBox="0 0 24 24"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" fill="currentColor"/></svg>',
  };

  function updateBanner(force) {
    const items = [];
    Object.keys(S.states).forEach((k) => items.push({ type: k, t: S.states[k].t, value: S.states[k].value }));
    S.transients.forEach((x) => items.push(x));
    items.sort((a, b) => (SEV_RANK[sevOf(b.type)] - SEV_RANK[sevOf(a.type)]) || (b.t - a.t));
    let cls, icon, text, more = "";
    if (!S.playing) {
      cls = "is-idle"; icon = ICONS.pause; text = "Đã tạm dừng";
      if (items.length) more = `${items.length} cảnh báo đang hiện`;
    } else if (!items.length) {
      cls = "is-ok"; icon = ICONS.ok; text = "Không có cảnh báo";
    } else {
      const top = items[0], sev = sevOf(top.type), d = describe(top.type, top.value);
      cls = "is-" + sev; icon = ICONS[sev];
      text = d.title + (d.detail ? " · " + d.detail : "");
      if (items.length > 1) more = `+${items.length - 1} cảnh báo khác`;
    }
    const key = cls + "|" + text + "|" + more;
    if (!force && key === S.bannerKey) return;
    S.bannerKey = key;
    const b = $("m-banner");
    b.className = "m-banner " + cls;
    b.querySelector(".m-banner-icon").innerHTML = icon;
    b.querySelector(".m-banner-text").textContent = text;
    b.querySelector(".m-banner-more").textContent = more;
  }

  /* ------------------------------------------------------------------ nhật ký */
  function renderLog() {
    const ol = $("m-log");
    ol.textContent = "";
    if (!S.log.length) {
      ol.append(el("li", { class: "m-log-empty", text: "Chưa có cảnh báo." }));
    }
    S.log.slice(0, 80).forEach((x) => {
      const isEnd = x.type.endsWith("_end");
      const d = describe(x.type, x.value);
      ol.append(el("li", null, [
        el("time", { text: mmss(x.t) }),
        el("span", { class: "dot " + (isEnd ? "sev-ok" : "sev-" + sevOf(x.type)), "aria-hidden": "true" }),
        el("span", { class: isEnd ? "is-end" : "" , text: d.title + (d.detail ? " · " + d.detail : "") }),
        el("span", { class: "n", text: x.n > 1 ? "×" + x.n : "" }),
      ]));
    });
    const total = S.log.reduce((a, x) => a + (x.type.endsWith("_end") ? 0 : x.n), 0);
    $("m-log-count").textContent = total ? `${total} sự kiện` : "";
  }

  /* ------------------------------------------------------------------ HR + tim đập */
  let pulseTimer = 0;
  function pulse(isPvc) {
    const h = $("m-beat");
    h.classList.toggle("is-pvc", isPvc);
    h.classList.add("is-on");
    clearTimeout(pulseTimer);
    pulseTimer = setTimeout(() => h.classList.remove("is-on"), 110);
  }
  function updateHr() {
    const lb = S.lastBeat;
    const hrEl = $("m-hr");
    hrEl.textContent = lb && lb.hr != null ? lb.hr : "--";
    const gap = lb ? S.t - lb.t : 0;
    hrEl.classList.toggle("is-alarm", !!(S.states.tachy || S.states.brady || gap > 2));
    $("m-rr").textContent = lb && S.prevBeat ? Math.round((lb.t - S.prevBeat.t) * 1000) : "--";
    $("m-pvc").textContent = S.pvcCount;
    $("m-pause").textContent = S.pauseCount;
    // RMSSD của 20 RR gần nhất (giống luật "nhịp không đều")
    const n = S.beatPtr, bt = S.beatT;
    if (n >= 22) {
      let acc = 0;
      for (let i = n - 20; i < n; i++) {
        const d = (bt[i] - bt[i - 1]) - (bt[i - 1] - bt[i - 2]);
        acc += d * d;
      }
      $("m-rmssd").textContent = Math.round(Math.sqrt(acc / 20) * 1000);
    } else $("m-rmssd").textContent = "--";
  }

  /* ------------------------------------------------------------------ ST-MEM */
  const truthText = (v) => v === 1 ? "Bất thường" : v === 0 ? "Bình thường" : "Không có nhãn beat";
  function countsText(c) {
    const parts = Object.keys(c || {}).map((k) => `${k}×${c[k]}`);
    return parts.length ? parts.join(", ") : "—";
  }
  function renderModel(force) {
    const k = Math.floor(S.t / S.win) - 1;   // cửa sổ 9 s gần nhất đã thu xong
    if (!force && k === S.shownWindow) {
      if (k < 0) $("m-progress-t") && ($("m-progress-t").textContent = (S.t % S.win).toFixed(1));
      return;
    }
    S.shownWindow = k;
    const body = $("m-model-body");
    body.textContent = "";
    const model = D.model;
    $("m-model-sub").textContent = model ? `cửa sổ ${S.win} s · ngưỡng ${fmt2(model.threshold)}` : `cửa sổ ${S.win} s`;
    if (k < 0) {
      body.append(el("p", { class: "m-progress" }, [
        "Đang thu cửa sổ 9 s đầu tiên: ", el("span", { id: "m-progress-t", text: (S.t % S.win).toFixed(1) }), " / 9 s",
      ]));
    } else {
      const w = S.rec.windows[k];
      const head = el("p", { class: "m-dim", style: "margin:0 0 4px;font-size:12px",
        text: `Cửa sổ ${k + 1}/${S.rec.windows.length} · ${mmss(k * S.win)}–${mmss((k + 1) * S.win)}` });
      body.append(head);
      if (model && w.p != null) {
        const abn = w.p >= model.threshold;
        body.append(el("div", { class: "m-verdict " + (abn ? "is-abn" : "is-norm") }, [
          abn ? "Bất thường" : "Bình thường", el("small", { text: `p = ${fmt2(w.p)}` }),
        ]));
        const bar = el("div", { class: "m-pbar", role: "img", "aria-label": `Xác suất bất thường ${fmt2(w.p)}, ngưỡng ${fmt2(model.threshold)}` }, [
          el("div", { class: "m-pbar-fill" + (abn ? " is-abn" : ""), style: `width:${(w.p * 100).toFixed(1)}%` }),
          el("div", { class: "m-pbar-thr", style: `left:calc(${model.threshold * 100}% - 1px)` }),
        ]);
        body.append(bar, el("div", { class: "m-pbar-scale" }, [el("span", { text: "0" }), el("span", { text: "ngưỡng " + fmt2(model.threshold) }), el("span", { text: "1" })]));
        const truth = el("p", { class: "m-truth" }, [
          "Chuyên gia: ", el("b", { text: truthText(w.truth) }), ` (${countsText(w.counts)})`,
        ]);
        if (w.truth != null) {
          const ok = (w.truth === 1) === abn;
          truth.append(el("span", { class: "m-agree " + (ok ? "is-yes" : "is-no"), text: ok ? "✓ khớp" : "✗ lệch" }));
        }
        body.append(truth);
      } else {
        body.append(el("p", { class: "m-progress", text: "Chưa có kết quả ST-MEM — chạy demo/train_stmem.py rồi demo/build_monitor.py." }));
        body.append(el("p", { class: "m-truth" }, ["Chuyên gia: ", el("b", { text: truthText(w.truth) }), ` (${countsText(w.counts)})`]));
      }
    }
    if (model) {
      const te = model.test || {};
      body.append(el("p", { class: "m-model-meta",
        text: `${model.name}, thử nghiệm ${model.experiment} (${model.experiment_text}). Tập test: F1 ${fmt2(te.f1)}, AUC ${fmt2(te.auc)}. Xác suất tính trước, phát theo thời gian.` }));
    }
  }

  /* ------------------------------------------------------------------ xu hướng (HR / RR / ST-MEM) */
  // Ba biểu đồ xếp chồng, chung trục thời gian của cả đoạn phát; phần sau đầu phát vẽ mờ.
  const trendCanvas = $("m-trend"), tctx = trendCanvas.getContext("2d");
  const trendWrap = $("m-trend-wrap");
  const poinCanvas = $("m-poincare"), pctx = poinCanvas.getContext("2d");
  const T = { W: 0, H: 0, PW: 0, PH: 0, rr: null, hrLo: 40, hrHi: 130, rrHi: 2, bands: [], pauses: [] };
  const TM = { l: 46, r: 12, t: 4, b: 20 };

  function prepTrend() {
    const rec = S.rec, bt = S.beatT;
    T.rr = new Float32Array(bt.length);
    let rrMax = 1.6, hrMin = 1e9, hrMax = -1e9;
    for (let i = 1; i < bt.length; i++) {
      T.rr[i] = bt[i] - bt[i - 1];
      rrMax = Math.max(rrMax, Math.min(4, T.rr[i]));
    }
    rec.beats.forEach((b) => { if (b[1] != null) { hrMin = Math.min(hrMin, b[1]); hrMax = Math.max(hrMax, b[1]); } });
    T.hrLo = Math.max(0, Math.min(40, Math.floor((hrMin - 5) / 10) * 10));
    T.hrHi = Math.min(240, Math.max(130, Math.ceil((hrMax + 5) / 10) * 10));
    T.rrHi = Math.ceil(rrMax * 2) / 2;
    // Khoảng thời gian có cảnh báo trạng thái (tô nền)
    T.bands = []; T.pauses = [];
    const open = {};
    rec.events.forEach((e) => {
      const base = e.type.replace(/_end$/, "");
      if (STATE_TYPES.includes(base)) {
        if (e.type.endsWith("_end")) {
          if (open[base] != null) { T.bands.push({ type: base, a: open[base], b: e.t }); delete open[base]; }
        } else open[base] = e.t;
      } else if (e.type === "pause") T.pauses.push(e);
    });
    Object.keys(open).forEach((k) => T.bands.push({ type: k, a: open[k], b: S.dur }));
  }

  function sizeCanvas(cv, cx, wrap) {
    const r = wrap.getBoundingClientRect();
    const w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
    cv.width = Math.round(w * DPR); cv.height = Math.round(h * DPR);
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    return [w, h];
  }
  function resizeTrend() {
    [T.W, T.H] = sizeCanvas(trendCanvas, tctx, trendWrap);
    [T.PW, T.PH] = sizeCanvas(poinCanvas, pctx, poinCanvas.parentElement);
  }

  function drawTrend() {
    const rec = S.rec, c = tctx, W = T.W, H = T.H, t = S.t;
    c.clearRect(0, 0, W, H);
    const x0 = TM.l, x1 = W - TM.r, pw = x1 - x0;
    const xOf = (s) => x0 + (s / S.dur) * pw;
    const gap = 16, inner = H - TM.t - TM.b - 2 * gap;
    const panels = [{ h: inner * 0.40 }, { h: inner * 0.36 }, { h: inner * 0.24 }];
    let y = TM.t;
    panels.forEach((p) => { p.y0 = y; p.y1 = y + p.h; y = p.y1 + gap; });
    const ink2 = css("--ink-2"), muted = css("--muted"), hrC = css("--hr"), warn = css("--warning"),
      crit = css("--critical"), serious = css("--serious"), grid = "rgba(255,255,255,0.07)";
    const mono = css("--mono"), font = css("--font");

    function frameP(p, ticks, yOf, fmtTick, title) {
      c.strokeStyle = grid; c.lineWidth = 1; c.fillStyle = muted; c.font = "10px " + mono; c.textAlign = "right";
      ticks.forEach((v) => {
        const yy = Math.round(yOf(v)) + 0.5;
        c.beginPath(); c.moveTo(x0, yy); c.lineTo(x1, yy); c.stroke();
        c.fillText(fmtTick(v), x0 - 6, yy + 3);
      });
      titles.push([title, p]);
    }
    function drawTitles() {
      c.textAlign = "left"; c.font = "600 11px " + font;
      titles.forEach(function (tp) {
        const w = c.measureText(tp[0]).width;
        c.fillStyle = "rgba(5,6,5,0.82)"; c.fillRect(x0 + 2, tp[1].y0 + 1, w + 8, 15);
        c.fillStyle = ink2; c.fillText(tp[0], x0 + 6, tp[1].y0 + 12);
      });
    }
    const titles = [];
    function band(p, a, b, color) {
      const xa = xOf(a), xb = xOf(Math.min(b, S.dur));
      c.fillStyle = color; c.fillRect(xa, p.y0, Math.max(2, xb - xa), p.h);
    }

    // --- HR ---
    const P1 = panels[0];
    const hrY = (v) => P1.y1 - (Math.max(T.hrLo, Math.min(T.hrHi, v)) - T.hrLo) / (T.hrHi - T.hrLo) * P1.h;
    T.bands.forEach((bd) => { if (bd.type !== "irregular" && bd.a <= t) band(P1, bd.a, Math.min(bd.b, t), "rgba(236,131,90,0.18)"); });
    const hrTicks = [];
    for (let v = Math.ceil(T.hrLo / 20) * 20; v <= T.hrHi; v += 20) hrTicks.push(v);
    frameP(P1, hrTicks, hrY, (v) => v, "HR (bpm)");
    c.setLineDash([4, 4]); c.strokeStyle = "rgba(230,103,103,0.6)";
    c.fillStyle = "rgba(230,103,103,0.9)"; c.font = "10px " + mono; c.textAlign = "right";
    [[120, "nhanh > 120"], [50, "chậm < 50"]].forEach(([v, label]) => {
      if (v <= T.hrLo || v >= T.hrHi) return;
      const yy = Math.round(hrY(v)) + 0.5;
      c.beginPath(); c.moveTo(x0, yy); c.lineTo(x1, yy); c.stroke();
      c.fillText(label, x1 - 2, yy - 3);
    });
    c.setLineDash([]);
    function hrLine(from, to, alpha) {
      c.globalAlpha = alpha; c.strokeStyle = hrC; c.lineWidth = 1.6; c.lineJoin = "round";
      c.beginPath(); let started = false;
      for (let i = from; i < to; i++) {
        const hr = rec.beats[i][1];
        if (hr == null) continue;
        const xx = xOf(S.beatT[i]), yy = hrY(hr);
        if (!started) { c.moveTo(xx, yy); started = true; } else c.lineTo(xx, yy);
      }
      c.stroke(); c.globalAlpha = 1;
    }
    hrLine(Math.max(0, S.beatPtr - 1), rec.beats.length, 0.15);
    hrLine(0, S.beatPtr, 1);

    // --- RR tachogram ---
    const P2 = panels[1];
    const rrY = (v) => P2.y1 - Math.min(v, T.rrHi) / T.rrHi * P2.h;
    T.bands.forEach((bd) => { if (bd.type === "irregular" && bd.a <= t) band(P2, bd.a, Math.min(bd.b, t), "rgba(250,178,25,0.13)"); });
    const rrTicks = [];
    for (let v = 0; v <= T.rrHi + 1e-6; v += (T.rrHi > 2.5 ? 1 : 0.5)) rrTicks.push(v);
    frameP(P2, rrTicks, rrY, (v) => v.toFixed(1), "RR (s) — tachogram");
    for (let i = 1; i < rec.beats.length; i++) {
      const rr = T.rr[i], pvc = rec.beats[i][2] === 1;
      c.globalAlpha = i >= S.beatPtr ? 0.15 : 1;
      c.fillStyle = rr > 2 ? crit : pvc ? warn : "#9fd7ff";
      c.beginPath(); c.arc(xOf(S.beatT[i]), rrY(rr), pvc || rr > 2 ? 2.6 : 1.8, 0, Math.PI * 2); c.fill();
    }
    c.globalAlpha = 1;

    // --- ST-MEM theo cửa sổ 9 s ---
    const P3 = panels[2];
    const pY = (v) => P3.y1 - v * (P3.h - 4);
    frameP(P3, [0, 0.5, 1], pY, (v) => v.toFixed(1), D.model ? "ST-MEM p(bất thường) mỗi 9 s" : "ST-MEM (chưa có kết quả)");
    const thr = D.model ? D.model.threshold : 0.5;
    const kDone = Math.floor(t / S.win);
    rec.windows.forEach((w, k) => {
      const xa = xOf(k * S.win) + 1, xb = xOf((k + 1) * S.win) - 1;
      const done = k < kDone;
      if (w.truth === 1) {
        c.strokeStyle = crit; c.lineWidth = 2; c.globalAlpha = done ? 1 : 0.3;
        c.beginPath(); c.moveTo(xa, P3.y1 + 4); c.lineTo(xb, P3.y1 + 4); c.stroke();
      }
      if (w.p == null) return;
      c.globalAlpha = done ? 1 : 0.15;
      c.fillStyle = w.p >= thr ? serious : "#4a5048";
      c.fillRect(xa, pY(w.p), Math.max(1, xb - xa), P3.y1 - pY(w.p));
    });
    c.globalAlpha = 1;
    c.setLineDash([4, 4]); c.strokeStyle = "rgba(255,255,255,0.45)"; c.lineWidth = 1;
    const ty = Math.round(pY(thr)) + 0.5;
    c.beginPath(); c.moveTo(x0, ty); c.lineTo(x1, ty); c.stroke();
    c.setLineDash([]);

    // Trục thời gian
    c.fillStyle = muted; c.font = "10px " + mono; c.textAlign = "center"; c.strokeStyle = grid;
    const step = S.dur > 240 ? 60 : 30;
    for (let s = 0; s <= S.dur + 0.01; s += step) {
      const xx = Math.round(xOf(s)) + 0.5;
      c.beginPath(); c.moveTo(xx, TM.t); c.lineTo(xx, H - TM.b); c.stroke();
      c.fillText(mmss(s), xOf(s), H - 6);
    }

    drawTitles();

    // Cửa sổ 9 s đang hiện trên màn ECG + đầu phát
    const sw = Math.floor(t / S.win) * S.win;
    c.fillStyle = "rgba(255,255,255,0.06)";
    c.fillRect(xOf(sw), TM.t, xOf(Math.min(S.dur, sw + S.win)) - xOf(sw), H - TM.t - TM.b);
    c.strokeStyle = "#fff"; c.lineWidth = 1.5;
    c.beginPath(); c.moveTo(xOf(t), TM.t); c.lineTo(xOf(t), H - TM.b + 2); c.stroke();
  }

  function drawPoincare() {
    const c = pctx, W = T.PW, H = T.PH, ml = 30, mb = 18, mt = 8, mr = 8;
    c.clearRect(0, 0, W, H);
    const hi = Math.max(1.5, Math.min(T.rrHi, 3));
    const size = Math.min(W - ml - mr, H - mt - mb);
    const ox = ml + (W - ml - mr - size) / 2, oy = mt + size;
    const sx = (v) => ox + Math.min(v, hi) / hi * size, sy = (v) => oy - Math.min(v, hi) / hi * size;
    const muted = css("--muted"), mono = css("--mono");
    c.strokeStyle = "rgba(255,255,255,0.08)"; c.lineWidth = 1;
    c.fillStyle = muted; c.font = "10px " + mono;
    for (let v = 0; v <= hi + 1e-6; v += 0.5) {
      c.beginPath(); c.moveTo(sx(v), sy(0)); c.lineTo(sx(v), sy(hi)); c.stroke();
      c.beginPath(); c.moveTo(sx(0), sy(v)); c.lineTo(sx(hi), sy(v)); c.stroke();
      if (v > 0 && Math.abs(v - Math.round(v)) < 1e-6) {
        c.textAlign = "center"; c.fillText(v + " s", sx(v), oy + 13);
        c.textAlign = "right"; c.fillText(v + " s", ox - 4, sy(v) + 3);
      }
    }
    c.strokeStyle = "rgba(255,255,255,0.25)"; c.setLineDash([3, 3]);
    c.beginPath(); c.moveTo(sx(0), sy(0)); c.lineTo(sx(hi), sy(hi)); c.stroke(); c.setLineDash([]);
    const n = S.beatPtr, bt = S.beatT, rec = S.rec;
    const warn = css("--warning"), crit = css("--critical");
    for (let i = 2; i < n; i++) {
      if (bt[i] < S.t - 60) continue;
      const a = T.rr[i - 1], b = T.rr[i];
      const flag = rec.beats[i][2] === 1 || rec.beats[i - 1][2] === 1;
      c.fillStyle = a > 2 || b > 2 ? crit : flag ? warn : "#9fd7ff";
      const last = i === n - 1;
      c.globalAlpha = last ? 1 : 0.7;
      c.beginPath(); c.arc(sx(a), sy(b), last ? 4 : 2.2, 0, Math.PI * 2); c.fill();
      if (last) { c.strokeStyle = "#fff"; c.lineWidth = 1; c.stroke(); }
    }
    c.globalAlpha = 1;
  }

  trendWrap.addEventListener("click", (e) => {
    const r = trendWrap.getBoundingClientRect();
    const frac = (e.clientX - r.left - TM.l) / (r.width - TM.l - TM.r);
    seek(Math.min(1, Math.max(0, frac)) * S.dur);
  });

  /* ------------------------------------------------------------------ canvas ECG */
  const canvas = $("m-canvas");
  const ctx = canvas.getContext("2d");
  let W = 0, H = 0, DPR = 1;
  function resize() {
    const r = canvas.parentElement.getBoundingClientRect();
    DPR = Math.min(2, window.devicePixelRatio || 1);
    W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
    canvas.width = Math.round(W * DPR); canvas.height = Math.round(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    $("m-scale").textContent = `${screenSeconds()} s/màn (= 1 cửa sổ ST-MEM) · lưới 0.2 s × 0.5 mV`;
    resizeTrend();
  }
  const screenSeconds = () => S.win;
  if (window.ResizeObserver) {
    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement); ro.observe(trendWrap); ro.observe(poinCanvas.parentElement);
  }
  window.addEventListener("resize", resize);

  const TOP = 22, BOTTOM = 20;
  function draw() {
    const rec = S.rec, fs = S.fs, sig = S.sig;
    const span = screenSeconds();
    ctx.clearRect(0, 0, W, H);

    const [lo0, hi0] = rec.y_range;
    const pad = (hi0 - lo0) * 0.12;
    const lo = lo0 - pad, hi = hi0 + pad;
    const plotH = H - TOP - BOTTOM;
    const yOf = (v) => TOP + (hi - v) / (hi - lo) * plotH;
    const pxPerS = W / span;

    // Lưới giấy ECG (đứng yên)
    const minor = css("--grid-minor"), major = css("--grid-major");
    ctx.lineWidth = 1;
    for (let i = 0, x = 0; x <= W; i++, x = i * 0.2 * pxPerS) {
      ctx.strokeStyle = i % 5 === 0 ? major : minor;
      ctx.beginPath(); ctx.moveTo(Math.round(x) + 0.5, 0); ctx.lineTo(Math.round(x) + 0.5, H); ctx.stroke();
    }
    const mvStep = 0.5;
    for (let v = Math.ceil(lo / mvStep) * mvStep; v <= hi; v += mvStep) {
      const y = Math.round(yOf(v)) + 0.5;
      ctx.strokeStyle = Math.abs(v) < 1e-6 ? major : minor;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    const t = S.t;
    const sweepStart = Math.floor(t / span) * span;
    const cursorX = (t - sweepStart) * pxPerS;
    const gapS = 18 / pxPerS;
    const trace = css("--trace");

    function segment(tFrom, tTo, origin, alpha) {
      const i0 = Math.max(0, Math.ceil(tFrom * fs)), i1 = Math.min(sig.length - 1, Math.floor(tTo * fs));
      if (i1 <= i0) return;
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = trace;
      ctx.lineWidth = 1.8;
      ctx.lineJoin = "round";
      ctx.beginPath();
      for (let i = i0; i <= i1; i++) {
        const x = (i / fs - origin) * pxPerS, y = yOf(sig[i]);
        if (i === i0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
    // Phần cũ (vòng quét trước) bên phải con trỏ, phần mới bên trái
    segment(t - span + gapS, sweepStart, sweepStart - span, 0.5);
    segment(sweepStart, t, sweepStart, 1);

    // Nhãn trên các beat & sự kiện trong khung nhìn
    ctx.font = "600 11px " + css("--mono");
    ctx.textAlign = "center";
    const xOfT = (bt) => {
      if (bt >= sweepStart && bt <= t) return (bt - sweepStart) * pxPerS;
      if (bt >= t - span + gapS && bt < sweepStart) return (bt - sweepStart + span) * pxPerS;
      return null;
    };
    const warn = css("--warning"), crit = css("--critical"), muted = css("--muted"), serious = css("--serious");
    const bFrom = Math.max(0, t - span);
    for (let i = lowerBound(S.beatT, bFrom); i < rec.beats.length && S.beatT[i] <= t; i++) {
      if (rec.beats[i][2] !== 1) continue;
      const x = xOfT(S.beatT[i]);
      if (x == null) continue;
      ctx.fillStyle = warn;
      ctx.fillText("PVC", x, 14);
    }
    rec.events.forEach((e) => {
      if (e.type !== "pause" || e.t < bFrom || e.t > t) return;
      const x1 = xOfT(e.t), x0 = xOfT(e.t - e.value);
      if (x1 == null) return;
      ctx.strokeStyle = crit; ctx.fillStyle = crit; ctx.lineWidth = 2;
      const xs = x0 != null && x0 < x1 ? x0 : Math.max(0, x1 - e.value * pxPerS);
      ctx.beginPath(); ctx.moveTo(xs, 6); ctx.lineTo(x1, 6); ctx.stroke();
      ctx.fillText(`Ngưng ${fmt2(e.value)} s`, (xs + x1) / 2, 18);
    });

    // Nhãn chuyên gia ở đáy
    if (annBox.checked) {
      const anns = rec.annotations;
      ctx.font = "11px " + css("--mono");
      for (let i = 0; i < anns.length; i++) {
        const at = anns[i][0] / fs;
        if (at < bFrom || at > t) continue;
        const s = anns[i][1];
        if (!D.symbols[s] || s === "+" || s === "~" || s === "|" || s === "\"") continue;
        const x = xOfT(at);
        if (x == null) continue;
        ctx.fillStyle = s === "N" ? muted : serious;
        ctx.fillText(s, x, H - 6);
      }
    }

    // Con trỏ quét
    ctx.fillStyle = "#050605";
    ctx.fillRect(cursorX + 1, 0, 16, H);
    const iNow = Math.min(sig.length - 1, Math.floor(t * fs));
    ctx.fillStyle = trace;
    ctx.shadowColor = css("--trace-glow"); ctx.shadowBlur = 10;
    ctx.beginPath(); ctx.arc(cursorX, yOf(sig[iNow]), 3, 0, Math.PI * 2); ctx.fill();
    ctx.shadowBlur = 0;
  }
  function lowerBound(arr, x) {
    let a = 0, b = arr.length;
    while (a < b) { const m = (a + b) >> 1; if (arr[m] < x) a = m + 1; else b = m; }
    return a;
  }

  /* ------------------------------------------------------------------ vòng lặp */
  function frame(now) {
    const dt = Math.min(0.1, (now - S.lastFrame) / 1000);
    S.lastFrame = now;
    if (S.playing && S.rec) {
      let t1 = S.t + dt * S.speed;
      if (t1 >= S.dur) {           // hết đoạn → phát lại từ đầu
        seek(0);
      } else {
        advance(t1, false);
        updateHr();
        renderModel(false);
        updateBanner(false);
      }
    }
    if (S.rec && W) {
      draw();
      if (now - S.lastTrend > 100 || !S.playing) { drawTrend(); drawPoincare(); S.lastTrend = now; }
    }
    const sec = Math.floor(S.t);
    if (sec !== S.lastClock) {
      S.lastClock = sec;
      $("m-clock").textContent = `${mmss(S.t)} / ${mmss(S.dur)}`;
      trendWrap.setAttribute("aria-valuemax", String(Math.round(S.dur)));
      trendWrap.setAttribute("aria-valuenow", String(sec));
      trendWrap.setAttribute("aria-valuetext", mmss(S.t));
    }
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------------------------ luật */
  (function renderRules() {
    const ul = el("ul", { class: "m-rules" });
    (D.rules || []).forEach((r) => {
      ul.append(el("li", null, [
        el("b", null, [el("span", { class: "dot sev-" + r.severity, "aria-hidden": "true" }), r.title]),
        r.rule,
      ]));
    });
    const box = $("m-rules");
    box.append(el("p", { class: "m-dim", style: "margin:10px 0 0",
      text: "Luật nhịp chạy trên từng R-peak, chỉ dùng các beat đã qua (giống chạy thời gian thực). ST-MEM chấm mỗi cửa sổ 9 s khi đã thu đủ; xác suất được tính trước bằng demo/train_stmem.py." }));
    box.append(ul);
  })();

  resize();
  setSpeed(SPEEDS.includes(Number(storeGet("ecg-monitor-speed", "1"))) ? Number(storeGet("ecg-monitor-speed", "1")) : 1);
  setPlaying(true);
  loadRecord(storeGet("ecg-monitor-record", D.records[0].id));
  S.lastFrame = performance.now();
  requestAnimationFrame(frame);
})();
