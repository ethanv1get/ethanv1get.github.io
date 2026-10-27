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
python3 scripts/test_cms_pipeline.py
python3 scripts/publish.py
node scripts/serve.mjs _site --port 4416
```

浏览器打开 http://127.0.0.1:4416/ 。构建只用 Python 标准库，不需要安装网站运行依赖。

## 维护

- `.pages.yml`：写作表单和上传图片配置。
- `articles.json`：文章原始数据。
- `scripts/content.py`：日期、网址、分类和发布状态校验。
- `scripts/build.py`：页面模板；修改设计请改这里和 `style.css`。
- `scripts/publish.py`：构建干净的 `_site` 公共发布包。
- `.github/workflows/publish.yml`：保存内容后自动发布，GitHub Pages Source 为 GitHub Actions。
- `CNAME` 和现有域名绑定保留，不需要修改 DNS。

源码根目录的 HTML 为既有生成快照，自动发布以模板、文章数据和 `_site` 构建结果为准；不要把编辑生成文件当作文章发布流程。
