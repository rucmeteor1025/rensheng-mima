import { ArrowRight, Layers3 } from "lucide-react";
import { Link } from "react-router-dom";
import { featureCards } from "../data/site";
import { KernelDepth } from "../components/effects/KernelDepth";
import { ParallaxGallery } from "../components/effects/ParallaxGallery";
import { ScrollReveal } from "../components/effects/ScrollReveal";
import { HeroMatrix } from "../components/three/HeroMatrix";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

export function Home() {
  return (
    <>
      <section className="relative grid min-h-screen place-items-center overflow-hidden px-5 pt-24">
        <HeroMatrix />
        <div className="absolute inset-0 bg-[#050401]/50" />
        <div className="relative z-10 mx-auto max-w-5xl text-center">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-[#ffb627]/35 bg-[#050401]/55 px-4 py-2 text-xs font-bold text-[#ffb627] backdrop-blur-xl">
            <Layers3 className="h-4 w-4" />
            八字 × 紫微 × AI
          </div>
          <h1 className="serif text-5xl font-black leading-[1.05] tracking-normal md:text-8xl">
            知命不认命，
            <br />
            解构你的命盘源代码
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-8 text-[#fdf6e3]/72 md:text-lg">
            融合八字、紫微斗数、MBTI/星座/血型辅助层。讲人话，有判断，有趋避建议，帮你把复杂命盘变成可理解的人生参考。
          </p>
          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button asChild size="lg">
              <Link to="/analysis">
                立即排盘 <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link to="/privacy">查看隐私承诺</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container-x">
          <ScrollReveal className="mb-10 max-w-2xl">
            <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">Features</p>
            <h2 className="serif text-4xl font-black md:text-6xl">讲人话的命盘工具</h2>
          </ScrollReveal>
          <div className="grid gap-4 md:grid-cols-3">
            {featureCards.map((item) => (
              <ScrollReveal key={item.title}>
                <Card className="h-full">
                  <CardHeader>
                    <item.icon className="h-8 w-8 text-[#ffb627]" />
                    <CardTitle>{item.title}</CardTitle>
                    <CardDescription>{item.text}</CardDescription>
                  </CardHeader>
                </Card>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      <section className="section pt-0">
        <div className="container-x">
          <div className="sticky top-24 z-10 mb-8 max-w-md">
            <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">Twelve Aspects</p>
            <h2 className="serif text-5xl font-black md:text-7xl">多维解构</h2>
            <p className="mt-4 text-sm leading-7 text-[#fdf6e3]/62">十二组命理图像随滚动错速移动，暗示命盘不是单一答案，而是多维结构。</p>
          </div>
          <ParallaxGallery />
        </div>
      </section>

      <section className="section">
        <div className="container-x grid gap-8 md:grid-cols-[0.9fr_1.1fr] md:items-center">
          <ScrollReveal>
            <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">Trust Model</p>
            <h2 className="serif text-4xl font-black leading-tight md:text-6xl">八字 + 紫微 + 心理三元模型</h2>
            <p className="mt-6 text-base leading-8 text-[#fdf6e3]/68">
              八字定底层气势和承接能力，紫微定命身主轴与现实场景，心理辅助层解释表达方式、压力反应和相处节奏。
            </p>
          </ScrollReveal>
          <ScrollReveal>
            <Card className="scanline p-5">
              <CardContent className="p-0">
                <div className="grid gap-3 mono text-sm">
                  {["命宫", "财帛", "官禄", "福德", "夫妻", "迁移"].map((label, index) => (
                    <div key={label} className="grid grid-cols-[70px_1fr_64px] items-center gap-3 rounded-xl border border-white/10 bg-white/[0.035] p-3">
                      <span className="text-[#ffb627]">{label}</span>
                      <span className="h-2 rounded-full bg-[#fdf6e3]/10">
                        <span
                          className="block h-2 rounded-full bg-[#ffb627]"
                          style={{ width: `${52 + index * 7}%` }}
                        />
                      </span>
                      <span className="text-right text-[#fdf6e3]/58">{82 - index * 5}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </ScrollReveal>
        </div>
      </section>

      <KernelDepth />

      <section className="section">
        <div className="container-x rounded-2xl border border-[#ffb627]/30 bg-[#ffb627]/8 p-7 text-center md:p-12">
          <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">Start</p>
          <h2 className="serif mx-auto max-w-3xl text-4xl font-black leading-tight md:text-6xl">从一份免费简批开始</h2>
          <p className="mx-auto mt-5 max-w-2xl text-sm leading-7 text-[#fdf6e3]/68">
            先看摘要，再决定是否解锁完整报告。所有出生信息仅用于排盘分析，可随时删除。
          </p>
          <Button asChild size="lg" className="mt-8">
            <Link to="/analysis">进入分析页面</Link>
          </Button>
        </div>
      </section>
    </>
  );
}
