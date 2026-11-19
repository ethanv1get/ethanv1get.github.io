# ethan.

记录此刻，也探索未知。一个关于思考、技术与生活的个人空间。

网站：https://ethanv1.top/
写作后台：https://app.pagescms.org/

## 日常发布

用 GitHub 登录 Pages CMS，选择本仓库的 `main` 分支，打开「文章管理」。填写标题、网址、分类、正文和首次发布日期，关闭草稿后保存，GitHub Actions 会自动生成并发布网站。

完整步骤见 [发布文章指南](发布文章指南.md)。首次登录需要将 Pages CMS GitHub App 授权给这个网站仓库。

## 草稿与日期

草稿不生成网页，取消发布会从网站移除文章入口及详情。仓库是公开的，GitHub 中的草稿原文仍公开，请勿保存私密内容。

正式文章必须填写 `datePublished`（`YYYY-MM-DD`）；修改正文或样式不会自动更改首次发布日期。现有开站文的正式发布日期是 2026-10-24。

## 本地检查与预览

```sh
npm ci --prefix mainframe
npm run build --prefix mainframe
python3 scripts/test_cms_pipeline.py
python3 scripts/publish.py
node scripts/serve.mjs _site --port 4416
```

浏览器打开 http://127.0.0.1:4416/ 。首页需要 Node.js 构建，分页构建仍只用 Python 标准库。

## 邮件订阅

在 [Buttondown](https://buttondown.com/) 完成注册、邮箱验证和发信审核，将确认过的用户名填入 `newsletter.json` 的 `buttondown_username`。文章列表和正文末尾会出现「邮件订阅更新」，表单直接提交到 Buttondown。读者需在确认邮件中点击订阅，退订由 Buttondown 的邮件页脚处理。名单和密钥存放在服务商及 GitHub Secrets 中。

只看本地布局可运行 `ETHAN_EMAIL_PREVIEW=1 python3 scripts/publish.py`，尚未配置用户名时，预览中的表单会显示待接入状态。设置用户名后重新构建即可检查真实提交地址。

先通过 Buttondown 后台的 Preview / Send draft 给站主发一封预览，主题带 `[PREVIEW]`。也可从已设置 `BUTTONDOWN_API_KEY` 环境变量的终端运行 `python3 scripts/notify_email.py --test-to '你的邮箱'`。这个命令使用现有的公开文章，创建私有草稿并只向指定地址发送预览。收到真实测试邮件并获站主确认后再安排上线。

正式启用时，在 GitHub Actions Secrets 中配置 `BUTTONDOWN_API_KEY`，在 Variables 中设置开启订阅前最后一次正式发布的完整提交 SHA `EMAIL_NOTIFY_BASE_SHA`。确认预览后设定 `EMAIL_NOTIFY_ENABLED=true`，启用通知流程。Buttondown 的免费定价目前覆盖前 100 位活跃订阅者，按每天最多向全体发送一封邮件计算，实际发布频率需符合所选套餐。

通知流程等正式部署成功后才运行。它以基准提交中已公开的文章为界，核对新文章的线上地址、标题和首次发布日期。每篇通知使用独立的 `email-notified/` 标签和 Buttondown 幂等键防重，修改旧文或重新部署不会再次发送。通知采用站点摘要和原文链接，保留 Buttondown 默认邮件页脚的退订功能。

服务商接受请求表示进入发送流程，实际收信需要到邮箱核验。若创建草稿被明确拒绝，会释放标签以便修复配置后重试。如果创建草稿或发布时网络结果不明确，会保留标签并使工作流失败。先在 Buttondown 核对对应 `article-文章短名` 的草稿和发送记录，再决定手动发布草稿或释放该条标签重试。

## 维护

- `.pages.yml`：写作表单和上传图片配置。
- `articles.json`：文章原始数据。
- `scripts/content.py`：日期、网址、分类和发布状态校验。
- `scripts/build.py`：页面模板；修改设计请改这里和 `style.css`。
- `mainframe/`：单屏刊物封面首页的源码。
- `scripts/publish.py`：构建干净的 `_site` 公共发布包。
- `.github/workflows/publish.yml`：保存内容后自动发布，GitHub Pages Source 为 GitHub Actions。
- `CNAME` 和现有域名绑定保留，不需要修改 DNS。

源码根目录的 HTML 为既有生成快照，自动发布以模板、文章数据和 `_site` 构建结果为准；不要把编辑生成文件当作文章发布流程。发布脚本会用 `mainframe/` 构建后的首页覆盖生成快照，文章、关于、联系等分页继续由 Python 模板生成。
