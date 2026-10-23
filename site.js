/* Progressive enhancements. Navigation, categories and article links work without JS. */
(() => {
  // Enable native page transitions only in script-capable browsers.
  // Navigation remains immediately usable when scripts are disabled.
  const transitions = document.createElement('style');
  transitions.textContent = '@media (prefers-reduced-motion: no-preference) { @view-transition { navigation: auto; } }';
  document.head.append(transitions);
  const year = String(new Date().getFullYear());
  document.querySelectorAll('[data-year]').forEach(node => { node.textContent = year; });
})();
