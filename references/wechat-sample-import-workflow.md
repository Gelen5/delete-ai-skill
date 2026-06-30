# 微信公众号样文导入工作流

这个工作流用来把“公众号名称”接进 `Delete AI Skill` 的 style DNA 生成流程。

## 目标

把某个公众号的公开文章变成可供写作建模的样文素材。

## 推荐流程

### 第一步：发现文章

运行：

```powershell
python .\scripts\discover_wechat_articles.py --account-name "公众号名称" --output .\output\wechat-discovery.json --markdown-output .\output\wechat-discovery.md --csv-output .\output\wechat-discovery.csv --allow-fuzzy
```

如果 Windows 终端直接传中文参数有乱码，改用 UTF-8 文本文件更稳：

```powershell
python .\scripts\discover_wechat_articles.py --account-name-file .\account-name.txt --output .\output\wechat-discovery.json --markdown-output .\output\wechat-discovery.md --csv-output .\output\wechat-discovery.csv --allow-fuzzy
```

它会输出：

- 文章标题
- 来源公众号名
- 发布时间
- 搜狗跳转链接
- 最终微信文章链接

## 第二步：提取正文

优先尝试直接提取：

```powershell
python .\scripts\extract_wechat_article.py --url "微信文章链接" --json-output .\output\article-1.json --markdown-output .\output\article-1.md
```

如果脚本提示需要验证：

1. 在正常浏览器里打开那篇文章
2. 把页面另存为 HTML
3. 再运行：

```powershell
python .\scripts\extract_wechat_article.py --html-input ".\saved\article-1.html" --json-output .\output\article-1.json --markdown-output .\output\article-1.md
```

## 第三步：批量整理

把提取出来的 `.md` 或 `.txt` 放进同一个文件夹，例如：

```text
samples/
|- article-1.md
|- article-2.md
`- article-3.md
```

## 第四步：生成 style DNA

运行：

```powershell
python .\scripts\build_style_dna_from_folder.py --input-folder .\samples --output .\output\style_dna.wechat.json --author-label "公众号名称"
```

这样就把公众号样文真正接入了 style DNA 工作流。

## 适合怎么用

- 用公众号作者已有文风做仿写参考
- 为内容团队建立风格档案
- 为去 AI 味改写提供真实样文基线

## v1 边界

- 文章发现支持“输入公众号名称”
- 最终微信文章链接可自动解析
- 正文提取是 best-effort
- 遇到微信验证页时，走“浏览器保存 HTML 再导入”的兜底流程

这个边界是为了保证它真的能卖、能交付、能让买家用，而不是做一个看起来很猛但一跑就挂的承诺
