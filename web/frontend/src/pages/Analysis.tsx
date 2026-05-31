import { AlertCircle, CheckCircle2, LockKeyhole, RefreshCw, ShieldCheck } from "lucide-react";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { analysisOptions, statusSteps } from "../data/site";
import type { CheckoutOrder, FocusType, FortunePayload, FortuneResponse, FullFortuneReport, FullReportResponse } from "../types";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Select } from "../components/ui/select";
import { buildDemoFortuneResponse, buildDemoFullReport } from "../lib/demoReport";
import { formatPrice } from "../lib/utils";

type PayState = "unpaid" | "paying" | "unlocked" | "failed";

const today = new Date();
const defaultDate = "1990-01-15";
const defaultTime = "14:30";
const DRAFT_STORAGE_KEY = "rsm_report_draft";
const ORDER_STORAGE_KEY = "rsm_checkout_order";
const PAID_REPORT_KEY = "rsm_paid_report_id";

interface ReportDraft {
  report: FortuneResponse;
  focus: FocusType;
  order: CheckoutOrder;
}

function parseDateTime(date: string, time: string) {
  const [year, month, day] = date.split("-").map(Number);
  const [hour, minute] = time.split(":").map(Number);
  return { year, month, day, hour, minute };
}

function readDraft(): ReportDraft | null {
  try {
    const raw = window.sessionStorage.getItem(DRAFT_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ReportDraft) : null;
  } catch {
    return null;
  }
}

function storeDraft(draft: ReportDraft) {
  window.sessionStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draft));
  window.sessionStorage.setItem(ORDER_STORAGE_KEY, JSON.stringify(draft.order));
}

function clearDraft() {
  window.sessionStorage.removeItem(DRAFT_STORAGE_KEY);
  window.sessionStorage.removeItem(ORDER_STORAGE_KEY);
  window.sessionStorage.removeItem(PAID_REPORT_KEY);
}

function buildOrder(report: FortuneResponse, focus: FocusType): CheckoutOrder {
  const option = analysisOptions.find((item) => item.id === focus) || analysisOptions[0];
  return {
    reportId: report.reportId,
    title: option.title,
    price: option.price,
    focus: option.id,
    createdAt: new Date().toISOString()
  };
}

