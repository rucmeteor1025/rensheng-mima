import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { navItems } from "../data/site";
import { Button } from "./ui/button";

export function Layout() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[#050401] text-[#fdf6e3]">
      <header
        className={`fixed inset-x-0 top-0 z-50 transition-all duration-500 mix-blend-difference ${
          scrolled ? "border-b border-white/15 bg-black/45 backdrop-blur-xl" : "bg-transparent"
        }`}
      >
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 md:h-20 md:px-8">
          <Link to="/" className="flex items-center gap-3" onClick={() => setOpen(false)}>
            <span className="grid h-10 w-10 place-items-center rounded-full border border-[#ffb627] text-[#ffb627] mono text-sm">
              命
            </span>
            <span>
              <strong className="block serif text-xl leading-none">人生密码</strong>
              <small className="text-xs text-[#fdf6e3]/65">AI 命理分析工具</small>
            </span>
          </Link>

          <nav className="hidden items-center gap-7 md:flex">
            {navItems.map((item) => (
              <NavLink
                key={item.href}
                to={item.href}
                className={({ isActive }) =>
                  `text-sm transition ${isActive ? "text-[#ffb627]" : "text-[#fdf6e3]/76 hover:text-[#ffb627]"}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <Button asChild className="hidden md:inline-flex">
            <Link to="/analysis">立即排盘</Link>
          </Button>

          <button
            className="grid h-11 w-11 place-items-center rounded-full border border-white/15 md:hidden"
            onClick={() => setOpen((value) => !value)}
            aria-label="打开导航"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {open && (
          <div className="mx-4 mb-4 rounded-2xl border border-white/10 bg-[#050401]/95 p-3 backdrop-blur-xl md:hidden">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className="block rounded-xl px-4 py-3 text-sm text-[#fdf6e3]/78 hover:bg-white/8 hover:text-[#ffb627]"
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            ))}
          </div>
        )}
      </header>

      <Outlet />
      <Footer />
    </div>
  );
}

function Footer() {
  return (
    <footer className="safe-bottom border-t border-[#fdf6e3]/12 px-5 py-10">
      <div className="container-x grid gap-8 md:grid-cols-[1.2fr_1fr_1fr]">
        <div>
          <div className="mb-4 flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-full border border-[#ffb627] text-[#ffb627] mono text-sm">
              命
            </span>
            <strong className="serif text-2xl">人生密码</strong>
          </div>
          <p className="max-w-md text-sm leading-7 text-[#fdf6e3]/58">
            讲人话、有判断、有趋避建议。命理报告仅供参考，不替代医疗、法律、投资等专业建议。
          </p>
        </div>
        <div>
          <h3 className="mb-4 text-sm font-bold text-[#ffb627]">导航</h3>
          <div className="grid gap-2 text-sm text-[#fdf6e3]/62">
            {navItems.map((item) => (
              <Link key={item.href} to={item.href} className="hover:text-[#ffb627]">
                {item.label}
              </Link>
            ))}
          </div>
        </div>
        <div>
          <h3 className="mb-4 text-sm font-bold text-[#ffb627]">隐私声明</h3>
          <p className="text-sm leading-7 text-[#fdf6e3]/58">
            出生信息仅用于排盘分析，正式版将提供加密存储、删除记录、导出数据和撤回授权能力。
          </p>
        </div>
      </div>
    </footer>
  );
}
