(function () {
  "use strict";

  var sortKey = "name";
  var sortDirection = 1;
  var FILTER_GROUPS = ["instances", "paradigm", "framework"];
  /* The catalogue shows one problem type at a time, as a tab. */
  var TYPES = ["optimization", "satisfaction"];
  var activeType = TYPES[0];
  /* With solvers picked, the catalogue shows the problems they have a model
     for ("yes") or the ones none of them has ("no"). */
  var modelledMode = "yes";

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

  var FILTER_NAMES = { instances: "Instances", paradigm: "Paradigm", framework: "Solver" };

  /* A filter in use reads its choice and is marked, so a narrowed list
     never looks like the whole catalogue. */
  function updateFilterButton(group) {
    var values = selectedFilterValues(group);
    var button = document.getElementById("filter-" + group);
    if (!button || !FILTER_NAMES[group]) return;
    var label = FILTER_NAMES[group] + ": ";
    if (!values.length) {
      label += "All";
    } else if (values.length === 1) {
      var input = document.querySelector('input[data-filter-group="' + group + '"][value="' + values[0] + '"]');
      label += input ? input.parentElement.textContent.trim() : "1 selected";
    } else {
      label += values.length + " selected";
    }
    button.textContent = label;
    button.classList.toggle("has-value", values.length > 0);
  }

  function closeMenus() {
    document.querySelectorAll(".filter-menu.open").forEach(function (menu) {
      menu.classList.remove("open");
      var trigger = menu.querySelector(".filter-trigger");
      if (trigger) trigger.setAttribute("aria-expanded", "false");
    });
  }

  function initFilterMenus() {
    document.querySelectorAll(".filter-menu").forEach(function (menu) {
      menu.addEventListener("click", function (event) { event.stopPropagation(); });
      var trigger = menu.querySelector(".filter-trigger");
      if (trigger) {
        trigger.addEventListener("click", function () {
          var open = !menu.classList.contains("open");
          closeMenus();
          menu.classList.toggle("open", open);
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
    document.addEventListener("click", closeMenus);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenus();
    });
  }

  /* The catalogue's state lives in its URL, so a filtered view can be shared
     and the "All problems" link on a problem page comes back to it. */
  var CATALOGUE_KEY = "dcp-catalogue";

  function currentQuery() {
    var params = [];
    var q = (document.getElementById("filter-q") || { value: "" }).value.trim();
    if (q) params.push("q=" + encodeURIComponent(q));
    FILTER_GROUPS.forEach(function (group) {
      var values = selectedFilterValues(group);
      if (values.length) params.push(group + "=" + values.map(encodeURIComponent).join(","));
    });
    if (modelledMode === "no" && selectedFilterValues("framework").length) params.push("modelled=no");
    if (sortKey !== "name" || sortDirection !== 1) {
      params.push("sort=" + (sortDirection === 1 ? "" : "-") + sortKey);
    }
    return params.join("&");
  }

  /* Reset clears the filters, search and sort; the tab stays where it is. */
  function syncState() {
    var query = currentQuery();
    var reset = document.getElementById("reset-filters");
    if (reset) reset.disabled = !query;
    if (activeType !== TYPES[0]) query = "type=" + activeType + (query ? "&" + query : "");
    if (window.history && history.replaceState) {
      history.replaceState(null, "", window.location.pathname + (query ? "?" + query : ""));
    }
    try { sessionStorage.setItem(CATALOGUE_KEY, window.location.href); } catch (e) { /* private mode */ }
  }

  /* With solvers picked (index.html?framework=choco_python from the Solvers
     page), a problem link opens the first picked solver's model the problem
     has, rather than the reference model. */
  function problemHref(problem) {
    var href = "problems/" + problem.id + ".html";
    var has = problem.generatedFrameworks || [];
    var framework = selectedFilterValues("framework").filter(function (solver) {
      return has.indexOf(solver) !== -1;
    })[0];
    if (framework) href += "?model=" + encodeURIComponent(framework);
    return href;
  }

  /* Long ids may break after an underscore, never inside a word. */
  function breakable(node, text) {
    text.split("_").forEach(function (part, i, parts) {
      node.appendChild(document.createTextNode(part + (i < parts.length - 1 ? "_" : "")));
      if (i < parts.length - 1) node.appendChild(document.createElement("wbr"));
    });
    return node;
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
      breakable(link, problem.id);
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
    var instances = selectedFilterValues("instances");
    var paradigms = selectedFilterValues("paradigm");
    var frameworks = selectedFilterValues("framework");

    var filtered = data.filter(function (problem) {
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
      if (q) {
        /* The whole description is searched, not just the shown snippet. */
        if (problem.haystack === undefined) {
          problem.haystack = (problem.id + " " + (problem.text || problem.snippet)).toLowerCase();
        }
        if (problem.haystack.indexOf(q) === -1) return false;
      }
      return true;
    });

    var switcher = document.querySelector(".mode-switch");
    if (frameworks.length) {
      var modelled = function (problem) {
        var has = problem.generatedFrameworks || [];
        return frameworks.some(function (framework) { return has.indexOf(framework) !== -1; });
      };
      var split = { yes: filtered.filter(modelled), no: filtered.filter(function (problem) { return !modelled(problem); }) };
      filtered = split[modelledMode];
      if (switcher) {
        switcher.querySelectorAll(".mode-btn").forEach(function (btn) {
          var mode = btn.getAttribute("data-mode");
          btn.classList.toggle("active", mode === modelledMode);
          btn.setAttribute("aria-pressed", mode === modelledMode ? "true" : "false");
          btn.querySelector(".tab-count").textContent = split[mode].length;
        });
      }
    }
    if (switcher) switcher.hidden = !frameworks.length;

    filtered.sort(compareProblems);
    if (countEl) {
      countEl.textContent = filtered.length === data.length ? data.length + " problems"
        : filtered.length + " of " + data.length + " problems match";
    }
    var byType = {};
    TYPES.forEach(function (kind) {
      byType[kind] = filtered.filter(function (problem) {
        return (problem.type || "satisfaction") === kind;
      });
    });
    document.querySelectorAll(".type-tab").forEach(function (tab) {
      var kind = tab.getAttribute("data-type");
      var active = kind === activeType;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
      tab.querySelector(".tab-count").textContent = byType[kind].length;
    });
    Array.prototype.forEach.call(sections, function (section) {
      var kind = section.getAttribute("data-type");
      section.hidden = kind !== activeType;
      var container = section.querySelector(".problem-table");
      container.innerHTML = "";
      if (kind !== activeType) return;
      if (byType[kind].length) {
        renderTable(container, byType[kind]);
        return;
      }
      /* Nothing here, but a search may well match in the other tab. */
      var empty = container.appendChild(el("p", "desc empty-state"));
      empty.textContent = "No " + kind + " problems match. ";
      var other = TYPES.filter(function (type) { return type !== kind && byType[type].length; })[0];
      if (other) {
        var jump = empty.appendChild(el("button", "link-btn"));
        jump.type = "button";
        jump.textContent = "Show the " + byType[other].length + " matching " + other + " problem" +
          (byType[other].length === 1 ? "" : "s") + ".";
        jump.addEventListener("click", function () { showType(other); });
      }
    });
    syncState();
  }

  function showType(kind) {
    if (TYPES.indexOf(kind) === -1) return;
    activeType = kind;
    renderCards();
  }

  /* Restore the catalogue from its URL, which is also how another page hands
     it a filter: paradigms.html links index.html?framework=swipl_clpfd.
     Unknown values simply match no checkbox. */
  function applyQueryFilters() {
    if (!window.URLSearchParams) return;
    var params = new URLSearchParams(window.location.search);
    var search = document.getElementById("filter-q");
    if (search && params.get("q")) search.value = params.get("q");
    if (TYPES.indexOf(params.get("type")) !== -1) activeType = params.get("type");
    if (params.get("modelled") === "no") modelledMode = "no";
    var sort = params.get("sort") || "";
    var key = sort.replace(/^-/, "");
    if (COLUMNS.some(function (column) { return column.key === key; })) {
      sortKey = key;
      sortDirection = sort.charAt(0) === "-" ? -1 : 1;
    }
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
    document.querySelectorAll(".type-tab").forEach(function (tab) {
      tab.addEventListener("click", function () { showType(tab.getAttribute("data-type")); });
    });
    document.querySelectorAll(".mode-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        modelledMode = btn.getAttribute("data-mode");
        renderCards();
      });
    });
    var reset = document.getElementById("reset-filters");
    if (reset) reset.addEventListener("click", function () {
      var searchInput = document.getElementById("filter-q");
      if (searchInput) searchInput.value = "";
      document.querySelectorAll('input[data-filter-group]').forEach(function (input) {
        input.checked = false;
      });
      closeMenus();
      FILTER_GROUPS.forEach(updateFilterButton);
      sortKey = "name";
      sortDirection = 1;
      modelledMode = "yes";
      renderCards();
    });
    renderCards();
  }

  function escHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /* Where a URL in prose ends: before trailing punctuation, and before a
     closing parenthesis it did not open. url_end in generate_site.py does the
     same for the metadata links. */
  function urlEnd(url) {
    var end = url.length;
    while (end) {
      var ch = url.charAt(end - 1);
      var head = url.slice(0, end);
      if (".,;:!?'".indexOf(ch) !== -1 ||
          (ch === ")" && head.split("(").length < head.split(")").length)) {
        end -= 1;
      } else {
        break;
      }
    }
    return end;
  }

  /* Escape text and wrap its URLs in links. */
  function linkify(text) {
    var out = "";
    var last = 0;
    var pattern = /https?:\/\/[^\s<>"]+/g;
    var match;
    while ((match = pattern.exec(text))) {
      var url = match[0].slice(0, urlEnd(match[0]));
      out += escHtml(text.slice(last, match.index)) + '<a href="' + escHtml(url).replace(/"/g, "&quot;") +
        '" target="_blank" rel="noopener">' + escHtml(url) + "</a>";
      last = match.index + url.length;
      pattern.lastIndex = last;
    }
    return out + escHtml(text.slice(last));
  }

  /* $$..$$, \[..\], \(..\), and $..$ only where it cannot be a price:
     "$20 and $5" stays text. MATH_RE in generate_site.py matches the same,
     to decide which pages load KaTeX. */
  var MATH = /\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$(?=[^\s\d$])([^$\n]*?[^\s$\\])\$(?!\d)/g;

  /* Some descriptions escape their backslashes for Markdown: \\times for
     \times, \\* for a plain asterisk. */
  function renderMath(source, tex, display) {
    if (!window.katex) return escHtml(source);
    tex = tex.replace(/\\\\\*/g, "*").replace(/\\\\(?=[A-Za-z])/g, "\\");
    return katex.renderToString(tex, { displayMode: display, throwOnError: false });
  }

  /* Math is set aside before Markdown runs, so that a_1 and a_m are not
     read as emphasis, and put back as KaTeX afterwards. */
  function initMarkdown() {
    if (!window.marked) return;
    document.querySelectorAll(".md-desc").forEach(function (el) {
      var maths = [];
      var text = el.textContent.replace(MATH, function (all, block, bracket, paren, dollar) {
        var display = block !== undefined || bracket !== undefined;
        maths.push(renderMath(all, block || bracket || paren || dollar, display));
        return "MATHTOKEN" + (maths.length - 1) + "END";
      });
      text = text.replace(/\\\\\*/g, "\\*");
      el.innerHTML = marked.parse(linkify(text)).replace(/MATHTOKEN(\d+)END/g, function (token, i) {
        return maths[Number(i)];
      });
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

  function initBackLink() {
    var crumb = document.querySelector(".crumb");
    if (!crumb) return;
    var left;
    try { left = sessionStorage.getItem(CATALOGUE_KEY); } catch (e) { return; }
    if (left && left.split("?")[0].replace(/index\.html$/, "") ===
        crumb.href.split("?")[0].replace(/index\.html$/, "")) {
      crumb.href = left;
    }
  }

  /* Problem pages: the left and right arrow keys step through the models in
     the order of the pills, wrapping round, while the Models section is on
     screen. On a device with a keyboard, a hint says so whenever the section
     is on screen, until the reader closes it. */
  var HINT_CLOSED = "dcp-model-keys-hint-closed";

  function stored(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  function store(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* private mode */ }
  }

  function initModelKeys() {
    var group = document.querySelector(".model-group");
    if (!group) return;
    var section = group.closest(".page-section") || group;
    var buttons = Array.prototype.slice.call(group.querySelectorAll(".model-picker .tab-btn"));
    if (buttons.length < 2) return;

    /* The address names the model on show, so a copied link opens it. */
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (!window.history || !history.replaceState) return;
        var name = btn.getAttribute("data-tab");
        var query = name === "ground_truth" ? "" : "?model=" + encodeURIComponent(name);
        history.replaceState(null, "", window.location.pathname + query + window.location.hash);
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.defaultPrevented) return;
      if (event.target.closest && event.target.closest("input, textarea, select, [contenteditable]")) return;
      var box = group.getBoundingClientRect();
      if (box.top >= window.innerHeight || box.bottom <= 0) return;
      var current = 0;
      buttons.forEach(function (btn, i) {
        if (btn.classList.contains("active")) current = i;
      });
      var step = event.key === "ArrowRight" ? 1 : -1;
      buttons[(current + step + buttons.length) % buttons.length].click();
      /* A shorter model could leave the reader below it: bring the pills back. */
      if (section.getBoundingClientRect().top < 0) section.scrollIntoView();
      event.preventDefault();
    });

    var keyboard = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    if (stored(HINT_CLOSED) || !keyboard || !window.IntersectionObserver) return;
    var hint = document.createElement("div");
    hint.className = "key-hint";
    hint.setAttribute("role", "status");
    hint.innerHTML = '<kbd>←</kbd><kbd>→</kbd><span>switch models</span>' +
      '<button type="button" aria-label="Close this hint">×</button>';
    document.body.appendChild(hint);
    /* Any part of the section on screen counts: a long model can be taller
       than the window, so a share of it would never be visible. */
    var observer = new IntersectionObserver(function (entries) {
      hint.classList.toggle("shown", entries[entries.length - 1].isIntersecting);
    });
    observer.observe(group);
    hint.querySelector("button").addEventListener("click", function () {
      store(HINT_CLOSED, "1");
      observer.disconnect();
      hint.remove();
    });
  }

  function init() {
    initIndex();
    initBackLink();
    initMarkdown();
    initTabs();
    initModelKeys();
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
