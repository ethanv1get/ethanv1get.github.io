# ethan.

记录此刻，也探索未知。一个关于思考、技术与生活的个人空间。

网站：https://ethanv1.top/

纯静态 HTML/CSS/JavaScript，无运行依赖。

## 维护

文章数据在 articles.json；共享页面模板在 scripts/build.py；样式在 style.css。
修改后运行 python3 scripts/build.py，并运行 python3 scripts/check.py 验证。
本地预览：node scripts/serve.mjs . --port 4400。

文章、技术、生活、关于、联系和旧文章地址均保留。开站文《给想法一个开始的地方》已正式发布。
CNAME 和 .nojekyll 沿用现有配置。提交到 main 会触发 GitHub Pages 发布。



## 文章发布日期规则

每篇正式文章在 `articles.json` 中必须填写 `datePublished`，格式为 `YYYY-MM-DD`；首页、文章列表、分类和详情页统一显示“发布于 YYYY年M月D日”。日期也用于文章的结构化数据。

此字段表示首次正式发布日期，后续改样式、修改正文或重新构建时不要改成当天。草稿可以暂不填写，正式发布前必须补齐；构建器会拒绝缺失或无效的日期，不会自动猜测。

已有开站文正式发布于 2026-10-24，依据提交 `58486602b6344925670bdeaa96714503e794974f`（2026-10-24 13:13:17，Asia/Shanghai）。不再展示预计阅读时长。
