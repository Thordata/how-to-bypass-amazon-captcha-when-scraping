/* CAPTCHA Playground — detection engine + UI.
 *
 * The CAPTCHA_MARKERS array below mirrors amazon_captcha/detect.py EXACTLY.
 * Keep both lists in sync when you add or remove a marker. The Python module
 * is the canonical source of truth.
 *
 * This file is dependency-free. It runs entirely in the browser and never
 * sends anything to a network — all analysis is local.
 */

(function () {
  "use strict";

  /* ---- Canonical marker list (mirrors amazon_captcha/detect.py) ------- */
  var CAPTCHA_MARKERS = [
    "type the characters you see in this image",
    "to discuss automated access to amazon data",
    "please enter the characters you see below",
    "enter the characters you see in the picture",
    "robot check",
    "/captcha/",
    "/errors/validatecapcha",
    "/errors/validatecaptcha",
    "errors/validatecaptcha",
    'name="amzn"',
    'id="captchacharacters"',
    "captchacharacters",
    "apexusimetrics",
    "<title>robot check",
    "<title>amazon captcha"
  ];

  var CHALLENGE_STATUS_CODES = { 403: true, 429: true, 503: true };

  /* ---- Synthetic sample snippets (NOT real Amazon HTML) -------------- */
  var SAMPLES = {
    captcha: {
      label: "CAPTCHA / robot-check page",
      status: 503,
      html: [
        "<!DOCTYPE html><html><head><title>Robot Check</title></head>",
        "<body>",
        "  <h4>Type the characters you see in this image below.</h4>",
        "  <form action=\"/errors/validatecapcha\" method=\"post\">",
        "    <input type=\"hidden\" name=\"amzn\" value=\"abc123\" />",
        "    <input type=\"text\" id=\"captchacharacters\" name=\"field-keywords\" />",
        "    <img src=\"/captcha/verify/img.png\" alt=\"captcha\" />",
        "  </form>",
        "  <p>To discuss automated access to Amazon data please contact apihelp@amazon.com</p>",
        "</body></html>"
      ].join("\n")
    },
    soft: {
      label: "Soft challenge (URL-only marker)",
      status: 200,
      html: [
        "<!DOCTYPE html><html><head><title>Please verify</title></head>",
        "<body>",
        "  <p>Redirecting for verification...</p>",
        "  <!-- effective URL contained /errors/validatecaptcha -->",
        "</body></html>"
      ].join("\n")
    },
    clean: {
      label: "Normal product page",
      status: 200,
      html: [
        "<!DOCTYPE html><html><head><title>Wireless Mouse - Amazon.com</title></head>",
        "<body>",
        "  <h1 id=\"title\">Ergonomic Wireless Mouse</h1>",
        "  <span id=\"priceblock_ourprice\">$19.99</span>",
        "  <span class=\"a-icon-alt\">4.5 out of 5 stars</span>",
        "</body></html>"
      ].join("\n")
    }
  };

  /* ---- State --------------------------------------------------------- */
  var customMarkers = []; // user-added markers (strings)

  /* ---- Detection (mirrors python detect()) --------------------------- */
  function findMarkers(haystack, extras) {
    if (!haystack) return [];
    var lower = haystack.toLowerCase();
    var all = CAPTCHA_MARKERS.concat(extras || []);
    var seen = {};
    var matched = [];
    for (var i = 0; i < all.length; i++) {
      var m = all[i];
      var key = m.toLowerCase();
      if (seen[key]) continue;
      if (lower.indexOf(key) !== -1) {
        seen[key] = true;
        matched.push(m);
      }
    }
    return matched;
  }

  function riskLevel(matched, status) {
    if (status && CHALLENGE_STATUS_CODES[status] && matched.length >= 1) return "high";
    if (matched.length >= 3) return "high";
    if (matched.length >= 1) return "medium";
    if (status && CHALLENGE_STATUS_CODES[status]) return "medium";
    if (status && status >= 400) return "low";
    return "none";
  }

  function detect(html, status) {
    var matched = findMarkers(html, customMarkers);
    var isCaptcha = matched.length > 0 || (!html && status && CHALLENGE_STATUS_CODES[status]);
    return {
      isCaptcha: isCaptcha,
      matched: matched,
      status: status,
      risk: riskLevel(matched, status)
    };
  }

  /* ---- HTML escaping -------------------------------------------------- */
  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /* ---- Highlight matched markers in the preview ---------------------- */
  function highlightPreview(html, matched) {
    if (!matched.length) return escapeHtml(html);
    // Escape first, then wrap occurrences. Build a single case-insensitive
    // regex from the escaped markers. Use a placeholder to avoid double-
    // highlighting nested markers.
    var escaped = escapeHtml(html);
    var patterns = matched.map(function (m) {
      return escapeHtml(m).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    });
    // Sort longest-first so longer markers win.
    patterns.sort(function (a, b) { return b.length - a.length; });
    var re = new RegExp("(" + patterns.join("|") + ")", "gi");
    return escaped.replace(re, '<mark>$&</mark>');
  }

  /* ---- Risk meter percentage ----------------------------------------- */
  function riskPercent(risk, matchedCount) {
    if (risk === "high") return Math.min(98, 70 + matchedCount * 6);
    if (risk === "medium") return 50;
    if (risk === "low") return 25;
    return 6;
  }

  /* ---- DOM helpers --------------------------------------------------- */
  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }

  function showToast(msg) {
    var t = $("#toast");
    t.textContent = msg;
    t.classList.add("is-shown");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(function () { t.classList.remove("is-shown"); }, 2200);
  }

  /* ---- Render: matched markers list ---------------------------------- */
  function renderMatches(matched) {
    var box = $("#matches");
    var list = $("#matchesList");
    list.innerHTML = "";
    if (!matched.length) {
      box.style.display = "none";
      return;
    }
    box.style.display = "";
    matched.forEach(function (m, i) {
      var li = document.createElement("li");
      li.className = "matches__item";
      li.style.animationDelay = (i * 60) + "ms";
      li.innerHTML =
        '<span class="check">✓</span>' +
        '<span class="marker-text">' + escapeHtml(m) + '</span>';
      list.appendChild(li);
    });
  }

  /* ---- Render: risk meter + verdict ---------------------------------- */
  function renderVerdict(result) {
    var meter = $("#riskValue");
    var bar = $("#riskBar");
    var verdict = $("#verdict");

    meter.className = "risk-meter__value is-" + result.risk;
    meter.textContent = result.risk;
    bar.className = "risk-bar__fill is-" + result.risk;
    bar.style.width = riskPercent(result.risk, result.matched.length) + "%";

    verdict.className = "verdict is-shown " + (result.isCaptcha ? "is-captcha" : "is-clean");
    var icon = result.isCaptcha ? "⚠️" : "✅";
    var title = result.isCaptcha ? "CAPTCHA / bot-check detected" : "Response looks clean";
    var detail = result.matched.length + " marker" + (result.matched.length === 1 ? "" : "s") + " matched";
    if (!result.isCaptcha && result.status && result.status >= 400) {
      detail = "No markers, but status " + result.status + " is still suspicious";
    }
    verdict.innerHTML =
      '<span class="verdict__icon">' + icon + '</span>' +
      '<div><div class="verdict__title">' + title + '</div>' +
      '<div class="verdict__detail">' + detail + '</div></div>';
  }

  /* ---- Render: highlighted preview ----------------------------------- */
  function renderPreview(html, matched) {
    $("#preview").innerHTML = highlightPreview(html, matched) || '<span style="color:var(--fg-3)">(empty body)</span>';
  }

  /* ---- Flow animation ------------------------------------------------- */
  function animateFlow() {
    var nodes = $$(".pg-flow__node");
    nodes.forEach(function (n) { n.classList.remove("is-active"); });
    nodes.forEach(function (node, i) {
      setTimeout(function () {
        node.classList.add("is-active");
        setTimeout(function () {
          if (i === nodes.length - 1) {
            // leave the last (JSON) node active as the "result"
          } else {
            node.classList.remove("is-active");
          }
        }, 380);
      }, i * 260);
    });
  }

  /* ---- Marker editor -------------------------------------------------- */
  function renderEditor() {
    var list = $("#editorList");
    list.innerHTML = "";
    CAPTCHA_MARKERS.forEach(function (m) {
      var li = document.createElement("li");
      li.className = "editor__item is-core";
      li.innerHTML =
        '<span class="editor__marker">' + escapeHtml(m) + '</span>' +
        '<span class="editor__badge">core</span>' +
        '<button class="editor__remove" disabled title="core markers cannot be removed">×</button>';
      list.appendChild(li);
    });
    customMarkers.forEach(function (m, idx) {
      var li = document.createElement("li");
      li.className = "editor__item is-custom";
      li.innerHTML =
        '<span class="editor__marker">' + escapeHtml(m) + '</span>' +
        '<span class="editor__badge">custom</span>' +
        '<button class="editor__remove" data-idx="' + idx + '" title="remove">×</button>';
      list.appendChild(li);
    });
    // Wire remove buttons.
    $$(".editor__remove[data-idx]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var idx = parseInt(btn.getAttribute("data-idx"), 10);
        customMarkers.splice(idx, 1);
        renderEditor();
        runAnalysis(); // re-analyze with the updated list
      });
    });
  }

  /* ---- Main analysis -------------------------------------------------- */
  function runAnalysis() {
    var html = $("#input").value;
    var statusRaw = $("#status").value.trim();
    var status = statusRaw ? parseInt(statusRaw, 10) : null;
    if (statusRaw && isNaN(status)) status = null;

    var result = detect(html, status);
    renderVerdict(result);
    renderMatches(result.matched);
    renderPreview(html, result.matched);
    animateFlow();
    return result;
  }

  /* ---- Export JSON ---------------------------------------------------- */
  function exportJson() {
    var html = $("#input").value;
    var statusRaw = $("#status").value.trim();
    var status = statusRaw ? parseInt(statusRaw, 10) : null;
    var result = detect(html, status);
    var payload = {
      timestamp: new Date().toISOString(),
      input_length: html.length,
      status: status,
      is_captcha: result.isCaptcha,
      risk_level: result.risk,
      matched_markers: result.matched,
      active_markers_total: CAPTCHA_MARKERS.length + customMarkers.length,
      custom_markers: customMarkers
    };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "captcha-detection-result.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("Exported result as JSON");
  }

  /* ---- Load preset ---------------------------------------------------- */
  function loadPreset(key, btn) {
    var sample = SAMPLES[key];
    if (!sample) return;
    $("#input").value = sample.html;
    $("#status").value = String(sample.status);
    $$(".preset-btn").forEach(function (b) { b.classList.remove("is-active"); });
    if (btn) btn.classList.add("is-active");
    runAnalysis();
  }

  /* ---- Boot ----------------------------------------------------------- */
  document.addEventListener("DOMContentLoaded", function () {
    renderEditor();

    // Load the captcha sample by default so the page isn't empty.
    loadPreset("captcha", document.querySelector('.preset-btn[data-preset="captcha"]'));

    $("#analyzeBtn").addEventListener("click", runAnalysis);
    $("#exportBtn").addEventListener("click", exportJson);
    $("#clearBtn").addEventListener("click", function () {
      $("#input").value = "";
      $("#status").value = "";
      $$(".preset-btn").forEach(function (b) { b.classList.remove("is-active"); });
      runAnalysis();
      showToast("Cleared");
    });

    $$(".preset-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        loadPreset(btn.getAttribute("data-preset"), btn);
      });
    });

    // Add custom marker.
    $("#addMarkerBtn").addEventListener("click", function () {
      var input = $("#newMarker");
      var val = input.value.trim();
      if (!val) return;
      if (customMarkers.indexOf(val) !== -1 || CAPTCHA_MARKERS.indexOf(val) !== -1) {
        showToast("Marker already exists");
        return;
      }
      customMarkers.push(val);
      input.value = "";
      renderEditor();
      runAnalysis();
      showToast("Custom marker added");
    });
    $("#newMarker").addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); $("#addMarkerBtn").click(); }
    });

    // Live re-analyze on status input (debounced).
    var t;
    $("#status").addEventListener("input", function () {
      clearTimeout(t);
      t = setTimeout(runAnalysis, 250);
    });

    // Theme sync: when the main site changes theme, playground follows
    // (it shares the same <html data-theme> since it's the same origin).
    window.addEventListener("themechange", function () {
      // data-theme is already applied to <html> by main.js; nothing to do here.
    });
  });
})();
