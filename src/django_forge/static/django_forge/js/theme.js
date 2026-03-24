(function () {
  var KEY = "django-forge-theme";
  var THEME_OPTIONS = ["light", "dark", "system"];

  function getSearchIndex() {
    var node = document.getElementById("forge-search-index");
    if (!node) return [];
    try {
      var parsed = JSON.parse(node.textContent || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch (_e) {
      return [];
    }
  }

  function getStoredThemeMode() {
    var saved = localStorage.getItem(KEY);
    if (THEME_OPTIONS.indexOf(saved) >= 0) {
      return saved;
    }
    var fallback = window.__forgeDefaultTheme || "system";
    return THEME_OPTIONS.indexOf(fallback) >= 0 ? fallback : "system";
  }

  function resolveTheme(mode) {
    if (mode === "system") {
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    return mode;
  }

  function applyThemeMode(mode) {
    var theme = resolveTheme(mode);
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem(KEY, mode);
    syncThemeOptionState(mode);
  }

  function syncThemeOptionState(mode) {
    document.querySelectorAll(".forge-theme-option").forEach(function (button) {
      var active = button.getAttribute("data-set-theme") === mode;
      button.classList.toggle("forge-theme-option-active", active);
    });
  }

  function setupAccountMenu() {
    var toggle = document.querySelector("[data-account-menu-toggle]");
    var menu = document.querySelector("[data-account-menu]");
    if (!toggle || !menu) return;

    function closeMenu() {
      menu.classList.add("hidden");
      toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", function () {
      var isHidden = menu.classList.contains("hidden");
      menu.classList.toggle("hidden", !isHidden);
      toggle.setAttribute("aria-expanded", isHidden ? "true" : "false");
    });

    document.addEventListener("click", function (event) {
      if (!menu.contains(event.target) && !toggle.contains(event.target)) {
        closeMenu();
      }
    });
  }

  function setupToasts() {
    document.querySelectorAll("[data-toast]").forEach(function (toast) {
      var close = toast.querySelector("[data-toast-close]");
      var dismiss = function () {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-4px)";
        setTimeout(function () {
          if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
          }
        }, 180);
      };

      toast.style.transition = "opacity 180ms ease, transform 180ms ease";
      if (close) close.addEventListener("click", dismiss);
      setTimeout(dismiss, 4200);
    });
  }

  function setupSidebarSearch() {
    var input = document.querySelector("[data-sidebar-search]");
    var nav = document.querySelector("[data-sidebar-nav]");
    var results = document.querySelector("[data-sidebar-search-results]");
    if (!input) return;

    var index = getSearchIndex();
    var items = Array.prototype.slice.call(nav.querySelectorAll("[data-search-item]"));
    function renderResults(term) {
      if (!results) return [];
      if (!term) {
        results.classList.add("hidden");
        results.innerHTML = "";
        return [];
      }
      var matches = index
        .filter(function (item) {
          return (item.label || "").toLowerCase().indexOf(term.toLowerCase()) >= 0;
        })
        .slice(0, 6);
      if (!matches.length) {
        results.classList.remove("hidden");
        results.innerHTML = '<div class="px-3 py-2 text-xs text-slate-500">No results found.</div>';
        return matches;
      }
      results.classList.remove("hidden");
      results.innerHTML = matches
        .map(function (item) {
          return (
            '<a class="forge-search-result-item block rounded-md px-3 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" href="' +
            item.url +
            '">' +
            item.label +
            "</a>"
          );
        })
        .join("");
      return matches;
    }

    input.addEventListener("input", function () {
      var term = (input.value || "").trim().toLowerCase();
      if (items.length) {
        items.forEach(function (item) {
          var match = item.textContent.toLowerCase().indexOf(term) >= 0;
          item.style.display = match || !term ? "" : "none";
        });
      }
      renderResults(term);
    });

    input.addEventListener("keydown", function (event) {
      if (event.key !== "Enter") return;
      var matches = renderResults((input.value || "").trim());
      if (!matches.length) return;
      window.location.href = matches[0].url;
    });

    document.addEventListener("click", function (event) {
      if (!results) return;
      if (!results.contains(event.target) && event.target !== input) {
        results.classList.add("hidden");
      }
    });
  }

  function setupGlobalSearch() {
    var input = document.querySelector("[data-global-search]");
    var results = document.querySelector("[data-global-search-results]");
    if (!input || !results) return;

    var links = getSearchIndex()
      .map(function (item) {
        return { label: item.label || "", href: item.url || "" };
      })
      .filter(function (item) {
        return item.label && item.href;
      });

    function render(term) {
      if (!term) {
        results.classList.add("hidden");
        results.innerHTML = "";
        return [];
      }

      var matches = links
        .filter(function (item) {
          return item.label.toLowerCase().indexOf(term.toLowerCase()) >= 0;
        })
        .slice(0, 8);

      if (!matches.length) {
        results.classList.remove("hidden");
        results.innerHTML = '<div class="px-3 py-2 text-xs text-slate-500">No results found.</div>';
        return matches;
      }

      results.classList.remove("hidden");
      results.innerHTML = matches
        .map(function (item) {
          return (
            '<a class="forge-search-result-item block rounded-md px-3 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800" href="' +
            item.href +
            '">' +
            item.label +
            "</a>"
          );
        })
        .join("");
      return matches;
    }

    input.addEventListener("input", function () {
      render((input.value || "").trim());
    });

    input.addEventListener("keydown", function (event) {
      if (event.key !== "Enter") return;
      var term = (input.value || "").trim();
      var matches = render(term);
      if (!matches.length) return;
      window.location.href = matches[0].href;
    });

    document.addEventListener("click", function (event) {
      if (!results.contains(event.target) && event.target !== input) {
        results.classList.add("hidden");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var mode = getStoredThemeMode();
    applyThemeMode(mode);
    setupAccountMenu();
    setupToasts();
    setupSidebarSearch();
    setupGlobalSearch();

    document.querySelectorAll("[data-set-theme]").forEach(function (button) {
      button.addEventListener("click", function () {
        applyThemeMode(button.getAttribute("data-set-theme") || "system");
      });
    });

    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
      if (getStoredThemeMode() === "system") {
        applyThemeMode("system");
      }
    });
  });
})();
