const state = {
  selectedAccount: null,
  articles: [],
  selectedArticleIds: new Set(),
};

const baseUrlInput = document.getElementById("baseUrl");
const authKeyInput = document.getElementById("authKey");
const accountNameInput = document.getElementById("accountName");
const keywordInput = document.getElementById("keyword");
const searchBtn = document.getElementById("searchBtn");
const loadBtn = document.getElementById("loadBtn");
const exportBtn = document.getElementById("exportBtn");
const selectAllBtn = document.getElementById("selectAllBtn");
const clearAllBtn = document.getElementById("clearAllBtn");
const accountList = document.getElementById("accountList");
const articleList = document.getElementById("articleList");
const statusBox = document.getElementById("statusBox");
const selectedText = document.getElementById("selectedText");
const articleCount = document.getElementById("articleCount");

function setStatus(message, extra) {
  statusBox.textContent = extra ? `${message}\n\n${extra}` : message;
}

function buildQuery(params) {
  return new URLSearchParams(params).toString();
}

async function getJson(url) {
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.error || `Request failed: ${res.status}`);
  }
  return data;
}

function renderAccounts(items) {
  accountList.innerHTML = "";
  if (!items.length) {
    accountList.className = "list empty";
    accountList.textContent = "没有搜到公众号，请检查 auth-key 或公众号名称";
    return;
  }
  accountList.className = "list";
  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "account-card";
    if (state.selectedAccount && state.selectedAccount.fakeid === item.fakeid) {
      card.classList.add("active");
    }
    card.innerHTML = `
      <h3>${item.nickname || "未命名公众号"}</h3>
      <div class="meta">
        <div>别名：${item.alias || "无"}</div>
        <div>fakeid：${item.fakeid}</div>
        <div>匹配分数：${item.match_score}</div>
        <div>签名：${item.signature || "无"}</div>
      </div>
      <div class="actions" style="margin-top: 12px">
        <button>选这个号</button>
      </div>
    `;
    card.querySelector("button").addEventListener("click", () => {
      state.selectedAccount = item;
      selectedText.textContent = `当前已选：${item.nickname} (${item.fakeid})`;
      loadBtn.disabled = false;
      renderAccounts(items);
      setStatus(`已选择公众号：${item.nickname}`);
    });
    accountList.appendChild(card);
  });
}

function updateArticleCount() {
  articleCount.textContent = `已选 ${state.selectedArticleIds.size} 篇`;
  exportBtn.disabled = state.selectedArticleIds.size === 0 || !state.selectedAccount;
}

function renderArticles(items) {
  articleList.innerHTML = "";
  state.articles = items;
  state.selectedArticleIds = new Set();
  updateArticleCount();
  selectAllBtn.disabled = items.length === 0;
  clearAllBtn.disabled = items.length === 0;
  if (!items.length) {
    articleList.className = "list empty";
    articleList.textContent = "没有拿到文章列表";
    return;
  }
  articleList.className = "list";
  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "article-card";
    const articleId = item.aid || item.link;
    const time = item.update_time ? new Date(item.update_time * 1000).toLocaleString() : "unknown";
    card.innerHTML = `
      <div class="article-top">
        <input type="checkbox" />
        <div>
          <h3>${item.title || "未命名文章"}</h3>
          <div class="meta">
            <div>作者：${item.author_name || "unknown"}</div>
            <div>发布时间：${time}</div>
            <div><a href="${item.link}" target="_blank">打开原文</a></div>
          </div>
        </div>
      </div>
    `;
    const checkbox = card.querySelector("input");
    checkbox.addEventListener("change", (event) => {
      if (event.target.checked) {
        state.selectedArticleIds.add(articleId);
      } else {
        state.selectedArticleIds.delete(articleId);
      }
      updateArticleCount();
    });
    articleList.appendChild(card);
  });
}

searchBtn.addEventListener("click", async () => {
  try {
    setStatus("正在搜索公众号...");
    state.selectedAccount = null;
    loadBtn.disabled = true;
    const query = buildQuery({
      base_url: baseUrlInput.value.trim(),
      auth_key: authKeyInput.value.trim(),
      account_name: accountNameInput.value.trim(),
    });
    const data = await getJson(`/api/search-account?${query}`);
    state.selectedAccount = data.selected || null;
    renderAccounts(data.items || []);
    if (state.selectedAccount) {
      selectedText.textContent = `推荐公众号：${state.selectedAccount.nickname}`;
      loadBtn.disabled = false;
    } else {
      selectedText.textContent = "没有自动选中公众号";
    }
    setStatus("公众号搜索完成", JSON.stringify(data.selected || {}, null, 2));
  } catch (error) {
    setStatus("搜索失败", String(error));
  }
});

loadBtn.addEventListener("click", async () => {
  try {
    if (!state.selectedAccount) {
      throw new Error("请先选择公众号");
    }
    setStatus("正在拉取文章列表...");
    const query = buildQuery({
      base_url: baseUrlInput.value.trim(),
      auth_key: authKeyInput.value.trim(),
      fakeid: state.selectedAccount.fakeid,
      keyword: keywordInput.value.trim(),
      max_articles: "30",
    });
    const data = await getJson(`/api/articles?${query}`);
    renderArticles(data.items || []);
    setStatus(`文章列表加载完成，共 ${data.items.length} 篇`);
  } catch (error) {
    setStatus("拉取文章失败", String(error));
  }
});

selectAllBtn.addEventListener("click", () => {
  state.selectedArticleIds = new Set(state.articles.map((item) => item.aid || item.link));
  articleList.querySelectorAll('input[type="checkbox"]').forEach((box) => {
    box.checked = true;
  });
  updateArticleCount();
});

clearAllBtn.addEventListener("click", () => {
  state.selectedArticleIds.clear();
  articleList.querySelectorAll('input[type="checkbox"]').forEach((box) => {
    box.checked = false;
  });
  updateArticleCount();
});

exportBtn.addEventListener("click", async () => {
  try {
    if (!state.selectedAccount) {
      throw new Error("请先选择公众号");
    }
    const selected = state.articles.filter((item) => state.selectedArticleIds.has(item.aid || item.link));
    if (!selected.length) {
      throw new Error("请至少选择一篇文章");
    }
    setStatus("正在导出 markdown 和 style_dna.json...");
    const res = await fetch("/api/export-package", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        base_url: baseUrlInput.value.trim(),
        account_name: state.selectedAccount.nickname || accountNameInput.value.trim(),
        author_label: state.selectedAccount.nickname || accountNameInput.value.trim(),
        articles: selected,
      }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || `导出失败: ${res.status}`);
    }
    const blob = await res.blob();
    const disposition = res.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="(.+?)"/);
    const filename = match ? match[1] : "wechat-export.zip";
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    setStatus(`导出完成：${filename}`);
  } catch (error) {
    setStatus("导出失败", String(error));
  }
});

setStatus("准备就绪。先填 exporter 地址、auth-key 和公众号名称。");
