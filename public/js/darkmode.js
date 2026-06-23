// Theme toggle — wires the #darkSwitch checkbox to the `.dark` class on <html>.
// The initial class is applied by an inline script in <head> (prevents a flash
// of the wrong theme); this file only handles interaction + keeping state in sync.
(function () {
  var toggle = document.getElementById("darkSwitch");
  if (!toggle) return; // pages without the toggle (e.g. 404) simply opt out

  var root = document.documentElement;

  function setTheme(on) {
    root.classList.toggle("dark", on);
    toggle.checked = on;
    try {
      localStorage.setItem("theme", on ? "dark" : "light");
    } catch (e) {}
  }

  // Sync the checkbox with whatever the head script already applied.
  toggle.checked = root.classList.contains("dark");

  toggle.addEventListener("change", function () {
    setTheme(toggle.checked);
  });

  // Follow the OS preference only when the user hasn't chosen explicitly.
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", function (e) {
      if (localStorage.getItem("theme") === null) setTheme(e.matches);
    });
})();
