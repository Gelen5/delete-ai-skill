# 导出文章网页版说明

这个网页版是给 `Delete AI Skill` 增加一个更直观的“公众号文章导出器”入口。

## 启动方式

```powershell
python .\scripts\start_exporter_web.py
```

启动后打开：

```text
http://127.0.0.1:8765
```

## 它能做什么

- 输入 `wechat-article-exporter` 地址
- 输入 `auth-key`
- 输入公众号名称
- 搜索公众号
- 拉文章列表
- 多选文章
- 导出一个 zip

zip 内包含：

- 选中文章的 markdown 文件
- `manifest.json`
- `style_dna.json`

## 这版的主要卡点

### 1. 登录态

最大的卡点不是网页本身，而是上游 `wechat-article-exporter` 的 `auth-key`。

如果 `auth-key` 失效：

- 搜号会失败
- 拉文章会失败
- 导出也会失败

### 2. 公众号命中不准

有些公众号名字太短、太泛、太口语化，会出现多结果或误匹配。

这版网页已经把候选列表展示出来，允许手动选号，避免完全自动误判。

### 3. 批量导出速度

导出 markdown 时，本地代理会逐篇请求上游接口。

所以：

- 选 5 到 20 篇体验最好
- 一次导几百篇会慢

### 4. 样式和排版

当前导出重点是 markdown 和 style DNA，不是做一个重运营后台。

所以这版偏：

- 实用
- 可跑
- 适合 first usable version

## 为什么不用纯前端

因为上游公开 API 没有给浏览器可直接使用的跨域响应头。

所以必须走一个本地小代理：

- 前端网页
- 本地 Python 服务
- Python 服务再去请求上游 exporter API

这样才能真正常用。
