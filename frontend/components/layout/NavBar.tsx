import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/submissions", label: "Submissions" },
  { href: "/billing", label: "Billing" },
  { href: "/account", label: "Account" },
];

export function NavBar() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[#071019]/85 backdrop-blur-xl">
      <nav className="mx-auto flex w-full max-w-7xl items-center justify-between px-8 py-4">
        <Link href="/dashboard" className="text-lg font-semibold tracking-tight text-white">
          Submission Ghostwriter
        </Link>
        <div className="flex items-center gap-8 text-sm text-white/80">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="transition hover:text-white">
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}
