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

  function selectedFilterValues(group) {
    var selector = 'input[data-filter-group="' + group + '"]:checked';
    return Array.prototype.map.call(document.querySelectorAll(selector), function (input) {
      return input.value;
    });
  }

  function updateFilterButton(group) {
    var labels = {
      type: { id: "filter-type", name: "Type" },
      source: { id: "filter-source", name: "Source" },
      instances: { id: "filter-instances", name: "Instances" },
      framework: { id: "filter-framework", name: "Generated framework" }
    };
    var config = labels[group];
    if (!config) return;
    var values = selectedFilterValues(group);
    var button = document.getElementById(config.id);
    if (!button) return;
    var label = config.name + ": ";
    if (!values.length) {
      label += group === "framework" ? "Any" : "All";
    } else if (group === "framework" && values.indexOf("any") !== -1) {
      label += "Any";
    } else if (values.length === 1) {
      var input = document.querySelector('input[data-filter-group="' + group + '"][value="' + values[0] + '"]');
      label += input ? input.parentElement.textContent.trim() : "1 selected";
    } else {
      label += values.length + " selected";
    }
    button.textContent = label;
  }

  function setViewMode(mode) {
    viewMode = mode;
    document.querySelectorAll(".view-btn").forEach(function (button) {
      var active = button.getAttribute("data-view") === mode;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    renderCards();
  }

  function initFilterMenus() {
    document.querySelectorAll(".filter-menu").forEach(function (menu) {
      menu.addEventListener("click", function (event) { event.stopPropagation(); });
      var trigger = menu.querySelector(".filter-trigger");
      if (trigger) {
        trigger.addEventListener("click", function () {
          var open = menu.classList.toggle("open");
          trigger.setAttribute("aria-expanded", open ? "true" : "false");
        });
      }
      menu.querySelectorAll('input[data-filter-group]').forEach(function (input) {
        input.addEventListener("change", function () {
          updateFilterButton(input.getAttribute("data-filter-group"));
          renderCards();
        });
      });
      updateFilterButton(menu.getAttribute("data-filter-menu"));
    });
    document.addEventListener("click", function () {
      document.querySelectorAll(".filter-menu.open").forEach(function (menu) {
        menu.classList.remove("open");
        var trigger = menu.querySelector(".filter-trigger");
        if (trigger) trigger.setAttribute("aria-expanded", "false");
      });
    });
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
    meta.appendChild(pill(problem.type === "optimization" ? "Optimization" : "Satisfaction", null));

    card.appendChild(h3);
    card.appendChild(desc);
    card.appendChild(meta);
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
      ["Instances", "instances"]].forEach(function (item) {
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
      container.appendChild(row);
    });
  }

  function renderCards() {
    var container = document.getElementById("cards");
    var countEl = document.getElementById("result-count");
    if (!container || !window.DCP_DATA) return;

    var data = window.DCP_DATA.problems || [];
    var q = (document.getElementById("filter-q") || { value: "" }).value.trim().toLowerCase();
    var types = selectedFilterValues("type");
    var sources = selectedFilterValues("source");
    var instances = selectedFilterValues("instances");
    var frameworks = selectedFilterValues("framework");

    var filtered = data.filter(function (problem) {
      if (types.length && types.indexOf(problem.type || "satisfaction") === -1) return false;
      if (sources.length && sources.indexOf(problem.source) === -1) return false;
      if (instances.length) {
        var instanceType = problem.instances === 0 ? "none" : (problem.instances === 1 ? "single" : "multiple");
        if (instances.indexOf(instanceType) === -1) return false;
      }
      if (frameworks.length && frameworks.indexOf("any") === -1) {
        var problemFrameworks = problem.generatedFrameworks || [];
        var matchesFramework = frameworks.some(function (framework) {
          return framework === "none" ? problemFrameworks.length === 0 : problemFrameworks.indexOf(framework) !== -1;
        });
        if (!matchesFramework) return false;
      }
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
    initFilterMenus();
    var search = document.getElementById("filter-q");
    if (search) search.addEventListener("input", renderCards);
    var sort = document.getElementById("sort-by");
    if (sort) sort.addEventListener("change", function () {
      sortKey = sort.value;
      sortDirection = 1;
      renderCards();
    });
    var reset = document.getElementById("reset-filters");
    if (reset) reset.addEventListener("click", function () {
      var searchInput = document.getElementById("filter-q");
      if (searchInput) searchInput.value = "";
      document.querySelectorAll('input[data-filter-group]').forEach(function (input) {
        input.checked = false;
      });
      var anyFramework = document.querySelector('input[data-filter-group="framework"][value="any"]');
      if (anyFramework) anyFramework.checked = true;
      document.querySelectorAll(".filter-menu.open").forEach(function (menu) {
        menu.classList.remove("open");
        var trigger = menu.querySelector(".filter-trigger");
        if (trigger) trigger.setAttribute("aria-expanded", "false");
      });
      ["type", "source", "instances", "framework"].forEach(updateFilterButton);
      sortKey = "name";
      sortDirection = 1;
      if (sort) sort.value = "name";
      setViewMode("grid");
    });
    document.addEventListener("click", function (event) {
      var button = event.target.closest ? event.target.closest(".view-btn") : null;
      if (button) setViewMode(button.getAttribute("data-view"));
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
