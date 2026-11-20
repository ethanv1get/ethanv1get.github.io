import { useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

function App() {
  const photoDialog = useRef<HTMLDialogElement>(null)
  const [hasOpenedPhoto, setHasOpenedPhoto] = useState(false)

  return <div className="cover">
    <a className="skip" href="#main">跳到正文</a>
    <header className="cover-header"><span>ethan 的个人网站</span><a href="https://t.me/ETHANV1">在 Telegram 找我</a></header>
    <main id="main" tabIndex={-1} className="cover-main">
      <div className="cover-intro"><p className="cover-annotation">[ PERSONAL SITE // 2026 ]</p><p className="cover-kicker">思考 / 技术 / 生活</p><h1>记录此刻，<br/>也探索未知。</h1><p className="cover-meta"><span className="status-dot" />一个持续修订的思考现场。</p></div>
      <div className="cover-index"><nav aria-label="主导航">
        <a href="/articles.html"><span>文章与记录</span><small>读一些文字</small></a>
        <a href="/about.html"><span>关于 ethan</span><small>认识我</small></a>
        <a href="/contact.html"><span>联系</span><small>聊聊你的发现</small></a>
      </nav></div>
    </main>
    <div className="cover-signature">
      <div className="cover-wordmark" aria-hidden="true">ethan.</div>
      <button
        className="cover-keepsake"
        type="button"
        aria-label="放大小鸭子"
        aria-haspopup="dialog"
        title="放大小鸭子"
        onClick={() => {
          setHasOpenedPhoto(true)
          photoDialog.current?.showModal()
        }}
      >
        <img
          src="/assets/duck-keepsake-320.webp"
          srcSet="/assets/duck-keepsake-160.webp 160w, /assets/duck-keepsake-320.webp 320w"
          sizes="(max-width: 700px) 84px, 148px"
          alt="戴粉色蝴蝶结、围着 FUN DAY 围兜的小鸭子"
          width="320"
          height="320"
          fetchPriority="high"
          decoding="async"
        />
      </button>
    </div>
    <footer className="cover-footer"><span>保持好奇，实现想法。</span><span>© {new Date().getFullYear()} ethan</span></footer>
    <dialog
      ref={photoDialog}
      className="keepsake-dialog"
      aria-label="小鸭子大图"
      onClick={event => {
        if (event.target === event.currentTarget) event.currentTarget.close()
      }}
    >
      <button className="keepsake-close" type="button" autoFocus onClick={() => photoDialog.current?.close()}>关闭</button>
      {hasOpenedPhoto && <img src="/assets/duck-keepsake-large.webp" alt="戴粉色蝴蝶结、围着 FUN DAY 围兜的小鸭子大图" width="1024" height="1024" decoding="async" />}
    </dialog>
  </div>
}
createRoot(document.getElementById('root')!).render(<App />)
