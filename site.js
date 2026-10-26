/* Progressive enhancements. Core navigation and contact links work without JS. */
(() => {
  const transitions = document.createElement('style');
  transitions.textContent = '@media (prefers-reduced-motion: no-preference) { @view-transition { navigation: auto; } }';
  document.head.append(transitions);

  const year = String(new Date().getFullYear());
  document.querySelectorAll('[data-year]').forEach(node => { node.textContent = year; });

  const buttons = [...document.querySelectorAll('[data-copy]')];
  const status = document.querySelector('.copy-status');
  if (!window.isSecureContext || !navigator.clipboard?.writeText || !status) return;

  buttons.forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const restoreFocus = document.activeElement === button;
      buttons.forEach(control => {
        control.disabled = true;
        delete control.dataset.copied;
      });
      status.textContent = '正在复制…';
      try {
        await navigator.clipboard.writeText(button.dataset.copy);
        button.dataset.copied = 'true';
        status.textContent = `已复制${button.dataset.copyLabel}。`;
      } catch {
        status.textContent = '未能复制，请长按上方账号或地址复制。';
      } finally {
        buttons.forEach(control => { control.disabled = false; });
        if (restoreFocus) button.focus({ preventScroll: true });
      }
    });
  });
})();
