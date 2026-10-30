import { useEffect, useRef, useState, type RefObject } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

const VIDEO_URL = '/assets/hero-video.mp4'
const MESSAGE = '记录思考，探索技术，也收藏生活里值得记住的瞬间。'
const navigation = [['文章', '/articles.html'], ['关于', '/about.html'], ['联系', '/contact.html']] as const

function useTypewriter(text: string) {
  const [displayed, setDisplayed] = useState('')
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { setDisplayed(text); return }
    let interval: ReturnType<typeof setInterval> | undefined
    const delay = window.setTimeout(() => {
      let index = 0
      interval = window.setInterval(() => {
        index += 1
        setDisplayed(text.slice(0, index))
        if (index >= text.length) window.clearInterval(interval)
      }, 34)
    }, 450)
    return () => { window.clearTimeout(delay); if (interval) window.clearInterval(interval) }
  }, [text])
  return { displayed, done: displayed.length === text.length }
}

function useMouseScrub(videoRef: RefObject<HTMLVideoElement | null>, enabled: boolean) {
  const prevX = useRef<number | null>(null)
  const targetTime = useRef(0)
  const seeking = useRef(false)
  const seekToTarget = () => {
    const video = videoRef.current
    if (!enabled || !video || seeking.current || !Number.isFinite(video.duration) || video.duration <= 0) return
    if (Math.abs(video.currentTime - targetTime.current) < 0.025) return
    seeking.current = true
    try { video.currentTime = targetTime.current } catch { seeking.current = false }
  }
  useEffect(() => {
    if (enabled) targetTime.current = videoRef.current?.currentTime ?? 0
    const onMove = (event: MouseEvent) => {
      if (!enabled) return
      const video = videoRef.current
      const currentX = event.clientX
      if (prevX.current === null) { prevX.current = currentX; return }
      const delta = currentX - prevX.current
      prevX.current = currentX
      if (!video || !Number.isFinite(video.duration) || video.duration <= 0) return
      targetTime.current = Math.max(0, Math.min(video.duration, targetTime.current + (delta / window.innerWidth) * 0.8 * video.duration))
      seekToTarget()
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [videoRef, enabled])
  return {
    onSeeked: () => { seeking.current = false; if (enabled) seekToTarget() },
    onLoadedMetadata: () => { targetTime.current = videoRef.current?.currentTime ?? 0; if (enabled) seekToTarget() },
  }
}

function App() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [mobileMotion, setMobileMotion] = useState(() => window.matchMedia('(max-width: 800px), (pointer: coarse)').matches)
  const videoHandlers = useMouseScrub(videoRef, !mobileMotion)
  const { displayed, done } = useTypewriter(MESSAGE)
  const [menuOpen, setMenuOpen] = useState(false)
  const [needsPlay, setNeedsPlay] = useState(false)
  useEffect(() => {
    const media = window.matchMedia('(max-width: 800px), (pointer: coarse)')
    const update = () => setMobileMotion(media.matches)
    media.addEventListener('change', update)
    return () => media.removeEventListener('change', update)
  }, [])
  useEffect(() => {
    const video = videoRef.current
    if (!video) return
    if (mobileMotion) void video.play().then(() => setNeedsPlay(false)).catch(() => setNeedsPlay(true))
    else { video.pause(); setNeedsPlay(false) }
  }, [mobileMotion])
  const startMobileVideo = () => {
    if (!mobileMotion) return
    const video = videoRef.current
    if (video && video.paused) void video.play().then(() => setNeedsPlay(false)).catch(() => setNeedsPlay(true))
  }
  useEffect(() => {
    if (!menuOpen) return
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === 'Escape') setMenuOpen(false) }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [menuOpen])

  return <>
    <header className="hero-header">
      <a href="/" className="hero-brand" aria-label="ethan. 首页">ethan.</a>
      <nav aria-label="主导航" className="hero-nav">{navigation.map(([label, href]) => <a href={href} key={label}>{label}</a>)}</nav>
      <button className="menu-toggle" type="button" aria-label={menuOpen ? '关闭菜单' : '打开菜单'} aria-expanded={menuOpen} aria-controls="mobile-menu" onClick={() => setMenuOpen(value => !value)}><span className={menuOpen ? 'open' : ''} /><span className={menuOpen ? 'open' : ''} /><span className={menuOpen ? 'open' : ''} /></button>
    </header>
    <nav id="mobile-menu" aria-label="手机导航" aria-hidden={!menuOpen} className={`mobile-menu ${menuOpen ? 'is-open' : ''}`}>{navigation.map(([label, href]) => <a href={href} key={label} tabIndex={menuOpen ? 0 : -1} onClick={() => setMenuOpen(false)}>{label}</a>)}</nav>
    <main>
      <section className="video-hero" aria-labelledby="hero-title" onTouchStart={startMobileVideo}>
        <video ref={videoRef} src={VIDEO_URL} poster="/assets/hero-poster.jpg" muted playsInline autoPlay={mobileMotion} loop={mobileMotion} preload="auto" aria-hidden="true" className="hero-video" onCanPlay={startMobileVideo} {...videoHandlers} />
        <div className="video-shade" aria-hidden="true" />
        {needsPlay && <button type="button" className="mobile-play" onClick={startMobileVideo} aria-label="播放背景动画">▶</button>}
        <div className="hero-inner"><div className="hero-copy">
          <p className="hero-intro">一个关于思考、技术与生活的个人空间。</p>
          <h1 id="hero-title">记录此刻，<br />也探索未知。</h1>
          <p className="hero-typewriter">{displayed}{!done && <span className="typing-cursor" aria-hidden="true" />}</p>
          <div className="hero-actions"><a className="hero-primary" href="/articles.html">浏览文章</a><a className="hero-secondary" href="/about.html">关于 ethan</a></div>
        </div></div>
      </section>
    </main>
  </>
}

createRoot(document.getElementById('root')!).render(<App />)
