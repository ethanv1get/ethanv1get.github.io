import { useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

if (typeof location !== 'undefined' && (location.hash === '#light' || location.hash === '#dark')) {
  document.documentElement.dataset.theme = location.hash.slice(1)
}

function App() {
  const photoDialog = useRef<HTMLDialogElement>(null)
  const [hasOpenedPhoto, setHasOpenedPhoto] = useState(false)
  const openDuck = () => {
    setHasOpenedPhoto(true)
    photoDialog.current?.showModal()
  }

  return (
    <div className="cover">
      <a className="skip" href="#main">跳到正文</a>
      <header className="cover-header">
        <a className="cover-brand" href="/" translate="no" aria-label="ethan. 首页">
          <img src="/assets/avatar.jpg" alt="" width="28" height="28" decoding="async" />
          <span>ethan<i aria-hidden="true">.</i></span>
        </a>
        <nav aria-label="顶部导航">
          <a href="/" aria-current="page">首页</a>
          <a href="/articles.html">文章</a>
          <a href="/works.html">作品</a>
          <a href="/about.html">关于</a>
          <a href="/contact.html">联系</a>
        </nav>
      </header>

      <main id="main" tabIndex={-1} className="cover-main">
        <div className="cover-intro">
          <div className="cover-who">
            <img
              className="cover-avatar"
              src="/assets/avatar.jpg"
              alt="ethan 的手写 e 头像"
              width="58"
              height="58"
              fetchPriority="high"
              decoding="async"
            />
            <div>
              <p className="cover-greeting">你好，我是 <span translate="no">ethan</span> <span aria-hidden="true">👋</span></p>
              <small>一个持续修订的思考现场</small>
            </div>
          </div>
          <h1>记录此刻，<br />也探索<mark>未知</mark>。</h1>
          <div className="cover-chips" aria-label="关注方向">
            <span>AI 工具</span>
            <span>技术实践</span>
            <span>生活观察</span>
          </div>
        </div>

        <div className="cover-index">
          <nav aria-label="主导航">
            <a href="/articles.html"><span>文章与记录</span><small>读一些文字 →</small></a>
            <a href="/works.html"><span>作品与工具</span><small>体验 Koin 记账 App →</small></a>
            <a href="/about.html"><span>关于 ethan</span><small>认识我 →</small></a>
            <a href="/contact.html"><span>联系</span><small>聊聊你的发现 →</small></a>
          </nav>
        </div>
      </main>

      <div className="cover-signature">
        <div className="cover-wordmark" aria-hidden="true">ethan<i>.</i></div>
        <button
          className="cover-keepsake"
          type="button"
          aria-label="放大小鸭子"
          aria-haspopup="dialog"
          title="放大小鸭子"
          onClick={openDuck}
        >
          <img
            src="/assets/duck-keepsake-320.webp"
            srcSet="/assets/duck-keepsake-160.webp 160w, /assets/duck-keepsake-320.webp 320w"
            sizes="(max-width: 700px) 84px, 140px"
            alt="戴粉色蝴蝶结、围着 FUN DAY 围兜的小鸭子"
            width="320"
            height="320"
            fetchPriority="high"
            decoding="async"
          />
        </button>
      </div>

      <footer className="cover-footer">
        <span>保持好奇，实现想法。</span>
        <span>© {new Date().getFullYear()} ethan</span>
      </footer>

      <dialog
        ref={photoDialog}
        className="keepsake-dialog"
        aria-label="小鸭子大图"
        onClick={event => {
          if (event.target === event.currentTarget) event.currentTarget.close()
        }}
      >
        <button className="keepsake-close" type="button" autoFocus onClick={() => photoDialog.current?.close()}>关闭</button>
        {hasOpenedPhoto && (
          <img
            src="/assets/duck-keepsake-large.webp"
            alt="戴粉色蝴蝶结、围着 FUN DAY 围兜的小鸭子大图"
            width="1024"
            height="1024"
            decoding="async"
          />
        )}
      </dialog>
    </div>
  )
}

createRoot(document.getElementById('root')!).render(<App />)
