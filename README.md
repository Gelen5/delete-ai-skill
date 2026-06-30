# Delete AI Skill

`Delete AI Skill` 是一套可售卖、可交付的中文写作 skill 工具包。

它的目标不是“保证通过某个检测器”，而是帮助用户把 AI 草稿改得更像真人表达，把历史文章沉淀成可复用的个人风格资产，并形成稳定的写作工作流。

适用场景：

- 公众号长文
- 小红书文案
- 博客文章
- 教程内容
- 个人品牌写作
- 内容团队协作

不适用场景：

- 学术论文
- 法律文书
- 医疗文书
- 新闻报道
- 任何需要承诺“必过检测”的场景

## 仓库包含内容

- `SKILL.md`
  - 核心 skill 工作流，负责生成和改写
- `scripts/extract_style_dna.py`
  - 本地风格提取脚本，把样文转成 `style_dna.json`
- `references/`
  - 风格模板、场景模板、QA 清单
- `examples/`
  - 示例输入、示例输出、示例风格档案
- `INSTALL.md`
  - 安装与使用说明
- `SELLING.md`
  - 产品定位和售卖建议
- `SALES_PAGE_CN.md`
  - 中文销售页
- `DEMO_SCRIPT_CN.md`
  - 演示文案
- `FAQ_CN.md`
  - 买家常见问题
- `DELIVERY_CHECKLIST_CN.md`
  - 交付清单

## 这套产品解决什么问题

很多 AI 草稿的问题不是“写不出来”，而是：

- 太像模板
- 句子太整齐
- 有信息但没体温
- 看起来完整，却不像作者本人会写的话
- 团队多人协作时风格不统一

`Delete AI Skill` 解决的重点是：

- 让内容更像一个具体的人在写
- 让旧文章变成可复用的风格资产
- 让改写不再靠感觉，而是靠流程
- 让团队围绕同一套风格标准协作

## 推荐售卖定位

这套产品更适合卖成：

- 个人风格写作 skill
- 低 AI 味改写工具包
- 作者风格资产化工作流
- 内容团队统一风格方案

不建议卖成：

- 保证通过某检测器
- 100% 过检工具
- 绕过平台识别产品

更稳的销售承诺应该是：

- 强化个人风格
- 降低模板化痕迹
- 提高自然度
- 提升内容交付稳定性

## 快速开始

1. 准备 `3-10` 篇真实样文
2. 运行风格提取脚本：

```powershell
python .\scripts\extract_style_dna.py --input .\examples\input-sample-1.md --output .\examples\style_dna.generated.json
```

3. 根据生成的 `style_dna.json`，配合 `SKILL.md` 进行写作或改写
4. 用 `references/humanization-qa-checklist.md` 做最后 QA

## 微信公众号样文导入

当前仓库对外采用 `wechat-article-exporter` 适配器方案。

也就是：

1. 通过 `wechat-article-exporter` 按公众号名称查询
2. 拉取历史文章列表
3. 直接导出 markdown
4. 生成该公众号的 `style_dna.json`

工作流说明见：

- `references/wechat-article-exporter-adapter.md`

核心脚本：

- `scripts/import_from_wechat_article_exporter.py`
- `scripts/build_style_dna_from_folder.py`

买家照抄版命令说明：

- `BUYER_QUICKSTART_CN.md`

## 目录结构

```text
Delete AI Skill/
|- SKILL.md
|- INSTALL.md
|- SELLING.md
|- SALES_PAGE_CN.md
|- DEMO_SCRIPT_CN.md
|- FAQ_CN.md
|- DELIVERY_CHECKLIST_CN.md
|- references/
|- scripts/
`- examples/
```

## 交付优势

这套仓库按“第一版就能卖”来设计，特点是：

- 上手门槛低
- 可直接打包交付
- 可本地运行风格提取
- 可继续升级成插件或网页工具

## 中文售卖素材入口

如果你要直接拿这个仓库去卖，优先看这些文件：

- `SALES_PAGE_CN.md`
- `DEMO_SCRIPT_CN.md`
- `FAQ_CN.md`
- `DELIVERY_CHECKLIST_CN.md`

## 一句话总结

`Delete AI Skill` 卖的不是“骗过谁”，而是“让内容更像你自己，并且能稳定重复做出来”。