export function Analysis() {
  const navigate = useNavigate();
  const location = useLocation();
  const [focus, setFocus] = useState<FocusType>("full");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState<FortuneResponse | null>(null);
  const [checkoutOrder, setCheckoutOrder] = useState<CheckoutOrder | null>(null);
  const [payState, setPayState] = useState<PayState>("unpaid");
  const [fullReport, setFullReport] = useState<FullFortuneReport | null>(null);
  const [fullLoading, setFullLoading] = useState(false);
  const [fullError, setFullError] = useState("");
  const handledPaidRef = useRef("");

  const selected = useMemo(() => analysisOptions.find((item) => item.id === focus) || analysisOptions[0], [focus]);
  const chart = report?.summary.chart;
  const isStaticHost = window.location.hostname.endsWith("github.io");
  const isDemoReport = isStaticHost || report?.summary.basic.version.includes("GitHub Pages Demo") || false;

  async function loadFullReport(reportId: string) {
    setFullLoading(true);
    setFullError("");
    setPayState("paying");
    try {
      const response = await fetch(`/api/report/${reportId}`);
      const contentType = response.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const demoSource = report || readDraft()?.report;
        if (demoSource) {
          setFullReport(buildDemoFullReport(demoSource));
          setPayState("unlocked");
          window.sessionStorage.setItem(PAID_REPORT_KEY, reportId);
          navigate("/analysis", { replace: true });
          return;
        }
      }
      const payload = (await response.json()) as FullReportResponse;
      if (!response.ok || !payload.ok || !payload.report) {
        throw new Error(payload.error || "完整报告读取失败");
      }
      setFullReport(payload.report);
      setPayState("unlocked");
      window.sessionStorage.setItem(PAID_REPORT_KEY, reportId);
      navigate("/analysis", { replace: true });
    } catch (err) {
      const demoSource = report || readDraft()?.report;
      if (demoSource) {
        setFullReport(buildDemoFullReport(demoSource));
        setPayState("unlocked");
        window.sessionStorage.setItem(PAID_REPORT_KEY, reportId);
        navigate("/analysis", { replace: true });
      } else {
        setFullError(err instanceof Error ? err.message : "完整报告读取失败，请重试");
        setPayState("failed");
      }
    } finally {
      setFullLoading(false);
    }
  }

  useEffect(() => {
    const draft = readDraft();
    if (!draft) return;
    setReport(draft.report);
    setFocus(draft.focus);
    setCheckoutOrder(draft.order);
    const paidParam = new URLSearchParams(location.search).get("paid");
    if (!paidParam && window.sessionStorage.getItem(PAID_REPORT_KEY) === draft.report.reportId) {
      void loadFullReport(draft.report.reportId);
    }
    // 只在首次进入分析页时恢复上一次本地订单。
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const paidReportId = params.get("paid");
    if (!paidReportId || handledPaidRef.current === paidReportId) return;
    handledPaidRef.current = paidReportId;
    const draft = readDraft();
    if (draft?.report.reportId === paidReportId) {
      setReport(draft.report);
      setFocus(draft.focus);
      setCheckoutOrder(draft.order);
    }
    void loadFullReport(paidReportId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setPayState("unpaid");
    const form = new FormData(event.currentTarget);
    const parsed = parseDateTime(String(form.get("birthDate")), String(form.get("birthTime")));
    const requestPayload: FortunePayload = {
      ...parsed,
      gender: String(form.get("gender") || "男"),
      place: String(form.get("place") || "北京"),
      focus: focus === "brief" ? "full" : focus
    };
    try {
      const response = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestPayload)
      });
      const contentType = response.headers.get("content-type") || "";
      let payload: FortuneResponse & { error?: string };
      if (contentType.includes("application/json")) {
        payload = (await response.json()) as FortuneResponse & { error?: string };
        if (!response.ok || !payload.ok) {
          setError(payload.error || "生成失败");
          setPayState("failed");
          return;
        }
      } else {
        payload = buildDemoFortuneResponse(requestPayload);
      }
      setReport(payload);
      setFullReport(null);
      setFullError("");
      const order = buildOrder(payload, focus);
      setCheckoutOrder(order);
      storeDraft({ report: payload, focus, order });
      window.sessionStorage.removeItem(PAID_REPORT_KEY);
    } catch (err) {
      const payload = buildDemoFortuneResponse(requestPayload);
      setReport(payload);
      setFullReport(null);
      setFullError("");
      const order = buildOrder(payload, focus);
      setCheckoutOrder(order);
      storeDraft({ report: payload, focus, order });
      window.sessionStorage.removeItem(PAID_REPORT_KEY);
    } finally {
      setLoading(false);
    }
  }

  function goCheckout() {
    if (!report) return;
    const order = checkoutOrder || buildOrder(report, focus);
    setCheckoutOrder(order);
    storeDraft({ report, focus: order.focus, order });
    navigate(`/checkout?reportId=${report.reportId}`, { state: { order } });
  }

  async function deleteReport() {
    if (report?.reportId) {
      await fetch(`/api/report/${report.reportId}`, { method: "DELETE" }).catch(() => undefined);
    }
    setReport(null);
    setCheckoutOrder(null);
    setFullReport(null);
    setFullError("");
    setPayState("unpaid");
    clearDraft();
  }

  return (
    <main className="pt-20">
      <section className="section pb-8">
        <div className="container-x">
          <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">AI Analysis</p>
          <h1 className="serif text-5xl font-black leading-tight md:text-7xl">AI 命盘分析</h1>
          <p className="mt-5 max-w-2xl text-sm leading-7 text-[#fdf6e3]/62">
            本地运行会调用最新版人生密码命理引擎；GitHub Pages 静态演示会返回合成摘要，用来验证网页流程。
          </p>
        </div>
      </section>

      <section className="section pt-4">
        <div className="container-x grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
          <Card>
            <CardHeader>
              <CardTitle>输入出生信息</CardTitle>
              <CardDescription>默认使用公历 + 钟表时间 + 出生地。</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={onSubmit} className="grid gap-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="grid gap-2 text-sm text-[#fdf6e3]/72">
                    出生日期
                    <Input name="birthDate" type="date" defaultValue={defaultDate} max={`${today.getFullYear()}-12-31`} required />
                  </label>
                  <label className="grid gap-2 text-sm text-[#fdf6e3]/72">
                    出生时间
                    <Input name="birthTime" type="time" defaultValue={defaultTime} required />
                  </label>
                  <label className="grid gap-2 text-sm text-[#fdf6e3]/72">
                    性别
                    <Select name="gender" defaultValue="男">
                      <option value="男">男</option>
                      <option value="女">女</option>
                    </Select>
                  </label>
                  <label className="grid gap-2 text-sm text-[#fdf6e3]/72">
                    出生地
                    <Input name="place" defaultValue="北京" placeholder="例如：北京、上海、广州" required />
                  </label>
                </div>

                <div className="grid gap-3">
                  <span className="text-sm text-[#fdf6e3]/72">分析类型</span>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {analysisOptions.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => setFocus(item.id)}
                        className={`min-h-[86px] rounded-2xl border p-4 text-left transition ${
                          focus === item.id
                            ? "border-[#ffb627] bg-[#ffb627]/12"
                            : "border-[#fdf6e3]/12 bg-[#fdf6e3]/5"
                        }`}
                      >
                        <span className="flex items-center justify-between gap-2">
                          <strong>{item.title}</strong>
                          <span className="mono text-[#ffb627]">{formatPrice(item.price)}</span>
                        </span>
                        <span className="mt-2 block text-xs leading-5 text-[#fdf6e3]/56">{item.desc}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-[#386641] bg-[#386641]/12 p-4 text-sm leading-7 text-[#fdf6e3]/72">
                  <ShieldCheck className="mb-2 h-5 w-5 text-[#6fbf73]" />
                  {isDemoReport
                    ? "当前为 GitHub Pages 静态演示，报告只保存在浏览器会话中，可随时删除。"
                    : "出生信息仅用于本地排盘分析，当前报告可随时删除。"}
                </div>

                <Button type="submit" size="lg" disabled={loading}>
                  {loading ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" /> 生成中
                    </>
                  ) : (
                    `生成${selected.title}`
                  )}
                </Button>
                {error && <p className="rounded-xl border border-[#bc4749]/40 bg-[#bc4749]/10 p-3 text-sm text-[#fdf6e3]">{error}</p>}
              </form>
            </CardContent>
          </Card>

          <div className="grid gap-5">
            <Card>
              <CardHeader>
                <CardTitle>免费摘要区</CardTitle>
                <CardDescription>八字四柱、性格底色、运势概览。</CardDescription>
              </CardHeader>
              <CardContent>
                {chart ? (
                  <div className="grid gap-4">
                    <div className="grid gap-3 sm:grid-cols-4">
                      {(chart.bazi || "").split(" ").map((pillar, index) => (
                        <div key={`${pillar}-${index}`} className="rounded-2xl border border-[#fdf6e3]/12 bg-black/25 p-4 text-center">
                          <span className="mb-2 block text-xs text-[#fdf6e3]/45">{["年柱", "月柱", "日柱", "时柱"][index]}</span>
                          <strong className="mono text-xl text-[#ffb627]">{pillar}</strong>
                        </div>
                      ))}
                    </div>
                    <div className="grid gap-3">
                      {report?.summary.free.map((line) => (
                        <div key={line.title} className="rounded-2xl border border-[#fdf6e3]/10 bg-[#fdf6e3]/5 p-4">
                          <h3 className="mb-2 font-bold text-[#ffb627]">{line.title}</h3>
                          <p className="text-sm leading-7 text-[#fdf6e3]/70">{line.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="grid min-h-[260px] place-items-center rounded-2xl border border-dashed border-[#fdf6e3]/15 text-center text-sm leading-7 text-[#fdf6e3]/58">
                    提交出生信息后，这里会显示免费摘要。
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="border-[#ffb627]/30 bg-[#ffb627]/8">
              <CardHeader>
                <CardTitle>付费解锁卡片</CardTitle>
                <CardDescription>未支付、支付中、已解锁、失败可重试。</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4">
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {statusSteps.map((step, index) => {
                    const active =
                      (payState === "unpaid" && index === 0) ||
                      (payState === "paying" && index === 1) ||
                      (payState === "unlocked" && index === 2) ||
                      (payState === "failed" && index === 3);
                    return (
                      <div key={step.label} className={`rounded-2xl border p-3 text-center ${active ? "border-[#ffb627] text-[#ffb627]" : "border-white/10 text-white/42"}`}>
                        <step.icon className="mx-auto mb-2 h-5 w-5" />
                        <span className="text-xs">{step.label}</span>
                      </div>
                    );
                  })}
                </div>
                {payState === "unlocked" ? (
                  <div className="rounded-2xl border border-[#386641] bg-[#386641]/12 p-4">
                    <CheckCircle2 className="mb-3 h-6 w-6 text-[#6fbf73]" />
                    <h3 className="mb-3 font-bold">完整报告已解锁</h3>
                    <FullReport
                      report={report}
                      fullReport={fullReport}
                      loading={fullLoading}
                      error={fullError}
                      onRetry={() => report?.reportId && loadFullReport(report.reportId)}
                    />
                  </div>
                ) : (
                  <Button onClick={goCheckout} disabled={!report || payState === "paying"}>
                    {payState === "paying" ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" /> 支付中
                      </>
                    ) : (
                      <>
                        <LockKeyhole className="h-4 w-4" /> 支付解锁完整报告
                      </>
                    )}
                  </Button>
                )}
                {payState === "failed" && fullError && (
                  <div className="rounded-2xl border border-[#bc4749]/40 bg-[#bc4749]/10 p-4 text-sm leading-7 text-[#fdf6e3]/72">
                    <AlertCircle className="mb-2 h-5 w-5 text-[#bc4749]" />
                    {fullError}
                    {report?.reportId && (
                      <Button className="mt-3" variant="outline" onClick={() => loadFullReport(report.reportId)}>
                        重新读取完整报告
                      </Button>
                    )}
                  </div>
                )}
                {report && (
                  <Button variant="outline" onClick={deleteReport}>
                    删除本次记录
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </main>
  );
}

function FullReport({
  report,
  fullReport,
  loading,
  error,
  onRetry
}: {
  report: FortuneResponse | null;
  fullReport: FullFortuneReport | null;
  loading: boolean;
  error: string;
  onRetry: () => void;
}) {
  if (loading) {
    return (
      <div className="rounded-xl bg-black/24 p-4 text-sm text-[#fdf6e3]/68">
        <RefreshCw className="mb-3 h-5 w-5 animate-spin text-[#ffb627]" />
        正在读取完整报告...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-[#bc4749]/40 bg-[#bc4749]/10 p-4 text-sm leading-7 text-[#fdf6e3]/72">
        <AlertCircle className="mb-3 h-5 w-5 text-[#bc4749]" />
        {error}
        <Button className="mt-3" variant="outline" onClick={onRetry}>
          重新读取
        </Button>
      </div>
    );
  }

  if (!report) return null;

  const sections = fullReport ? buildFullSections(fullReport, report) : buildSummaryFallback(report);
  const visibleSections = sections.length > 0 ? sections : buildSummaryFallback(report);

  return (
    <div className="grid gap-3">
      {visibleSections.map(({ title, text }) => (
        <article key={title} className="rounded-xl bg-black/24 p-4">
          <h4 className="mb-2 text-sm font-bold text-[#ffb627]">{title}</h4>
          <p className="whitespace-pre-line text-sm leading-7 text-[#fdf6e3]/68">{text || "完整报告正在整理，请稍后重试。"}</p>
        </article>
      ))}
    </div>
  );
}

function buildSummaryFallback(report: FortuneResponse) {
  return [
    { title: "八字命盘精解", text: report.summary.paidPreview[0]?.text || report.summary.free[0]?.text },
    {
      title: "紫微斗数详批",
      text: `命宫主星：${Array.isArray(report.summary.chart.mingStar) ? report.summary.chart.mingStar.join("、") : report.summary.chart.mingStar || "待补充"}；身宫：${report.summary.chart.shenPalace || "待补充"}`
    },
    { title: "性格与心理画像", text: report.summary.free[1]?.text },
    { title: "事业财运深度分析", text: report.summary.free[2]?.text },
    { title: "趋避建议", text: report.summary.paidPreview[report.summary.paidPreview.length - 1]?.text }
  ];
}

function buildFullSections(fullReport: FullFortuneReport, report: FortuneResponse) {
  const styled = valueAt(fullReport, "风格化输出");
  const main = valueAt(styled, "命理主输出");
  const life = valueAt(styled, "生活版");
  const bazi = valueAt(fullReport, "八字命理");
  const ziwei = valueAt(fullReport, "紫微斗数");
  const fusion = valueAt(fullReport, "融合判断");

  const sections = [
    {
      title: "整体判断",
      text: mergeText(valueAt(main, "整体判断"), valueAt(life, "总论"), valueAt(fusion, "主轴"), report.summary.free[0]?.text)
    },
    {
      title: "八字命盘精解",
      text: mergeText(valueAt(bazi, "专业分析"), valueAt(bazi, "日主"), valueAt(bazi, "五行分析"), valueAt(main, "盘面支撑"))
    },
    {
      title: "紫微斗数详批",
      text: mergeText(valueAt(ziwei, "重点宫位"), valueAt(ziwei, "十二宫"), valueAt(ziwei, "四化"))
    },
    {
      title: "性格与心理画像",
      text: mergeText(valueAt(main, "性格气质"), valueAt(life, "性格气质"), valueAt(fullReport, "MBTI"), valueAt(fullReport, "星座"), valueAt(fullReport, "血型"))
    },
    {
      title: "事业财运深度分析",
      text: mergeText(valueAt(main, "事业与财运"), valueAt(life, "事业财运"), valueAt(main, "当前运势"))
    },
    {
      title: "感情与关系",
      text: mergeText(valueAt(main, "感情与婚姻"), valueAt(life, "感情关系"))
    },
    {
      title: "趋避建议",
      text: mergeText(valueAt(main, "建议"), valueAt(fusion, "建议"), valueAt(life, "建议"))
    },
    {
      title: "总结",
      text: mergeText(valueAt(main, "总结"), valueAt(life, "收束"), report.summary.disclaimer)
    }
  ];

  return sections.filter((section) => section.text.trim().length > 0);
}

function valueAt(source: unknown, key: string): unknown {
  if (!source || typeof source !== "object" || Array.isArray(source)) return "";
  return (source as Record<string, unknown>)[key] ?? "";
}

function mergeText(...values: unknown[]) {
  return values
    .map((value) => valueToText(value))
    .filter(Boolean)
    .join("\n\n");
}

function valueToText(value: unknown, depth = 0): string {
  if (value === null || value === undefined || value === "") return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) {
    const items = value.map((item) => valueToText(item, depth + 1)).filter(Boolean);
    return items.join(items.some((item) => item.includes("\n")) ? "\n" : "、");
  }
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>)
      .filter(([, item]) => item !== null && item !== undefined && item !== "")
      .slice(0, depth > 1 ? 8 : 16);
    return entries
      .map(([key, item]) => {
        const text = valueToText(item, depth + 1);
        return text ? `${key}：${text}` : "";
      })
      .filter(Boolean)
      .join("\n");
  }
  return "";
}
