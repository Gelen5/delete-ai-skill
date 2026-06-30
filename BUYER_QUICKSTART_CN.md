# 买家版一键命令说明

这份说明是给不会命令行的买家直接照抄用的。

## 你要先准备什么

需要准备 4 样东西：

1. 一个可用的 `wechat-article-exporter` 网站地址
   - 例如：`https://down.mptext.top`
2. 一个有效的 `auth-key`
3. 你想导入的公众号名称
4. 电脑里已经安装 `Python 3.9+`

## 第一步：打开命令行

在本仓库文件夹空白处：

1. 按住 `Shift`
2. 点击鼠标右键
3. 选择“在此处打开 PowerShell 窗口”

## 第二步：直接复制这一条命令

把下面命令里的 3 个地方改掉再运行：

- `你的 exporter 地址`
- `你的 auth-key`
- `你的公众号名称`

```powershell
python .\scripts\import_from_wechat_article_exporter.py --base-url "你的 exporter 地址" --auth-key "你的 auth-key" --account-name "你的公众号名称" --output-dir ".\output\wechat-samples" --style-dna-output ".\output\style_dna.wechat.json"
```

## 示例

如果你的参数是：

- exporter 地址：`https://down.mptext.top`
- auth-key：`abc123`
- 公众号名称：`丁香医生`

那就运行：

```powershell
python .\scripts\import_from_wechat_article_exporter.py --base-url "https://down.mptext.top" --auth-key "abc123" --account-name "丁香医生" --output-dir ".\output\wechat-samples" --style-dna-output ".\output\style_dna.wechat.json"
```

## 如果你只想抓某个主题的文章

比如你只想抓标题里和 `AI` 相关的文章，就加 `--keyword`：

```powershell
python .\scripts\import_from_wechat_article_exporter.py --base-url "https://down.mptext.top" --auth-key "你的 auth-key" --account-name "你的公众号名称" --keyword "AI" --output-dir ".\output\wechat-samples" --style-dna-output ".\output\style_dna.wechat.json"
```

## 跑完后你会看到什么

成功后会得到两类结果：

1. `.\output\wechat-samples\`
   - 里面是一批导出的 markdown 文章
2. `.\output\style_dna.wechat.json`
   - 这就是后续去 AI 味改写要用的风格档案

## 下一步怎么用

拿到 `style_dna.wechat.json` 后，就可以把它作为样文风格基线，接进 `Delete AI Skill` 的改写流程。

## 最常见的报错

### 1. auth-key 无效

表现：

- 提示登录失效
- 提示认证失败
- 查不到公众号列表

处理：

- 回 `wechat-article-exporter` 网站重新登录
- 重新拿一遍 `auth-key`

### 2. 公众号名称搜不到

处理：

- 换更完整的公众号名称
- 不要只输太短的词
- 先在 `wechat-article-exporter` 网站里手动试一下同样的名字

### 3. Python 不能运行

表现：

- `python` 不是内部或外部命令

处理：

- 先安装 Python
- 安装时勾选“Add Python to PATH”

## 最短版

买家如果只想看一句话，就给他这句：

```powershell
python .\scripts\import_from_wechat_article_exporter.py --base-url "https://down.mptext.top" --auth-key "你的 auth-key" --account-name "你的公众号名称" --output-dir ".\output\wechat-samples" --style-dna-output ".\output\style_dna.wechat.json"
```
