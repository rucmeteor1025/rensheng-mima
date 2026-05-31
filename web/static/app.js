const app = document.querySelector("#app");

let currentReport = null;
let currentReportId = "";

const routes = {
  "/": renderHome,
  "/analysis": renderAnalysis,
  "/pricing": renderPricing,
  "/privacy": renderPrivacy,
  "/about": renderAbout
};

function html(strings, ...values) {
  return strings.reduce((out, str, i) => out + str + (values[i] ?? ""), "");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function lineCards(lines = []) {
  if (!lines.length) {
    return `<article class="soft-card"><h3>等待生成</h3><p>提交出生信息后，这里会展示免费摘要。</p></article>`;
  }
  return lines.map((item) => html`
    <article class="soft-card">
      <h3>${escapeHtml(item.title || "判断")}</h3>
      <p>${escapeHtml(item.text || "")}</p>
    </article>
  `).join("");
}

function compactForm() {
  return html`
    <form id="fortune-form" class="form-card">
      <div class="form-head">
        <div>
          <p class="eyebrow">立即体验</p>
          <h2>输入出生信息</h2>
        </div>
        <span class="pill">公历 · 钟表时间</span>
      </div>
      <div class="grid six">
        <label><span>出生年</span><input name="year" type="number" min="1900" max="2100" value="1990" required /></label>
        <label><span>月</span><input name="month" type="number" min="1" max="12" value="1" required /></label>
        <label><span>日</span><input name="day" type="number" min="1" max="31" value="15" required /></label>
        <label><span>时</span><input name="hour" type="number" min="0" max="23" value="14" required /></label>
        <label><span>分</span><input name="minute" type="number" min="0" max="59" value="30" required /></label>
        <label><span>性别</span><select name="gender"><option value="男">男</option><option value="女">女</option></select></label>
      </div>
      <label><span>出生地</span><input name="place" value="北京" maxlength="80" placeholder="例如：北京、上海、广州" /></label>
      <div class="segmented" role="radiogroup" aria-label="分析类型">
        <label><input type="radio" name="focus" value="full" checked /><span>综合全盘</span></label>
        <label><input type="radio" name="focus" value="career" /><span>事业财运</span></label>
        <label><input type="radio" name="focus" value="relationship" /><span>感情关系</span></label>
        <label><input type="radio" name="focus" value="wealth" /><span>年度财富</span></label>
      </div>
      <details class="optional">
        <summary>补充信息</summary>
        <div class="grid two">
          <label><span>MBTI</span><input name="mbti" placeholder="可选，例如 INFJ" /></label>
          <label><span>血型</span><input name="bloodType" placeholder="可选，例如 B型" /></label>
        </div>
      </details>
      <button id="submit-button" type="submit">生成免费摘要</button>
      <p class="fineprint">出生信息仅用于本次排盘分析；当前本地 MVP 仅在服务内存暂存，可随时删除。</p>
    </form>
  `;
}

function renderHome() {
  app.innerHTML = html`
    <section class="hero-grid">
      <div class="hero-copy">
        <p class="eyebrow">开发端公测版</p>
        <h1>人生密码</h1>
        <p class="hero-text">结合八字、紫微斗数与 AI 表达，让命盘从术语变成能读懂、能参考、能行动的人生分析。</p>
        <div class="hero-actions">
          <a class="primary-link" href="#fortune-form">开始分析</a>
          <a class="ghost-link" href="/privacy" data-link>查看隐私承诺</a>
        </div>
      </div>
      <div class="visual-panel" aria-label="人生密码可视化">
        <div class="ring">
          <span>命宫</span><span>事业</span><span>关系</span><span>财运</span>
        </div>
        <div class="visual-note">
          <strong>八字 × 紫微 × AI</strong>
          <p>先定结构，再看场景，最后落到趋避建议。</p>
        </div>
      </div>
    </section>
    ${compactForm()}
    <section class="section-grid three">
      ${featureCard("先给判断", "不是堆术语，而是先说这张盘最重要的主轴。")}
      ${featureCard("功能完整", "综合全盘、事业财运、感情关系、年度财富逐步接入。")}
      ${featureCard("尊重隐私", "出生信息只用于排盘，可删除，不写入公开资料。")}
    </section>
    <section class="wide-section">
      <div>
        <p class="eyebrow">服务维度</p>
        <h2>从命盘到行动建议</h2>
      </div>
      <div class="dimension-grid">
        ${dimension("八字命理", "底层气势、十神结构、喜忌方向")}
        ${dimension("紫微斗数", "命身主轴、十二宫、四化落点")}
        ${dimension("AI 解读", "讲人话、有判断、有趋避建议")}
        ${dimension("隐私控制", "删除记录、少采集、不公开")}
      </div>
    </section>
    <section class="trust-row">
      <div><strong>5</strong><span>核心页面</span></div>
      <div><strong>3</strong><span>价格层级</span></div>
      <div><strong>0</strong><span>强制实名</span></div>
      <div><strong>1</strong><span>真实命理引擎</span></div>
    </section>
    <section class="section-grid two">
      ${quote("比传统报告更像人在说话，能快速抓住重点。")}
      ${quote("先免费摘要，再决定是否解锁完整版，体验更舒服。")}
    </section>
    ${faqBlock()}
  `;
  bindForm();
}

function renderAnalysis() {
  const summary = currentReport?.summary;
  const chart = summary?.chart || {};
  app.innerHTML = html`
    <section class="page-head">
      <p class="eyebrow">AI 命盘分析</p>
      <h1>免费摘要与完整版解锁</h1>
      <p>当前分析页已接入本地最新版命理引擎。没有报告时，可回首页生成一份免费摘要。</p>
    </section>
    <section class="analysis-grid">
      <div class="analysis-main">
        <div class="panel-head">
          <h2>免费摘要预览</h2>
          <span class="pill">${summary ? "已生成" : "未生成"}</span>
        </div>
        <div class="chart-strip">
          <div><span>八字</span><strong>${escapeHtml(chart.bazi || "-")}</strong></div>
          <div><span>日主</span><strong>${escapeHtml([chart.dayMaster, chart.strength, chart.useful].filter(Boolean).join(" · ") || "-")}</strong></div>
          <div><span>命宫主星</span><strong>${escapeHtml(Array.isArray(chart.mingStar) ? chart.mingStar.join("、") || "-" : chart.mingStar || "-")}</strong></div>
        </div>
        <div class="lines">${lineCards(summary?.free)}</div>
        <div class="ziwei-box">
          <h2>紫微斗数概览</h2>
          <p>身宫：${escapeHtml(chart.shenPalace || "-")}。完整版会展开十二宫、四化、宫位联动和趋避建议。</p>
        </div>
      </div>
      <aside class="analysis-side">
        <div class="pay-card">
          <p class="eyebrow">完整版</p>
          <h2>¥29.9 解锁完整报告</h2>
          <p>包含事业、关系、状态、阶段运势、趋避建议。当前本地 MVP 暂未接入真实支付。</p>
          <button disabled>支付功能待接入</button>
        </div>
        <div class="order-flow">
          <h3>订单状态流程</h3>
          <ol>
            <li class="active">未支付</li>
            <li>支付中</li>
            <li>已解锁</li>
            <li>失败可重试</li>
          </ol>
        </div>
        <div class="history-card">
          <h3>历史报告</h3>
          <p>正式版会支持登录后查看历史报告。当前本地报告只存在内存。</p>
          ${currentReportId ? `<button id="delete-button" type="button">删除本次记录</button>` : `<a class="primary-link full" href="/" data-link>去生成报告</a>`}
        </div>
      </aside>
    </section>
  `;
  bindDelete();
}

function renderPricing() {
  app.innerHTML = html`
    <section class="page-head">
      <p class="eyebrow">价格方案</p>
      <h1>先体验，再付费</h1>
      <p>第一版建议用单次报告验证付费意愿，会员放到第二阶段。</p>
    </section>
    <section class="price-grid">
      ${priceCard("免费简批", "¥0", "基础盘面 + 3 条核心判断", "生成免费摘要")}
      ${priceCard("单次完整版", "¥29.9", "完整报告 + 趋避建议 + 付费解锁", "推荐方案", true)}
      ${priceCard("年度会员", "¥198", "多次生成 + 历史报告 + 专题分析", "后续开放")}
    </section>
    <section class="wide-section">
      <h2>权益对比</h2>
      <table class="compare-table">
        <tr><th>权益</th><th>免费</th><th>单次</th><th>会员</th></tr>
        <tr><td>免费摘要</td><td>有</td><td>有</td><td>有</td></tr>
        <tr><td>完整版报告</td><td>无</td><td>1 次</td><td>多次</td></tr>
        <tr><td>历史报告</td><td>无</td><td>有</td><td>有</td></tr>
        <tr><td>专题分析</td><td>无</td><td>按次</td><td>包含</td></tr>
      </table>
    </section>
    ${faqBlock()}
  `;
}

function renderPrivacy() {
  app.innerHTML = html`
    <section class="page-head">
      <p class="eyebrow">隐私协议</p>
      <h1>出生信息只用于排盘分析</h1>
      <p>人生密码按高隐私工具设计：少采集、可删除、日志脱敏、付费数据隔离。</p>
    </section>
    <section class="section-grid two">
      ${policy("数据收集范围", "出生年月日时、性别、出生地、分析类型，以及你主动填写的 MBTI/血型。")}
      ${policy("处理方式", "信息仅用于生成命盘分析，不要求身份证，不强制真实姓名。")}
      ${policy("加密措施", "正式版会对出生信息和报告做数据库加密，支付回调与报告数据隔离。")}
      ${policy("用户权利", "你可以删除报告、删除账号、申请导出或撤回授权。")}
      ${policy("日志安全", "生产日志不打印完整出生信息、手机号、token 或支付敏感字段。")}
      ${policy("联系方式", "正式上线前会补充服务主体、客服邮箱和退款规则。")}
    </section>
  `;
}

function renderAbout() {
  app.innerHTML = html`
    <section class="page-head">
      <p class="eyebrow">关于我们</p>
      <h1>把命理报告做成现代 AI 工具</h1>
      <p>人生密码不是让用户交出判断权，而是把复杂命盘翻译成可理解的自我认知和行动参考。</p>
    </section>
    <section class="wide-section about-layout">
      <div>
        <h2>平台愿景</h2>
        <p>讲人话、有判断、有趋避建议；重大决策永远回到命理参考与理性判断双轨。</p>
      </div>
      <div>
        <h2>技术架构</h2>
        <p>前端页面接入本地 API，后端复用人生密码本地命理引擎，不影响原有命令行入口。</p>
      </div>
      <div>
        <h2>用户承诺</h2>
        <p>不强制实名，不公开命盘，不把个人出生信息写入公开报告或训练数据。</p>
      </div>
    </section>
  `;
}

function featureCard(title, text) {
  return `<article class="soft-card"><h3>${title}</h3><p>${text}</p></article>`;
}

function dimension(title, text) {
  return `<div><strong>${title}</strong><span>${text}</span></div>`;
}

function quote(text) {
  return `<article class="quote-card"><p>${text}</p><span>试用反馈</span></article>`;
}

function priceCard(title, price, desc, action, highlight = false) {
  return html`
    <article class="price-card ${highlight ? "highlight" : ""}">
      <h2>${title}</h2>
      <strong>${price}</strong>
      <p>${desc}</p>
      <button ${highlight ? "" : "disabled"}>${action}</button>
    </article>
  `;
}

function policy(title, text) {
  return `<article class="soft-card"><h3>${title}</h3><p>${text}</p></article>`;
}

function faqBlock() {
  return html`
    <section class="wide-section faq">
      <p class="eyebrow">FAQ</p>
      <h2>常见问题</h2>
      <details open><summary>命理分析能替代现实决策吗？</summary><p>不能。它是参考工具，不替代医疗、法律、投资等专业建议。</p></details>
      <details><summary>出生信息会被公开吗？</summary><p>不会。正式版会提供删除记录、导出数据和撤回授权能力。</p></details>
      <details><summary>什么时候接支付？</summary><p>本地体验确认后，再接微信支付、支付宝或 Stripe，并加入订单回调校验。</p></details>
    </section>
  `;
}

function formPayload(form) {
  const data = new FormData(form);
  return {
    year: Number(data.get("year")),
    month: Number(data.get("month")),
    day: Number(data.get("day")),
    hour: Number(data.get("hour")),
    minute: Number(data.get("minute")),
    gender: data.get("gender"),
    place: data.get("place"),
    focus: data.get("focus"),
    mbti: data.get("mbti"),
    bloodType: data.get("bloodType")
  };
}

function bindForm() {
  const form = document.querySelector("#fortune-form");
  if (!form) return;
  const button = document.querySelector("#submit-button");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    button.disabled = true;
    button.textContent = "生成中...";
    try {
      const response = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formPayload(form))
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok) throw new Error(payload.error || "生成失败");
      currentReport = payload;
      currentReportId = payload.reportId;
      navigate("/analysis");
    } catch (error) {
      alert(error.message || "生成失败，请稍后重试");
    } finally {
      button.disabled = false;
      button.textContent = "生成免费摘要";
    }
  });
}

function bindDelete() {
  const button = document.querySelector("#delete-button");
  if (!button) return;
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      if (currentReportId) {
        await fetch(`/api/report/${currentReportId}`, { method: "DELETE" });
      }
      currentReport = null;
      currentReportId = "";
      renderAnalysis();
    } finally {
      button.disabled = false;
    }
  });
}

function navigate(path) {
  window.history.pushState({}, "", path);
  renderRoute();
}

function renderRoute() {
  const route = routes[window.location.pathname] || renderHome;
  route();
  document.querySelectorAll("[data-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      const url = new URL(link.href);
      if (url.origin === window.location.origin) {
        event.preventDefault();
        navigate(url.pathname);
      }
    });
  });
}

window.addEventListener("popstate", renderRoute);
renderRoute();
