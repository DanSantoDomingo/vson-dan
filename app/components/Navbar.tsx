import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router";
import { NAV_LINKS, SITE } from "../config";
import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";

export function Navbar() {
  const { pathname } = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <header className="fixed inset-x-0 top-0 z-50">
        <div className="container mx-auto px-4 pt-4">
          <div
            className={`flex h-14 items-center justify-between rounded-full border px-3 pl-5 transition-all duration-300 ${
              scrolled
                ? "border-border bg-card/70 shadow-sm backdrop-blur-xl"
                : "border-transparent"
            }`}
          >
            <Link
              to="/"
              className="flex items-center gap-2 text-lg font-bold tracking-tight text-foreground"
            >
              <Logo />
              {SITE.name}
            </Link>

            {NAV_LINKS.length > 0 && (
              <nav className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-1 md:flex">
                {NAV_LINKS.map((link) => (
                  <Link
                    key={link.href}
                    to={link.href}
                    className={`rounded-full px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground ${
                      pathname === link.href
                        ? "text-foreground"
                        : "text-muted-foreground"
                    }`}
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            )}

            <div className="flex items-center gap-1.5">
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>
      <div className="h-[88px]" aria-hidden="true" />
    </>
  );
}
