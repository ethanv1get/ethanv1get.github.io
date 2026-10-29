import React, { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260826_041744_63efcd78-bf7d-4039-99e2-2461e8a61903.mp4'
const EMAIL = 'hello@mainframe.co'
const MESSAGE = 'Glad you stopped in. Good taste tends to find us. Now, what are we building?'

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
  ['Labs', '/tech.html'], ['Studio', '/about.html'], ['Openings', '/contact.html'], ['Shop', '/articles.html'],
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

  const mailLink = (subject: string) => `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}`
  const pillClass = 'inline-flex items-center justify-center rounded-full border border-black/10 bg-white px-4 sm:px-5 py-[0.3em] mx-[0.2em] mb-[0.4em] whitespace-nowrap text-[13px] sm:text-[15px] text-black hover:bg-black hover:text-white transition-colors duration-200'
  const copyEmail = async () => {
    try {
      await navigator.clipboard.writeText(EMAIL)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch { setCopied(false) }
  }

  return <>
    <video ref={videoRef} src={VIDEO_URL} muted playsInline preload="auto" aria-hidden="true" className="fixed inset-0 z-0 h-full w-full object-cover object-[70%_center]" {...videoHandlers} />
    <nav aria-label="Main navigation" className="fixed top-0 z-10 flex w-full items-center justify-between px-5 py-4 sm:px-8 sm:py-5">
      <a href="/" className="flex items-center gap-3 text-white" aria-label="Mainframe home">
        <span className="text-[21px] sm:text-[26px] tracking-tight" style={{ fontFamily: 'var(--font-heading)' }}>Mainframe®</span>
        <span aria-hidden="true" className="select-none text-[25px] sm:text-[30px] tracking-[-0.02em]">✳︎</span>
      </a>
      <div className="hidden md:flex text-[23px] text-white" aria-label="Sections">
        {links.map(([label, href], index) => <React.Fragment key={label}><a href={href} className="transition-opacity hover:opacity-60">{label}</a>{index < links.length - 1 && <span>,&nbsp;</span>}</React.Fragment>)}
      </div>
      <a href={mailLink('Hello Mainframe')} className="hidden md:inline text-[23px] text-white underline underline-offset-2 transition-opacity hover:opacity-60">Get in touch</a>
      <button type="button" aria-label={menuOpen ? 'Close menu' : 'Open menu'} aria-expanded={menuOpen} aria-controls="mobile-menu" onClick={() => setMenuOpen(value => !value)} className="relative z-10 flex flex-col gap-[5px] md:hidden">
        <span className={`h-[2px] w-6 bg-white transition-transform duration-300 ${menuOpen ? 'translate-y-[7px] rotate-45' : ''}`} />
        <span className={`h-[2px] w-6 bg-white transition-opacity duration-300 ${menuOpen ? 'opacity-0' : ''}`} />
        <span className={`h-[2px] w-6 bg-white transition-transform duration-300 ${menuOpen ? '-translate-y-[7px] -rotate-45' : ''}`} />
      </button>
    </nav>
    <div id="mobile-menu" aria-hidden={!menuOpen} className={`fixed inset-0 z-[9] flex flex-col items-start justify-center gap-8 bg-black/90 px-8 backdrop-blur-md transition-opacity duration-300 md:hidden ${menuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
      {links.map(([label, href]) => <a key={label} href={href} tabIndex={menuOpen ? 0 : -1} onClick={() => setMenuOpen(false)} className="text-[32px] font-medium text-white">{label}</a>)}
      <a href={mailLink('Hello Mainframe')} tabIndex={menuOpen ? 0 : -1} className="text-[32px] font-medium text-white underline underline-offset-2">Get in touch</a>
    </div>
    <main className="relative z-[1] flex h-screen min-h-[550px] flex-col justify-end overflow-hidden px-5 pb-12 sm:px-8 md:justify-center md:px-10 md:pb-0">
      <div className="relative z-10 max-w-xl">
        <h1 className="pointer-events-none mb-5 select-none text-white sm:mb-6" style={{ fontSize: 'clamp(18px, 4vw, 26px)', lineHeight: 1.3, fontWeight: 400, filter: 'blur(4px)' }}>Hey there, meet A.R.I.A,<br />Mainframe&apos;s Adaptive Response Interface Agent</h1>
        <p className="mb-5 min-h-[54px] text-white sm:mb-6" style={{ fontSize: 'clamp(18px, 4vw, 26px)', lineHeight: 1.35, fontWeight: 400 }}>{displayed}{!done && <span aria-hidden="true" className="typing-cursor ml-[2px] inline-block h-[1.1em] w-[2px] align-middle bg-white" />}</p>
        <div className={`pills-enter flex flex-wrap gap-y-1 ${pillsVisible ? 'is-visible' : ''}`}>
          <a className={pillClass} href={mailLink('Pitch an idea')}>Pitch us an idea</a>
          <a className={pillClass} href={mailLink('Working at Mainframe')}>Come work here</a>
          <a className={pillClass} href={mailLink('A brief hello')}>Send a brief hello</a>
          <a className={pillClass} href="/about.html">See how we operate</a>
          <button type="button" onClick={copyEmail} aria-label={copied ? 'Email copied' : `Copy ${EMAIL}`} className="mx-[0.2em] mb-[0.4em] inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full border border-white bg-transparent px-4 py-[0.3em] text-[13px] text-white transition-colors duration-200 hover:bg-white hover:text-black sm:gap-3 sm:px-5 sm:text-[15px]">
            <span>Reach us: <u className="underline-offset-1">{EMAIL}</u></span>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.2" aria-hidden="true"><rect x="3.5" y="3.5" width="7" height="7" rx=".5" /><path d="M8.5 3.5V2a.5.5 0 0 0-.5-.5H2a.5.5 0 0 0-.5.5v6a.5.5 0 0 0 .5.5h1.5" /></svg>
          </button>
          <span role="status" aria-live="polite" className="sr-only">{copied ? 'Email copied to clipboard' : ''}</span>
        </div>
      </div>
    </main>
  </>
}

createRoot(document.getElementById('root')!).render(<App />)
