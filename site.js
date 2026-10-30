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

/* The same video behavior as the homepage: mouse scrub on desktop, motion on phones. */
(() => {
  const video = document.querySelector('[data-subpage-video]');
  if (!video) return;
  const playButton = document.querySelector('.subpage-play');
  const media = window.matchMedia('(max-width: 800px), (pointer: coarse)');
  let previousX = null;
  let targetTime = 0;
  let seeking = false;

  const seekToTarget = () => {
    if (media.matches || seeking || !Number.isFinite(video.duration) || video.duration <= 0) return;
    if (Math.abs(video.currentTime - targetTime) < .025) return;
    seeking = true;
    try { video.currentTime = targetTime; } catch { seeking = false; }
  };
  const playMobile = () => {
    if (!media.matches) return;
    video.play().then(() => { if (playButton) playButton.hidden = true; })
      .catch(() => { if (playButton) playButton.hidden = false; });
  };
  const updateMode = () => {
    previousX = null;
    targetTime = video.currentTime || 0;
    video.loop = media.matches;
    video.autoplay = media.matches;
    if (media.matches) playMobile();
    else {
      video.pause();
      if (playButton) playButton.hidden = true;
    }
  };

  window.addEventListener('mousemove', event => {
    if (media.matches) return;
    const currentX = event.clientX;
    if (previousX === null) { previousX = currentX; return; }
    const delta = currentX - previousX;
    previousX = currentX;
    if (!Number.isFinite(video.duration) || video.duration <= 0) return;
    targetTime = Math.max(0, Math.min(video.duration, targetTime + delta / window.innerWidth * .8 * video.duration));
    seekToTarget();
  });
  video.addEventListener('loadedmetadata', () => { targetTime = video.currentTime; seekToTarget(); });
  video.addEventListener('seeked', () => { seeking = false; seekToTarget(); });
  video.addEventListener('canplay', () => { if (media.matches && video.paused) playMobile(); });
  playButton?.addEventListener('click', playMobile);
  document.querySelector('.page-heading, .article-masthead')?.addEventListener('touchstart', playMobile, { passive: true });
  media.addEventListener('change', updateMode);
  updateMode();
})();
