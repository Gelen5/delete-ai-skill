# WeChat Article Exporter 适配器工作流

这个工作流把 `wechat-article-exporter` 接进 `Delete AI Skill`。

## 定位

这是当前仓库的公众号样文导入主方案。

它适合：

- 已经有 `wechat-article-exporter` 在线站点或私有部署
- 能拿到有效 `auth-key`
- 想按公众号名称批量导出 markdown
- 想把文章目录直接转成 `style_dna.json`

## 总体流程

1. 登录 `wechat-article-exporter`
2. 拿到 `auth-key`
3. 输入公众号名称
4. 通过 API 查询公众号
5. 获取公众号历史文章列表
6. 逐篇导出 markdown
7. 调用现有 style DNA 构建流程

## 前提

- 一个可用的 `wechat-article-exporter` 实例
  - 例如 `https://down.mptext.top`
  - 或你自己的私有部署地址
- 一个有效的 `auth-key`

## 如何拿 auth-key

按 `wechat-article-exporter` 的设计：

- 先在网站里扫码登录
- 然后在 API 页面查询当前 `auth-key`
- 调用 API 时通过 `X-Auth-Key` 请求头传入

## 一条命令导入

```powershell
python .\scripts\import_from_wechat_article_exporter.py `
  --base-url "https://down.mptext.top" `
  --auth-key "你的auth-key" `
  --account-name "公众号名称" `
  --output-dir .\output\wechat-samples `
  --style-dna-output .\output\style_dna.wechat.json
```

## 带关键词过滤

```powershell
python .\scripts\import_from_wechat_article_exporter.py `
  --base-url "https://down.mptext.top" `
  --auth-key "你的auth-key" `
  --account-name "公众号名称" `
  --keyword "AI" `
  --output-dir .\output\wechat-samples `
  --style-dna-output .\output\style_dna.wechat.json
```

## 会输出什么

- 一个 markdown 目录
- 一个 style DNA JSON 文件
- 可选的匹配公众号元数据 JSON

## 参数说明

- `--base-url`
  - `wechat-article-exporter` 实例地址
- `--auth-key`
  - 网站 API 密钥
- `--account-name`
  - 公众号名称或搜索关键字
- `--keyword`
  - 可选，文章标题/摘要/作者名过滤
- `--output-dir`
  - markdown 导出目录
- `--style-dna-output`
  - 最终风格档案输出路径
- `--max-articles`
  - 最多导出多少篇
- `--account-meta-output`
  - 可选，保存命中的公众号资料

## 与去 AI 味 workflow 的衔接

导出完成后，生成的 `style_dna.json` 就是后续改写流程的样文基线。

也就是说：

- `wechat-article-exporter` 负责拿样文
- `Delete AI Skill` 负责把样文变成风格资产，再用来改写 AI 草稿

## 为什么现在只保留这一条主链

因为这一条链：

- 可直接按公众号名称查询
- 可直接导出 markdown
- 与 style DNA 构建最顺
- 更接近可售卖产品里的“高级模式”

相比之下，旧的轻量模式更像兜底，不再作为当前产品主入口对外说明。
