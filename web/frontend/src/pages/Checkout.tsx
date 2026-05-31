import { ArrowLeft, BadgeCheck, CheckCircle2, CreditCard, LockKeyhole, QrCode, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import type { CheckoutOrder } from "../types";
import { formatPrice } from "../lib/utils";

const ORDER_STORAGE_KEY = "rsm_checkout_order";
const PAID_REPORT_KEY = "rsm_paid_report_id";

function readStoredOrder(): CheckoutOrder | null {
  try {
    const raw = window.sessionStorage.getItem(ORDER_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as CheckoutOrder) : null;
  } catch {
    return null;
  }
}

export function Checkout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [params] = useSearchParams();
  const stateOrder = (location.state as { order?: CheckoutOrder } | null)?.order;
  const [processing, setProcessing] = useState(false);

  const order = useMemo(() => {
    const stored = readStoredOrder();
    const candidate = stateOrder || stored;
    const reportId = params.get("reportId");
    if (!candidate || (reportId && candidate.reportId !== reportId)) return null;
    return candidate;
  }, [params, stateOrder]);

  function completeTestPayment() {
    if (!order) return;
    setProcessing(true);
    window.setTimeout(() => {
      window.sessionStorage.setItem(PAID_REPORT_KEY, order.reportId);
      navigate(`/analysis?paid=${order.reportId}`, { replace: true });
    }, 900);
  }

  return (
    <main className="pt-20">
      <section className="section">
        <div className="container-x mx-auto max-w-4xl">
          <Link to="/analysis" className="mb-6 inline-flex items-center gap-2 text-sm text-[#fdf6e3]/62 transition hover:text-[#ffb627]">
            <ArrowLeft className="h-4 w-4" />
            返回分析页
          </Link>

          <div className="grid gap-5 lg:grid-cols-[1fr_0.78fr]">
            <Card className="border-[#ffb627]/28">
              <CardHeader>
                <p className="text-xs font-bold uppercase tracking-normal text-[#ffb627]">Checkout</p>
                <CardTitle className="serif text-4xl md:text-5xl">支付解锁完整报告</CardTitle>
                <CardDescription>本地版先使用测试支付打通流程，正式上线时替换为真实支付网关。</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4">
                {order ? (
                  <>
                    <div className="rounded-2xl border border-[#fdf6e3]/12 bg-black/24 p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-xs text-[#fdf6e3]/45">订单项目</p>
                          <h2 className="mt-1 text-xl font-bold">{order.title}</h2>
                          <p className="mono mt-2 text-xs text-[#fdf6e3]/45">报告 ID：{order.reportId}</p>
                        </div>
                        <strong className="mono text-2xl text-[#ffb627]">{formatPrice(order.price)}</strong>
                      </div>
                    </div>

                    <div className="grid gap-3">
                      <PaymentMethod active icon={BadgeCheck} title="测试支付" text="用于本地验证支付后解锁完整报告。" />
                      <PaymentMethod icon={QrCode} title="微信支付 / 支付宝" text="正式上线后接入商户号、回调验签和订单状态查询。" />
                      <PaymentMethod icon={CreditCard} title="Stripe / 海外卡" text="面向海外用户时可作为备选收款通道。" />
                    </div>

                    <div className="rounded-2xl border border-[#386641] bg-[#386641]/12 p-4 text-sm leading-7 text-[#fdf6e3]/70">
                      <ShieldCheck className="mb-2 h-5 w-5 text-[#6fbf73]" />
                      支付只绑定本次报告 ID。出生信息不进入支付渠道，生产版支付回调也只处理订单状态。
                    </div>

                    <Button size="lg" onClick={completeTestPayment} disabled={processing}>
                      {processing ? (
                        <>
                          <LockKeyhole className="h-4 w-4 animate-pulse" /> 正在确认支付
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="h-4 w-4" /> 模拟支付成功
                        </>
                      )}
                    </Button>
                  </>
                ) : (
                  <div className="grid min-h-[300px] place-items-center rounded-2xl border border-dashed border-[#fdf6e3]/15 text-center">
                    <div>
                      <h2 className="font-bold">没有待支付订单</h2>
                      <p className="mt-3 text-sm text-[#fdf6e3]/58">先生成一份命盘摘要，再进入支付解锁。</p>
                      <Button className="mt-5" asChild>
                        <Link to="/analysis">去生成报告</Link>
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>正式支付怎么接</CardTitle>
                <CardDescription>上线版本会把这里换成真实订单系统。</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 text-sm leading-7 text-[#fdf6e3]/68">
                <p>1. 前端创建订单，后端生成 `order_id` 和支付参数。</p>
                <p>2. 微信或支付宝完成收款后，请求后端回调地址。</p>
                <p>3. 后端验签成功，再把订单改成已支付。</p>
                <p>4. 分析页查询订单状态，确认已支付后拉取完整报告。</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </main>
  );
}

function PaymentMethod({
  active,
  icon: Icon,
  title,
  text
}: {
  active?: boolean;
  icon: typeof BadgeCheck;
  title: string;
  text: string;
}) {
  return (
    <div className={`rounded-2xl border p-4 ${active ? "border-[#ffb627] bg-[#ffb627]/10" : "border-[#fdf6e3]/10 bg-[#fdf6e3]/5"}`}>
      <div className="flex gap-3">
        <Icon className={`mt-1 h-5 w-5 ${active ? "text-[#ffb627]" : "text-[#fdf6e3]/45"}`} />
        <div>
          <h3 className="font-bold">{title}</h3>
          <p className="mt-1 text-sm leading-6 text-[#fdf6e3]/58">{text}</p>
        </div>
      </div>
    </div>
  );
}
