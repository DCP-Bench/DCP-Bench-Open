(function () {
  "use strict";

  /* ---------- Index: card rendering + filtering ---------- */
  var EVAL_STATUS = {
    optimal: { color: "#16a34a", label: "valid · optimal" },
    valid: { color: "#2563eb", label: "valid" },
    no_valid: { color: "#dc2626", label: "no valid model" },
    no_models: { color: "#6b7280", label: "no models" }
  };

  function pill(label, color) {
    var el = document.createElement("span");
    el.className = color ? "badge" : "badge plain";
    if (color) el.style.background = color;
    el.textContent = label;
    return el;
  }

  function renderCards() {
    var container = document.getElementById("cards");
    var countEl = document.getElementById("result-count");
    if (!container || !window.DCP_DATA) return;

    var data = window.DCP_DATA.problems || [];
    var q = (document.getElementById("filter-q") || { value: "" }).value.trim().toLowerCase();
    var type = (document.getElementById("filter-type") || { value: "" }).value;
    var source = (document.getElementById("filter-source") || { value: "" }).value;
    var inst = (document.getElementById("filter-instances") || { value: "" }).value;
    var gen = (document.getElementById("filter-gen") || { value: "" }).value;
    var evalStatus = (document.getElementById("filter-eval") || { value: "" }).value;
    var sort = (document.getElementById("sort-by") || { value: "name" }).value;

    var filtered = data.filter(function (p) {
      if (type && (p.type || "satisfaction") !== type) return false;
      if (source && p.source !== source) return false;
      if (inst === "single" && p.instances !== 1) return false;
      if (inst === "multiple" && p.instances < 2) return false;
      if (inst === "none" && (p.instances || 0) !== 0) return false;
      if (gen === "yes" && !p.generated) return false;
      if (gen === "no" && p.generated) return false;
      if (evalStatus && (p.evalBadge || "no_models") !== evalStatus) return false;
      if (q) {
        var hay = (p.id + " " + p.snippet).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });

    filtered.sort(function (a, b) {
      if (sort === "instances") return b.instances - a.instances;
      if (sort === "generated") return b.generated - a.generated;
      return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
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
      meta.appendChild(pill(p.type === "optimization" ? "Optimization" : "Satisfaction",
        p.type === "optimization" ? "#7c3aed" : null));

      var foot = document.createElement("div");
      foot.className = "card-foot";
      var instSpan = document.createElement("span");
      instSpan.className = "muted";
      instSpan.textContent = (p.instances || 0) + " instance" + (p.instances === 1 ? "" : "s");
      foot.appendChild(instSpan);
      if (p.generated) {
        var genSpan = document.createElement("span");
        genSpan.className = "muted";
        genSpan.textContent = p.generated + " generated model" + (p.generated === 1 ? "" : "s");
        foot.appendChild(genSpan);
      }
      var ev = EVAL_STATUS[p.evalBadge] || EVAL_STATUS.no_models;
      var evalPill = document.createElement("span");
      evalPill.className = "badge";
      evalPill.style.background = ev.color;
      evalPill.textContent = ev.label;
      foot.appendChild(evalPill);

      card.appendChild(h3);
      card.appendChild(desc);
      card.appendChild(meta);
      card.appendChild(foot);
      container.appendChild(card);
    });

    if (!filtered.length) {
      var empty = document.createElement("p");
      empty.className = "desc";
      empty.textContent = "No problems match the current filters.";
      container.appendChild(empty);
    }
  }

  function initIndex() {
    if (!window.DCP_DATA) return;
    ["filter-q", "filter-type", "filter-source", "filter-instances",
     "filter-gen", "filter-eval", "sort-by"].forEach(function (id) {
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
