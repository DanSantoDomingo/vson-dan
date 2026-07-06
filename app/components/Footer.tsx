import { SITE } from "../config";
import { Logo } from "./Logo";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="relative overflow-hidden border-t border-border bg-card/40">
      <div className="container mx-auto flex flex-col items-center justify-between gap-4 px-4 py-10 sm:flex-row">
        <div className="flex items-center gap-2 text-base font-bold text-foreground">
          <Logo className="h-6 w-6" />
          {SITE.name}
        </div>
        <p className="text-sm text-muted-foreground">
          &copy; {year} {SITE.name}. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
