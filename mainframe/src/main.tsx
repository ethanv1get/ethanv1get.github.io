import React, { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260826_041744_63efcd78-bf7d-4039-99e2-2461e8a61903.mp4'
const TELEGRAM_HANDLE = '@ETHANV1'
const MESSAGE = '记录思考，探索技术，也收藏生活里值得记住的瞬间。'

function useTypewriter(text: string, speed = 38, startDelay = 600) {
  const [displayed, setDisplayed] = useState('')
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setDisplayed(text)
      return
    }
    let interval: ReturnType<typeof setInterval> | undefined
    const delay = window.setTimeout(() => {
      let index = 0
      interval = window.setInterval(() => {
        index += 1
        setDisplayed(text.slice(0, index))
        if (index >= text.length) window.clearInterval(interval)
      }, speed)
    }, startDelay)
    return () => { window.clearTimeout(delay); if (interval) window.clearInterval(interval) }
  }, [text, speed, startDelay])
  return { displayed, done: displayed.length === text.length }
}

function useMouseScrub(videoRef: React.RefObject<HTMLVideoElement | null>) {
  const prevX = useRef<number | null>(null)
  const targetTime = useRef(0)
  const seeking = useRef(false)

  const seekToTarget = () => {
    const video = videoRef.current
    if (!video || seeking.current || !Number.isFinite(video.duration) || video.duration <= 0) return
    if (Math.abs(video.currentTime - targetTime.current) < 0.025) return
    seeking.current = true
    try { video.currentTime = targetTime.current } catch { seeking.current = false }
  }

  useEffect(() => {
    const onMove = (event: MouseEvent) => {
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
  }, [videoRef])

  return {
    onSeeked: () => { seeking.current = false; seekToTarget() },
    onLoadedMetadata: () => { targetTime.current = videoRef.current?.currentTime ?? 0; seekToTarget() },
  }
}

const links = [
  ['文章', '/articles.html'], ['技术', '/tech.html'], ['生活', '/life.html'], ['关于', '/about.html'],
] as const

function App() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const videoHandlers = useMouseScrub(videoRef)
  const { displayed, done } = useTypewriter(MESSAGE)
  const [menuOpen, setMenuOpen] = useState(false)
  const [pillsVisible, setPillsVisible] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => setPillsVisible(true), 400)
    return () => window.clearTimeout(timer)
  }, [])
  useEffect(() => {
    if (!menuOpen) return
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === 'Escape') setMenuOpen(false) }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [menuOpen])

  const pillClass = 'inline-flex items-center justify-center rounded-full border border-black/10 bg-white px-4 sm:px-5 py-[0.3em] mx-[0.2em] mb-[0.4em] whitespace-nowrap text-[13px] sm:text-[15px] text-black hover:bg-black hover:text-white transition-colors duration-200'
  const copyTelegram = async () => {
    try {
      await navigator.clipboard.writeText(TELEGRAM_HANDLE)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch { setCopied(false) }
  }

  return <>
    <video ref={videoRef} src={VIDEO_URL} muted playsInline preload="auto" aria-hidden="true" className="fixed inset-0 z-0 h-full w-full object-cover object-[70%_center]" {...videoHandlers} />
    <nav aria-label="主导航" className="fixed top-0 z-10 flex w-full items-center justify-between px-5 py-4 sm:px-8 sm:py-5">
      <a href="/" className="flex items-center gap-3 text-white" aria-label="ethan. 首页">
        <span className="text-[21px] sm:text-[26px] tracking-tight" style={{ fontFamily: 'var(--font-heading)' }}>ethan.</span>
        <span aria-hidden="true" className="select-none text-[25px] sm:text-[30px] tracking-[-0.02em]">✳︎</span>
      </a>
      <div className="hidden md:flex text-[23px] text-white" aria-label="网站栏目">
        {links.map(([label, href], index) => <React.Fragment key={label}><a href={href} className="transition-opacity hover:opacity-60">{label}</a>{index < links.length - 1 && <span>,&nbsp;</span>}</React.Fragment>)}
      </div>
      <a href="/contact.html" className="hidden md:inline text-[23px] text-white underline underline-offset-2 transition-opacity hover:opacity-60">联系我</a>
      <button type="button" aria-label={menuOpen ? '关闭菜单' : '打开菜单'} aria-expanded={menuOpen} aria-controls="mobile-menu" onClick={() => setMenuOpen(value => !value)} className="relative z-10 flex flex-col gap-[5px] md:hidden">
        <span className={`h-[2px] w-6 bg-white transition-transform duration-300 ${menuOpen ? 'translate-y-[7px] rotate-45' : ''}`} />
        <span className={`h-[2px] w-6 bg-white transition-opacity duration-300 ${menuOpen ? 'opacity-0' : ''}`} />
        <span className={`h-[2px] w-6 bg-white transition-transform duration-300 ${menuOpen ? '-translate-y-[7px] -rotate-45' : ''}`} />
      </button>
    </nav>
    <div id="mobile-menu" aria-hidden={!menuOpen} className={`fixed inset-0 z-[9] flex flex-col items-start justify-center gap-8 bg-black/90 px-8 backdrop-blur-md transition-opacity duration-300 md:hidden ${menuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
      {links.map(([label, href]) => <a key={label} href={href} tabIndex={menuOpen ? 0 : -1} onClick={() => setMenuOpen(false)} className="text-[32px] font-medium text-white">{label}</a>)}
      <a href="/contact.html" tabIndex={menuOpen ? 0 : -1} className="text-[32px] font-medium text-white underline underline-offset-2">联系我</a>
    </div>
    <main className="relative z-[1] flex h-screen flex-col justify-end overflow-hidden px-5 pb-12 sm:px-8 md:justify-center md:px-10 md:pb-0">
      <div className="relative z-10 max-w-xl">
        <h1 className="pointer-events-none mb-5 select-none text-white sm:mb-6" style={{ fontSize: 'clamp(18px, 4vw, 26px)', lineHeight: 1.3, fontWeight: 400, filter: 'blur(4px)' }}>你好，我是 ethan。<br />记录此刻，也探索未知。</h1>
        <p className="mb-5 min-h-[54px] text-white sm:mb-6" style={{ fontSize: 'clamp(18px, 4vw, 26px)', lineHeight: 1.35, fontWeight: 400 }}>{displayed}{!done && <span aria-hidden="true" className="typing-cursor ml-[2px] inline-block h-[1.1em] w-[2px] align-middle bg-white" />}</p>
        <div className={`pills-enter flex flex-wrap gap-y-1 ${pillsVisible ? 'is-visible' : ''}`}>
          <a className={pillClass} href="/articles.html">浏览文章</a>
          <a className={pillClass} href="/tech.html">技术文章</a>
          <a className={pillClass} href="/life.html">生活记录</a>
          <a className={pillClass} href="/about.html">关于 ethan</a>
          <button type="button" onClick={copyTelegram} aria-label={copied ? '已复制 Telegram 用户名' : `复制 Telegram 用户名 ${TELEGRAM_HANDLE}`} className="mx-[0.2em] mb-[0.4em] inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full border border-white bg-transparent px-4 py-[0.3em] text-[13px] text-white transition-colors duration-200 hover:bg-white hover:text-black sm:gap-3 sm:px-5 sm:text-[15px]">
            <span>Telegram: <u className="underline-offset-1">{TELEGRAM_HANDLE}</u></span>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.2" aria-hidden="true"><rect x="3.5" y="3.5" width="7" height="7" rx=".5" /><path d="M8.5 3.5V2a.5.5 0 0 0-.5-.5H2a.5.5 0 0 0-.5.5v6a.5.5 0 0 0 .5.5h1.5" /></svg>
          </button>
          <span role="status" aria-live="polite" className="sr-only">{copied ? 'Telegram 用户名已复制' : ''}</span>
        </div>
      </div>
    </main>
  </>
}

createRoot(document.getElementById('root')!).render(<App />)
