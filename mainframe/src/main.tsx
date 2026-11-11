import { createRoot } from 'react-dom/client'
import './index.css'

function App() {
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
    <div className="cover-wordmark" aria-hidden="true">ethan.</div>
    <footer className="cover-footer"><span>保持好奇，实现想法。</span><span>© {new Date().getFullYear()} ethan</span></footer>
  </div>
}
createRoot(document.getElementById('root')!).render(<App />)
