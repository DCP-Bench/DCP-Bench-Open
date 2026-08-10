(function () {
  "use strict";

  /* ---------- Index: card rendering + filtering ---------- */
  function renderCards() {
    var container = document.getElementById("cards");
    var countEl = document.getElementById("result-count");
    if (!container || !window.DCP_DATA) return;

    var data = window.DCP_DATA.problems || [];
    var query = (document.getElementById("filter-q") || { value: "" }).value.trim().toLowerCase();
    var fw = (document.getElementById("filter-fw") || { value: "" }).value;
    var origin = (document.getElementById("filter-origin") || { value: "" }).value;

    var filtered = data.filter(function (p) {
      if (fw && p.frameworks.indexOf(fw) === -1) return false;
      if (origin && (p.origin || "hand") !== origin) return false;
      if (query) {
        var hay = (p.id + " " + p.snippet).toLowerCase();
        if (hay.indexOf(query) === -1) return false;
      }
      return true;
    });

    if (countEl) {
      countEl.textContent = filtered.length + " of " + data.length + " problems";
    }

    container.innerHTML = "";
    filtered.forEach(function (p) {
      var card = document.createElement("div");
      card.className = "card";

      var h3 = document.createElement("h3");
      var link = document.createElement("a");
      link.href = "problems/" + p.id + ".html";
      link.textContent = p.id;
      h3.appendChild(link);

      var desc = document.createElement("p");
      desc.className = "desc";
      desc.textContent = p.snippet;

      var meta = document.createElement("div");
      meta.className = "meta";
      (p.frameworks || []).forEach(function (f) { meta.appendChild(badge(f, f)); });
      meta.appendChild(badge(p.originLabel || p.origin, p.origin));
      var inst = document.createElement("span");
      inst.className = "muted";
      inst.textContent = (p.instances || 0) + " instance" + (p.instances === 1 ? "" : "s");
      meta.appendChild(inst);
      if (p.generated) {
        var gen = document.createElement("span");
        gen.className = "muted";
        gen.textContent = (p.generated === 1 ? "1 generated model" : p.generated + " generated models");
        meta.appendChild(gen);
      }

      card.appendChild(h3);
      card.appendChild(desc);
      card.appendChild(meta);
      container.appendChild(card);
    });

    if (!filtered.length) {
      var empty = document.createElement("p");
      empty.className = "desc";
      empty.textContent = "No problems match the current filters.";
      container.appendChild(empty);
    }
  }

  function badge(label, key) {
    var el = document.createElement("span");
    el.className = "badge " + badgeClass(key);
    el.textContent = label;
    return el;
  }

  function badgeClass(key) {
    var colors = {
      CPMpy: "#0d9488",
      "OR-Tools": "#ea580c",
      MiniZinc: "#2563eb",
      hand: "#64748b"
    };
    if (colors[key]) return "";
    return "plain";
  }

  function initIndex() {
    if (!window.DCP_DATA) return;
    ["filter-q", "filter-fw", "filter-origin"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("input", renderCards);
    });
    renderCards();
  }

  /* ---------- Problem page: markdown descriptions ---------- */
  function escHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function linkify(text) {
    return text.replace(/(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noopener">$1</a>');
  }

  function initMarkdown() {
    if (!window.marked) return;
    document.querySelectorAll(".md-desc").forEach(function (el) {
      el.innerHTML = marked.parse(linkify(escHtml(el.textContent)));
    });
  }

  /* ---------- Problem page: nested tabs + copy buttons ---------- */
  function initTabs() {
    document.querySelectorAll(".tab-group").forEach(function (group) {
      var bar = group.querySelector(".tab-bar");
      if (!bar) return;
      var buttons = bar.querySelectorAll(".tab-btn");
      buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var name = btn.getAttribute("data-tab");
          buttons.forEach(function (b) { b.classList.toggle("active", b === btn); });
          // only direct children of this group are this group's panes
          Array.prototype.forEach.call(group.children, function (el) {
            if (el.classList.contains("tab-pane")) {
              el.classList.toggle("active", el.getAttribute("data-pane") === name);
            }
          });
        });
      });
    });
  }

  function initCopy() {
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        var target = document.getElementById(btn.getAttribute("data-copy"));
        if (!target) return;
        var text = target.textContent;
        var done = function () {
          var old = btn.textContent;
          btn.classList.add("copied");
          btn.textContent = "Copied ✓";
          setTimeout(function () {
            btn.textContent = old;
            btn.classList.remove("copied");
          }, 1200);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, done);
        } else {
          done();
        }
      });
    });
  }

  function init() {
    initIndex();
    initMarkdown();
    initTabs();
    initCopy();
    if (window.hljs) hljs.highlightAll();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
