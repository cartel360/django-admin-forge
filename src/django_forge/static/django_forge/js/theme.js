(function () {
  var KEY = "django-forge-theme";
  var THEME_OPTIONS = ["light", "dark", "system"];

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

  document.addEventListener("DOMContentLoaded", function () {
    var mode = getStoredThemeMode();
    applyThemeMode(mode);
    setupAccountMenu();
    setupToasts();

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
