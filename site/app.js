(function () {
  "use strict";

  var EVAL_STATUS = {
    optimal: { color: "#16a34a", label: "valid · optimal" },
    valid: { color: "#2563eb", label: "valid" },
    no_valid: { color: "#dc2626", label: "no valid model" },
    no_models: { color: "#6b7280", label: "no models" }
  };
  var viewMode = "grid";
  var sortKey = "name";
  var sortDirection = 1;

  function pill(label, color) {
    var el = document.createElement("span");
    el.className = color ? "badge" : "badge plain";
    if (color) el.style.background = color;
    el.textContent = label;
    return el;
  }

  function valueForSort(problem, key) {
    if (key === "type") return problem.type || "satisfaction";
    if (key === "source") return problem.source || "";
    if (key === "instances") return problem.instances || 0;
    if (key === "generated") return problem.generated || 0;
    return problem.id || "";
  }

  function compareProblems(a, b) {
    var av = valueForSort(a, sortKey);
    var bv = valueForSort(b, sortKey);
    var result;
    if (typeof av === "number" && typeof bv === "number") {
      result = av - bv;
    } else {
      result = String(av).localeCompare(String(bv));
    }
    return result * sortDirection;
  }

  function setSort(key) {
    if (sortKey === key) {
      sortDirection *= -1;
    } else {
      sortKey = key;
      sortDirection = 1;
    }
    var select = document.getElementById("sort-by");
    if (select && Array.prototype.some.call(select.options, function (option) {
      return option.value === key;
    })) {
      select.value = key;
    }
    renderCards();
  }

  function appendGridCard(container, problem) {
    var card = document.createElement("div");
    card.className = "card";

    var h3 = document.createElement("h3");
    var link = document.createElement("a");
    link.href = "problems/" + problem.id + ".html";
    link.textContent = problem.id;
    h3.appendChild(link);

    var desc = document.createElement("p");
    desc.className = "desc";
    desc.textContent = problem.snippet;

    var meta = document.createElement("div");
    meta.className = "meta";
    meta.appendChild(pill(problem.type === "optimization" ? "Optimization" : "Satisfaction",
      problem.type === "optimization" ? "#7c3aed" : null));

    var foot = document.createElement("div");
    foot.className = "card-foot";
    var instanceLabel = (problem.instances || 0) + " instance" + (problem.instances === 1 ? "" : "s");
    foot.appendChild(document.createTextNode(instanceLabel));
    if (problem.generated) {
      foot.appendChild(document.createTextNode(" · " + problem.generated + " generated model" +
        (problem.generated === 1 ? "" : "s")));
    }
    var ev = EVAL_STATUS[problem.evalBadge] || EVAL_STATUS.no_models;
    foot.appendChild(pill(ev.label, ev.color));

    card.appendChild(h3);
    card.appendChild(desc);
    card.appendChild(meta);
    card.appendChild(foot);
    container.appendChild(card);
  }

  function appendListCell(row, text, className) {
    var cell = document.createElement("div");
    cell.className = "list-cell" + (className ? " " + className : "");
    cell.textContent = text;
    row.appendChild(cell);
    return cell;
  }

  function renderList(container, data) {
    var header = document.createElement("div");
    header.className = "list-header";
    header.setAttribute("role", "row");
    [["Problem", "name"], ["Type", "type"], ["Source", "source"],
      ["Instances", "instances"], ["Generated", "generated"]].forEach(function (item) {
      var cell = document.createElement("div");
      cell.className = "list-cell";
      var button = document.createElement("button");
      button.type = "button";
      button.className = "list-sort";
      button.textContent = item[0] + (sortKey === item[1] ? (sortDirection === 1 ? " ↑" : " ↓") : "");
      button.addEventListener("click", function () { setSort(item[1]); });
      cell.appendChild(button);
      header.appendChild(cell);
    });
    container.appendChild(header);

    data.forEach(function (problem) {
      var row = document.createElement("div");
      row.className = "list-row";
      row.setAttribute("role", "row");
      var nameCell = document.createElement("div");
      nameCell.className = "list-cell list-name";
      var link = document.createElement("a");
      link.href = "problems/" + problem.id + ".html";
      link.textContent = problem.id;
      nameCell.appendChild(link);
      row.appendChild(nameCell);
      appendListCell(row, problem.type === "optimization" ? "Optimization" : "Satisfaction");
      appendListCell(row, problem.source || "Unknown");
      appendListCell(row, String(problem.instances || 0));
      appendListCell(row, String(problem.generated || 0));
      container.appendChild(row);
    });
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

    var filtered = data.filter(function (problem) {
      if (type && (problem.type || "satisfaction") !== type) return false;
      if (source && problem.source !== source) return false;
      if (inst === "single" && problem.instances !== 1) return false;
      if (inst === "multiple" && problem.instances < 2) return false;
      if (q) {
        var haystack = (problem.id + " " + problem.snippet).toLowerCase();
        if (haystack.indexOf(q) === -1) return false;
      }
      return true;
    });

    filtered.sort(compareProblems);
    if (countEl) countEl.textContent = filtered.length + " of " + data.length + " problems";
    container.innerHTML = "";
    container.classList.toggle("list-view", viewMode === "list");

    if (!filtered.length) {
      var empty = document.createElement("p");
      empty.className = "desc empty-state";
      empty.textContent = "No problems match the current filters.";
      container.appendChild(empty);
      return;
    }
    if (viewMode === "list") {
      renderList(container, filtered);
    } else {
      filtered.forEach(function (problem) { appendGridCard(container, problem); });
    }
  }

  function initIndex() {
    if (!window.DCP_DATA) return;
    ["filter-q", "filter-type", "filter-source", "filter-instances"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener(el.tagName === "SELECT" ? "change" : "input", renderCards);
    });
    var sort = document.getElementById("sort-by");
    if (sort) sort.addEventListener("change", function () {
      sortKey = sort.value;
      sortDirection = 1;
      renderCards();
    });
    document.querySelectorAll(".view-btn").forEach(function (button) {
      button.addEventListener("click", function () {
        viewMode = button.getAttribute("data-view");
        document.querySelectorAll(".view-btn").forEach(function (other) {
          var active = other === button;
          other.classList.toggle("active", active);
          other.setAttribute("aria-pressed", active ? "true" : "false");
        });
        renderCards();
      });
    });
    renderCards();
  }

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

  function initTabs() {
    document.querySelectorAll(".tab-group").forEach(function (group) {
      var bar = group.querySelector(".tab-bar");
      if (!bar) return;
      var buttons = bar.querySelectorAll(".tab-btn");
      buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var name = btn.getAttribute("data-tab");
          buttons.forEach(function (b) { b.classList.toggle("active", b === btn); });
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
          navigator.clipboard.writeText(target.textContent).then(done, done);
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
