import { Check } from "lucide-react";
import { Link } from "react-router-dom";
import { faqItems, pricingPlans } from "../data/site";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

export function Pricing() {
  return (
    <main className="pt-20">
      <section className="section pb-8">
        <div className="container-x">
          <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">Pricing</p>
          <h1 className="serif text-5xl font-black leading-tight md:text-7xl">价格方案</h1>
          <p className="mt-5 max-w-2xl text-sm leading-7 text-[#fdf6e3]/62">
            先体验，再付费。简批免费，完整版按次解锁，会员适合长期跟踪专题报告。
          </p>
        </div>
      </section>

      <section className="section pt-6">
        <div className="container-x grid gap-4 md:grid-cols-3">
          {pricingPlans.map((plan) => {
            const popular = plan.badge === "最受欢迎";
            return (
              <Card key={plan.title} className={popular ? "border-[#ffb627]/50 bg-[#ffb627]/10" : ""}>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <CardTitle>{plan.title}</CardTitle>
                    {plan.badge && <span className="rounded-full bg-[#ffb627] px-3 py-1 text-xs font-bold text-[#050401]">{plan.badge}</span>}
                  </div>
                  <div className="serif text-4xl font-black text-[#ffb627]">{plan.price}</div>
                  <CardDescription>{plan.desc}</CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4">
                  <ul className="grid gap-3">
                    {plan.benefits.map((item) => (
                      <li key={item} className="flex items-center gap-3 text-sm text-[#fdf6e3]/72">
                        <Check className="h-4 w-4 text-[#386641]" />
                        {item}
                      </li>
                    ))}
                  </ul>
                  <Button asChild disabled={plan.title === "年度会员"} variant={popular ? "default" : "outline"}>
                    <Link to="/analysis">{plan.cta}</Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      <section className="section pt-0">
        <div className="container-x">
          <h2 className="serif mb-6 text-3xl font-black md:text-5xl">FAQ</h2>
          <div className="grid gap-3">
            {faqItems.map(([question, answer]) => (
              <details key={question} className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
                <summary className="cursor-pointer font-bold text-[#fdf6e3]">{question}</summary>
                <p className="mt-3 text-sm leading-7 text-[#fdf6e3]/62">{answer}</p>
              </details>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
