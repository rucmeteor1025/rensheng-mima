import { aboutPrinciples, architecture } from "../data/site";
import { Card, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

export function About() {
  return (
    <main className="pt-20">
      <section className="section pb-8">
        <div className="container-x">
          <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">About</p>
          <h1 className="serif text-5xl font-black leading-tight md:text-7xl">关于我们</h1>
          <p className="mt-5 max-w-2xl text-sm leading-7 text-[#fdf6e3]/62">
            人生密码希望把传统命理、现代 AI 和克制的产品设计结合起来，让用户在读懂自己时更清醒，而不是更焦虑。
          </p>
        </div>
      </section>

      <section className="section pt-6">
        <div className="container-x grid gap-5 md:grid-cols-[0.9fr_1.1fr] md:items-start">
          <Card className="bg-[#ffb627]/8">
            <CardHeader>
              <CardTitle className="serif text-3xl md:text-5xl">平台愿景</CardTitle>
              <CardDescription className="text-base leading-8">
                知命不认命。命盘不是判决书，而是一张结构图。我们用 AI 把复杂术语翻译成能行动的建议，并始终提醒用户理性决策。
              </CardDescription>
            </CardHeader>
          </Card>
          <div className="grid gap-4 sm:grid-cols-2">
            {aboutPrinciples.map((item) => (
              <Card key={item.title}>
                <CardHeader>
                  <item.icon className="h-7 w-7 text-[#ffb627]" />
                  <CardTitle className="text-lg">{item.title}</CardTitle>
                  <CardDescription>{item.text}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="section pt-0">
        <div className="container-x">
          <h2 className="serif mb-6 text-4xl font-black md:text-6xl">技术架构说明</h2>
          <div className="grid gap-4 md:grid-cols-4">
            {architecture.map((item, index) => (
              <Card key={item}>
                <CardHeader>
                  <span className="mono text-sm text-[#ffb627]">Layer {index + 1}</span>
                  <CardTitle className="text-xl">{item}</CardTitle>
                  <CardDescription>
                    {[
                      "八字、紫微、宫位、十神等结构化知识。",
                      "将结构化命盘转化为可读分析和建议。",
                      "MBTI、星座、血型只作行为解释补充。",
                      "区分高置信结构判断与低置信主题提示。"
                    ][index]}
                  </CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="section pt-0">
        <div className="container-x rounded-2xl border border-white/10 bg-white/[0.04] p-6 md:p-10">
          <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">Team</p>
          <h2 className="serif text-3xl font-black md:text-5xl">团队介绍</h2>
          <p className="mt-5 max-w-3xl text-sm leading-8 text-[#fdf6e3]/64">
            当前阶段由命理引擎、AI 产品、前端交互和隐私安全几个模块协同推进。正式商业化前，会进一步补齐服务主体、专业顾问审核机制和用户支持流程。
          </p>
        </div>
      </section>
    </main>
  );
}
