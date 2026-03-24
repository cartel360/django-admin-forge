(function () {
  var KEY = "django-forge-theme";

  function getPreferredTheme() {
    var saved = localStorage.getItem(KEY);
    if (saved === "light" || saved === "dark") {
      return saved;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem(KEY, theme);
  }

  function toggleTheme() {
    var current = document.documentElement.classList.contains("dark") ? "dark" : "light";
    applyTheme(current === "dark" ? "light" : "dark");
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(getPreferredTheme());
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      button.addEventListener("click", toggleTheme);
    });
  });
})();
