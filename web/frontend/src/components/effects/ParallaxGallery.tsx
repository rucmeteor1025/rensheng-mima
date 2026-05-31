import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useEffect, useMemo, useRef } from "react";
import { galleryTiles } from "../../data/site";

gsap.registerPlugin(ScrollTrigger);

function makeSvg([title, a, b]: string[], index: number) {
  const bg = index % 3 === 0 ? "#12120c" : index % 3 === 1 ? "#0b1511" : "#170c0c";
  const accent = index % 3 === 0 ? "#ffb627" : index % 3 === 1 ? "#386641" : "#bc4749";
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="720" height="920" viewBox="0 0 720 920">
    <rect width="720" height="920" fill="${bg}"/>
    <g fill="none" stroke="${accent}" stroke-opacity=".42">
      <circle cx="360" cy="360" r="210"/>
      <circle cx="360" cy="360" r="120"/>
      <path d="M110 360h500M360 110v500"/>
    </g>
    <text x="52" y="96" fill="#fdf6e3" font-family="Noto Serif SC, serif" font-size="54" font-weight="900">${title}</text>
    <text x="52" y="170" fill="${accent}" font-family="JetBrains Mono, monospace" font-size="32">${a} / ${b}</text>
    <text x="360" y="720" text-anchor="middle" fill="#fdf6e3" fill-opacity=".72" font-family="Noto Sans SC, sans-serif" font-size="28">XIA SHEN SUAN</text>
  </svg>`;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

export function ParallaxGallery() {
  const ref = useRef<HTMLDivElement | null>(null);
  const sources = useMemo(() => galleryTiles.map(makeSvg), []);

  useEffect(() => {
    if (!ref.current) return;
    const ctx = gsap.context(() => {
      const columns = gsap.utils.toArray<HTMLElement>(".parallax-column");
      columns.forEach((column, index) => {
        gsap.fromTo(
          column,
          { y: index === 1 ? 90 : -40, skewY: index === 1 ? -4 : 4 },
          {
            y: index === 1 ? -90 : 70,
            skewY: index === 1 ? 3 : -3,
            ease: "none",
            scrollTrigger: {
              trigger: ref.current,
              start: "top bottom",
              end: "bottom top",
              scrub: 1.2
            }
          }
        );
      });
    }, ref);
    return () => ctx.revert();
  }, []);

  return (
    <div ref={ref} className="relative grid gap-4 md:grid-cols-3">
      {[0, 1, 2].map((column) => (
        <div key={column} className="parallax-column grid gap-4">
          {sources
            .filter((_, index) => index % 3 === column)
            .map((src, index) => (
              <img
                key={src}
                src={src}
                loading="lazy"
                alt={`${galleryTiles[column + index * 3][0]} 命理视觉卡`}
                className="aspect-[4/5] w-full rounded-2xl border border-[#fdf6e3]/12 object-cover opacity-88"
              />
            ))}
        </div>
      ))}
    </div>
  );
}
