import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useEffect, useRef } from "react";
import { kernelWords } from "../../data/site";

gsap.registerPlugin(ScrollTrigger);

export function KernelDepth() {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const ctx = gsap.context(() => {
      const words = gsap.utils.toArray<HTMLElement>(".kernel-word");
      gsap.set(words, {
        z: (i) => -i * 90,
        rotationX: (i) => (i % 2 ? 18 : -18),
        rotationY: (i) => (i % 3 ? -14 : 14),
        transformPerspective: 900
      });
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: ref.current,
          start: "top 70%",
          end: "bottom top",
          scrub: 1.4
        }
      });
      tl.to(words, {
        z: 220,
        xPercent: (i) => (i % 2 ? 18 : -18),
        yPercent: (i) => (i % 3 ? -8 : 8),
        rotationX: 0,
        rotationY: 0,
        stagger: 0.025,
        ease: "power2.out"
      }).to(words, {
        xPercent: (i) => (i % 2 ? 150 : -150),
        yPercent: (i) => (i % 2 ? -45 : 45),
        rotationY: (i) => (i % 2 ? 45 : -45),
        opacity: 0.2,
        ease: "power2.in"
      });
    }, ref);
    return () => ctx.revert();
  }, []);

  return (
    <section ref={ref} className="section bg-black">
      <div className="container-x">
        <div className="mb-12 max-w-xl">
          <p className="mb-3 text-xs font-bold uppercase tracking-normal text-[#ffb627]">Model Kernel</p>
          <h2 className="serif text-4xl font-black leading-tight md:text-6xl">模型内核</h2>
          <p className="mt-5 text-sm leading-7 text-[#fdf6e3]/62">
            命理结构、人格补充和置信系统分层进入模型，不让低权重标签推翻核心盘面。
          </p>
        </div>
        <div className="grid min-h-[440px] place-items-center overflow-hidden rounded-2xl border border-white/10 bg-[#050401]">
          <div className="grid grid-cols-3 gap-4 px-8 text-center md:grid-cols-5">
            {kernelWords.map((word, index) => (
              <span
                key={`${word}-${index}`}
                className="kernel-word serif text-3xl font-black text-[#fdf6e3] md:text-5xl"
              >
                {word}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
