/* Progressive enhancement for the Koin Android share & download page.
   Works without JS via baked-in fallback links; enhances with WeChat detection,
   clipboard copy (with WebView fallback), and live version.json mirror race. */
(() => {
  const REPO = 'ethanv1get/koin';
  const FALLBACK_VERSION = '1.0.10';
  const RELEASE_PATH_RE = /^https:\/\/.+\/ethanv1get\/koin\/releases\/download\/v\d+\.\d+\.\d+\/Koin-v\d+\.\d+\.\d+-arm64\.apk$/;

  const ua = navigator.userAgent || '';
  const params = new URLSearchParams(location.search);
  const isWeChat = /MicroMessenger/i.test(ua) || params.get('preview') === 'wechat';
  const isInAppQQ = /\bQQ\/[\d.]+/i.test(ua) && !/QQBrowser/i.test(ua);
  const isBlockedWebView = isWeChat || isInAppQQ;

  const tipEl = document.getElementById('koin-wechat-tip');
  const downloadBtn = document.getElementById('koin-download-btn');
  const copyUrlBtn = document.getElementById('koin-copy-url');
  const copyPageBtn = document.getElementById('koin-copy-page');
  const statusEl = document.getElementById('koin-status');

  const setStatus = (msg) => {
    if (statusEl) statusEl.textContent = msg;
  };

  const copyText = async (text) => {
    if (window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch {
        // Fall through to legacy textarea copy for older mobile WebViews.
      }
    }
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      ta.style.pointerEvents = 'none';
      document.body.appendChild(ta);
      ta.select();
      ta.setSelectionRange(0, text.length);
      const ok = document.execCommand('copy');
      document.body.removeChild(ta);
      return ok;
    } catch {
      return false;
    }
  };

  if (isBlockedWebView && tipEl) {
    tipEl.hidden = false;
    if (downloadBtn) {
      downloadBtn.addEventListener('click', (event) => {
        event.preventDefault();
        tipEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setStatus('微信/QQ 内置浏览器无法直接下载 APK，请点右上角「···」选择「在浏览器打开」，或复制链接到系统浏览器下载。');
      });
    }
  }

  if (copyUrlBtn) {
    copyUrlBtn.addEventListener('click', async () => {
      const url = copyUrlBtn.dataset.copyUrl || (downloadBtn ? downloadBtn.href : '');
      if (!url) return;
      const ok = await copyText(url);
      setStatus(ok ? '已复制国内免翻下载直链，粘贴到手机浏览器即可直接下载。' : '未能自动复制，请长按下方任意线路链接复制。');
    });
  }

  if (copyPageBtn) {
    copyPageBtn.addEventListener('click', async () => {
      const shareUrl = 'https://ethanv1.top/koin.html';
      const ok = await copyText(shareUrl);
      setStatus(ok ? '已复制本页地址（https://ethanv1.top/koin.html），粘贴到系统浏览器打开即可下载。' : '未能自动复制，请点击右上角「···」在浏览器中打开。');
    });
  }

  const parseSemver = (v) => {
    const m = String(v || '').trim().replace(/^v/i, '').match(/^(\d+)\.(\d+)\.(\d+)$/);
    return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
  };

  const compareSemver = (a, b) => {
    const pa = parseSemver(a);
    const pb = parseSemver(b);
    if (!pa || !pb) return 0;
    for (let i = 0; i < 3; i += 1) {
      if (pa[i] !== pb[i]) return pa[i] - pb[i];
    }
    return 0;
  };

  const isTrustedApkUrl = (url) => typeof url === 'string' && RELEASE_PATH_RE.test(url.trim());

  const fetchJson = async (url, timeoutMs) => {
    const controller = typeof AbortController === 'function' ? new AbortController() : null;
    const timer = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;
    try {
      const res = await fetch(url, {
        cache: 'no-store',
        signal: controller ? controller.signal : undefined,
      });
      if (!res.ok) throw new Error(String(res.status));
      return await res.json();
    } finally {
      if (timer) clearTimeout(timer);
    }
  };

  const STORAGE_KEY = 'koin_manifest_v1';
  const SHA256_RE = /^[a-f0-9]{64}$/i;

  const formatDate = (iso) => {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '';
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  };

  const normalizeManifest = (data) => {
    if (!data || typeof data !== 'object') return null;
    if (typeof data.version === 'string' && parseSemver(data.version)) {
      const sha = typeof data.sha256 === 'string' ? data.sha256.trim().toLowerCase() : '';
      return {
        version: data.version.trim().replace(/^v/i, ''),
        notes: typeof data.notes === 'string' ? data.notes.trim() : '',
        sha256: SHA256_RE.test(sha) ? sha : '',
        downloadUrl: typeof data.downloadUrl === 'string' ? data.downloadUrl.trim() : '',
        downloadUrls: Array.isArray(data.downloadUrls) ? data.downloadUrls.filter(isTrustedApkUrl) : [],
        updatedAt: typeof data.updatedAt === 'string' ? data.updatedAt.trim() : '',
      };
    }
    if (typeof data.tag_name === 'string' && parseSemver(data.tag_name)) {
      return {
        version: data.tag_name.trim().replace(/^v/i, ''),
        notes: typeof data.body === 'string' ? data.body.trim() : '',
        sha256: '',
        downloadUrl: '',
        downloadUrls: [],
        updatedAt: typeof data.published_at === 'string' ? data.published_at.trim() : '',
      };
    }
    return null;
  };

  const mergeManifest = (current, incoming) => {
    if (!incoming || compareSemver(incoming.version, FALLBACK_VERSION) < 0) return null;
    if (!current) return incoming;
    const cmp = compareSemver(incoming.version, current.version);
    if (cmp > 0) return incoming;
    if (cmp < 0) return null;

    const merged = {
      version: current.version,
      notes: current.notes || incoming.notes,
      sha256: current.sha256 || incoming.sha256,
      downloadUrl: current.downloadUrl || incoming.downloadUrl,
      downloadUrls: current.downloadUrls.length >= incoming.downloadUrls.length
        ? current.downloadUrls
        : incoming.downloadUrls,
      updatedAt: current.updatedAt || incoming.updatedAt,
    };

    const changed =
      merged.notes !== current.notes ||
      merged.sha256 !== current.sha256 ||
      merged.downloadUrl !== current.downloadUrl ||
      merged.downloadUrls.length !== current.downloadUrls.length ||
      merged.updatedAt !== current.updatedAt;

    return changed ? merged : null;
  };

  const applyManifest = (manifest) => {
    const version = manifest.version;
    if (!parseSemver(version) || compareSemver(version, FALLBACK_VERSION) < 0) return;

    const originUrl = `https://github.com/${REPO}/releases/download/v${version}/Koin-v${version}-arm64.apk`;
    const candidates = [
      manifest.downloadUrl,
      ...(Array.isArray(manifest.downloadUrls) ? manifest.downloadUrls : []),
      `https://tvv.tw/${originUrl}`,
      `https://gh-proxy.org/${originUrl}`,
      `https://edgeone.gh-proxy.org/${originUrl}`,
      originUrl,
    ].filter(isTrustedApkUrl);

    const primaryUrl = candidates[0] || `https://tvv.tw/${originUrl}`;

    document.querySelectorAll('[data-koin-version]').forEach((node) => {
      node.textContent = `v${version}`;
    });

    if (manifest.updatedAt) {
      const dateStr = formatDate(manifest.updatedAt);
      if (dateStr) {
        document.querySelectorAll('[data-koin-updated]').forEach((node) => {
          node.textContent = `更新于 ${dateStr}`;
          if (node.tagName === 'TIME') node.setAttribute('datetime', dateStr);
        });
      }
    }

    if (downloadBtn) {
      downloadBtn.href = primaryUrl;
      downloadBtn.textContent = `下载 Android 安装包（v${version}）`;
    }

    if (copyUrlBtn) {
      copyUrlBtn.dataset.copyUrl = primaryUrl;
    }

    if (manifest.notes) {
      const notesEl = document.querySelector('[data-koin-notes]');
      if (notesEl) notesEl.textContent = manifest.notes;
    }

    const shaEl = document.querySelector('[data-koin-sha256]');
    if (shaEl) {
      if (manifest.sha256) {
        shaEl.textContent = manifest.sha256;
      } else if (compareSemver(version, FALLBACK_VERSION) > 0) {
        shaEl.textContent = '同步中…';
      }
    }

    const mirrorMap = {
      tvv: `https://tvv.tw/${originUrl}`,
      ghproxy: `https://gh-proxy.org/${originUrl}`,
      edgeone: `https://edgeone.gh-proxy.org/${originUrl}`,
      origin: originUrl,
      release: `https://github.com/${REPO}/releases/tag/v${version}`,
    };

    Object.entries(mirrorMap).forEach(([key, href]) => {
      const link = document.querySelector(`[data-koin-mirror="${key}"]`);
      if (link) link.href = href;
    });
  };

  let bestManifest = null;

  const commitManifest = (incoming, persist) => {
    const next = mergeManifest(bestManifest, incoming);
    if (!next) return;
    bestManifest = next;
    applyManifest(next);
    if (persist) {
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        // Ignore private-browsing or quota errors.
      }
    }
  };

  try {
    const rawCache = sessionStorage.getItem(STORAGE_KEY);
    if (rawCache) {
      const cached = normalizeManifest(JSON.parse(rawCache));
      if (cached) commitManifest(cached, false);
    }
  } catch {
    // Ignore malformed or restricted sessionStorage.
  }

  const syncLatestVersion = () => {
    const bust = Date.now();
    const raw = `https://raw.githubusercontent.com/${REPO}/main/version.json`;
    const api = `https://api.github.com/repos/${REPO}/releases/latest`;
    const sources = [
      `https://tvv.tw/${raw}?t=${bust}`,
      `https://gh-proxy.org/${raw}?t=${bust}`,
      `https://edgeone.gh-proxy.org/${raw}?t=${bust}`,
      `${raw}?t=${bust}`,
      api,
      `https://tvv.tw/${api}`,
      `https://cdn.jsdmirror.com/gh/${REPO}@main/version.json?t=${bust}`,
    ];

    sources.forEach((src) => {
      fetchJson(src, 6000)
        .then((data) => {
          const normalized = normalizeManifest(data);
          if (normalized) commitManifest(normalized, true);
        })
        .catch(() => {});
    });
  };

  syncLatestVersion();
})();
