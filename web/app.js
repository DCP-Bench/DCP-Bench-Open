(function () {
  "use strict";

  var sortKey = "name";
  var sortDirection = 1;
  var FILTER_GROUPS = ["type", "instances", "paradigm", "framework"];

  /* Names compare by code point, the order generate_site.py gives the
     problem pages' prev/next links. */
  function valueForSort(problem, key) {
    if (key === "instances") return problem.instances || 0;
    if (key === "models") return (problem.generatedFrameworks || []).length;
    return problem.id || "";
  }

  /* Ties on a count keep the problems in name order. */
  function compareProblems(a, b) {
    var av = valueForSort(a, sortKey);
    var bv = valueForSort(b, sortKey);
    var result = av < bv ? -1 : (av > bv ? 1 : 0);
    if (result) return result * sortDirection;
    return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
  }

  function setSort(key) {
    if (sortKey === key) {
      sortDirection *= -1;
    } else {
      sortKey = key;
      sortDirection = 1;
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
      instances: { id: "filter-instances", name: "Instances" },
      paradigm: { id: "filter-paradigm", name: "Paradigm" },
      framework: { id: "filter-framework", name: "Solver" }
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

  /* With one framework picked (index.html?framework=pychoco from the Solvers
     page), a problem link opens that framework's model rather than the
     reference model. */
  function problemHref(problem) {
    var href = "problems/" + problem.id + ".html";
    var framework = selectedFilterValues("framework")[0];
    if (framework && framework !== "any" && framework !== "none" &&
        (problem.generatedFrameworks || []).indexOf(framework) !== -1) {
      href += "?model=" + encodeURIComponent(framework);
    }
    return href;
  }

  var COLUMNS = [
    { label: "Name", key: "name" },
    { label: "Description" },
    { label: "Instances", key: "instances", num: true },
    { label: "Models", key: "models", num: true,
      title: "Solvers with an accepted generated model" }
  ];

  function el(tag, className) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    return node;
  }

  function renderTable(container, data) {
    var table = el("table", "plain problem-list");
    var headRow = el("tr");
    COLUMNS.forEach(function (column) {
      var th = el("th", column.num ? "num" : "");
      if (column.title) th.title = column.title;
      if (!column.key) {
        th.textContent = column.label;
      } else {
        var button = el("button", "list-sort");
        button.type = "button";
        button.textContent = column.label +
          (sortKey === column.key ? (sortDirection === 1 ? " \u2191" : " \u2193") : "");
        button.addEventListener("click", function () { setSort(column.key); });
        th.setAttribute("aria-sort", sortKey !== column.key ? "none" :
          (sortDirection === 1 ? "ascending" : "descending"));
        th.appendChild(button);
      }
      headRow.appendChild(th);
    });
    table.appendChild(el("thead")).appendChild(headRow);

    var body = table.appendChild(el("tbody"));
    data.forEach(function (problem) {
      var row = body.appendChild(el("tr"));
      var link = el("a");
      link.href = problemHref(problem);
      link.textContent = problem.id;
      row.appendChild(el("td", "list-name")).appendChild(link);
      row.appendChild(el("td", "list-desc")).appendChild(el("div", "clamp")).textContent = problem.snippet;
      /* No instances: the description fixes the data. */
      var instances = row.appendChild(el("td", "num"));
      instances.textContent = problem.instances ? String(problem.instances) : "\u2013";
      if (!problem.instances) instances.title = "No separate instances: the description fixes the data";
      row.appendChild(el("td", "num")).textContent = String((problem.generatedFrameworks || []).length);
    });
    container.appendChild(table);
  }

  function renderCards() {
    var countEl = document.getElementById("result-count");
    var sections = document.querySelectorAll(".problem-section");
    if (!sections.length || !window.DCP_DATA) return;

    var data = window.DCP_DATA.problems || [];
    var q = (document.getElementById("filter-q") || { value: "" }).value.trim().toLowerCase();
    var types = selectedFilterValues("type");
    var instances = selectedFilterValues("instances");
    var paradigms = selectedFilterValues("paradigm");
    var frameworks = selectedFilterValues("framework");

    var filtered = data.filter(function (problem) {
      if (types.length && types.indexOf(problem.type || "satisfaction") === -1) return false;
      if (instances.length) {
        var instanceType = problem.instances === 0 ? "none" : (problem.instances === 1 ? "single" : "multiple");
        if (instances.indexOf(instanceType) === -1) return false;
      }
      if (paradigms.length) {
        var problemParadigms = problem.paradigms || [];
        var matchesParadigm = paradigms.some(function (paradigm) {
          return problemParadigms.indexOf(paradigm) !== -1;
        });
        if (!matchesParadigm) return false;
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
    if (countEl) {
      countEl.textContent = filtered.length ? filtered.length + " of " + data.length + " problems"
        : "No problems match the current filters.";
    }
    Array.prototype.forEach.call(sections, function (section) {
      var kind = section.getAttribute("data-type");
      var rows = filtered.filter(function (problem) {
        return (problem.type || "satisfaction") === kind;
      });
      section.hidden = !rows.length;
      section.querySelector(".section-count").textContent = "(" + rows.length + ")";
      var container = section.querySelector(".problem-table");
      container.innerHTML = "";
      if (rows.length) renderTable(container, rows);
    });
  }

  /* Let another page hand the catalogue a filter, as paradigms.html does with
     index.html?paradigm=mip and index.html?framework=swipl_clpfd. Unknown
     values simply match no checkbox. The framework group is a radio group whose
     "Any" option is checked by default, so selecting one of its values clears
     that default without any extra handling here. */
  function applyQueryFilters() {
    if (!window.URLSearchParams) return;
    var params = new URLSearchParams(window.location.search);
    FILTER_GROUPS.forEach(function (group) {
      var values = params.getAll(group).join(",").split(",");
      values.forEach(function (value) {
        if (!value) return;
        var input = document.querySelector('input[data-filter-group="' + group +
          '"][value="' + value.replace(/"/g, "") + '"]');
        if (input) input.checked = true;
      });
      updateFilterButton(group);
    });
  }

  function initIndex() {
    if (!window.DCP_DATA) return;
    initFilterMenus();
    applyQueryFilters();
    var search = document.getElementById("filter-q");
    if (search) search.addEventListener("input", renderCards);
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
      FILTER_GROUPS.forEach(updateFilterButton);
      sortKey = "name";
      sortDirection = 1;
      renderCards();
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
    var model = window.URLSearchParams ? new URLSearchParams(window.location.search).get("model") : null;
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
      /* problems/x.html?model=pychoco opens that model's tab and scrolls to it. */
      var wanted = model && bar.querySelector('.tab-btn[data-tab="' + model.replace(/"/g, "") + '"]');
      if (wanted) {
        wanted.click();
        (group.closest(".page-section") || group).scrollIntoView();
      }
    });
  }

  /* Solvers page: a paradigm row expands to the solvers behind it. A link to
     #cp, or to anything inside that group, opens the group it lands in. One
     button shows or hides every group at once. */
  function initParadigms() {
    var groups = document.querySelectorAll("tbody.paradigm");
    if (!groups.length) return;
    var expandAll = document.querySelector(".expand-all");
    var toggles = Array.prototype.filter.call(groups, function (group) {
      return group.querySelector(".row-toggle[aria-expanded]");
    });

    function syncExpandAll() {
      if (!expandAll) return;
      var allOpen = toggles.every(function (group) {
        return !group.classList.contains("collapsed");
      });
      expandAll.textContent = allOpen ? "Hide all" : "Show all";
      expandAll.setAttribute("aria-pressed", allOpen ? "true" : "false");
    }

    function setOpen(group, open) {
      var btn = group.querySelector(".row-toggle[aria-expanded]");
      if (!btn) return;
      group.classList.toggle("collapsed", !open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      syncExpandAll();
    }

    if (expandAll) {
      expandAll.addEventListener("click", function () {
        var open = expandAll.getAttribute("aria-pressed") !== "true";
        toggles.forEach(function (group) { setOpen(group, open); });
      });
    }

    Array.prototype.forEach.call(groups, function (group) {
      var row = group.querySelector(".paradigm-row");
      row.addEventListener("click", function (event) {
        if (event.target.closest("a, .info-wrap")) return;
        setOpen(group, group.classList.contains("collapsed"));
      });
    });

    function openFromHash() {
      if (!location.hash) return;
      var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      var group = target && target.closest("tbody.paradigm");
      if (group) setOpen(group, true);
    }
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
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
    initParadigms();
    if (window.hljs) hljs.highlightAll();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
