import { privacyCards } from "../data/site";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

const sections = [
  ["收集范围", "出生年月日时、性别、出生地、分析类型，以及用户主动填写的 MBTI、星座、血型等辅助信息。"],
  ["使用方式", "信息仅用于排盘分析、报告生成、订单校验和用户主动请求的历史报告查看。"],
  ["数据安全", "正式版会采用数据库加密、访问权限隔离、日志脱敏和支付数据分区管理。"],
  ["用户权利", "用户可以删除命盘、删除报告、导出个人数据、撤回授权或注销账号。"],
  ["免责声明", "报告仅供参考，帮助自我认知和人生规划，不替代医疗、法律、投资等专业建议。"]
];

export function Privacy() {
  return (
    <main className="pt-20">
      <section className="section pb-8">
        <div className="container-x">
          <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">Privacy</p>
          <h1 className="serif text-5xl font-black leading-tight md:text-7xl">隐私协议</h1>
          <p className="mt-5 max-w-2xl text-sm leading-7 text-[#fdf6e3]/62">
            命理产品处理的是高度私密的信息。人生密码按少采集、可删除、可解释、可撤回的原则设计。
          </p>
        </div>
      </section>

      <section className="section pt-6">
        <div className="container-x grid gap-4 md:grid-cols-4">
          {privacyCards.map((item) => (
            <Card key={item.title}>
              <CardHeader>
                <item.icon className="h-7 w-7 text-[#ffb627]" />
                <CardTitle className="text-lg">{item.title}</CardTitle>
                <CardDescription>{item.text}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      <section className="section pt-0">
        <div className="container-x grid gap-4">
          {sections.map(([title, text], index) => (
            <Card key={title}>
              <CardContent className="grid gap-3 p-5 md:grid-cols-[120px_1fr] md:p-6">
                <div className="mono text-sm text-[#ffb627]">0{index + 1}</div>
                <div>
                  <h2 className="serif mb-3 text-2xl font-black">{title}</h2>
                  <p className="text-sm leading-7 text-[#fdf6e3]/68">{text}</p>
                </div>
              </CardContent>
            </Card>
          ))}
          <Card className="border-[#386641]/60 bg-[#386641]/10">
            <CardHeader>
              <CardTitle>联系方式</CardTitle>
              <CardDescription>正式上线前会补充服务主体、客服邮箱、退款规则和数据保护负责人联系方式。</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>
    </main>
  );
}
