import { Link, useLocation } from 'react-router';
import { Heart, Home, Sparkles } from 'lucide-react';
import { motion } from 'motion/react';

const links = [
  ['/', 'Home', Home],
  ['/recommendations', 'Discover', Sparkles],
  ['/favorites', 'Favorites', Heart],
] as const;

export function Navigation() {
  const { pathname } = useLocation();
  return (
    <motion.header initial={{ y: -80 }} animate={{ y: 0 }} className="sticky top-0 z-50 border-b border-border bg-background/90 backdrop-blur-xl">
      <nav aria-label="Primary navigation" className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 sm:px-8 lg:px-10">
        <Link to="/" className="flex items-center gap-3" aria-label="RWI7A home">
          <span className="grid size-10 place-items-center rounded-full border border-accent/50 bg-primary font-serif text-xl text-[#f5e9d4] shadow-lg">R</span>
          <span className="flex flex-col">
            <span className="font-serif text-2xl leading-none tracking-[0.16em]">RWI7A</span>
            <span className="mt-1 text-[0.5rem] font-semibold uppercase tracking-[0.28em] text-[#8d6b43]">Olfactory studio</span>
          </span>
        </Link>
        <div className="flex gap-1 rounded-full border border-border bg-white/50 p-1 shadow-sm">
          {links.map(([path, label, Icon]) => {
            const active = pathname === path;
            return <Link key={path} to={path} aria-label={label} aria-current={active ? 'page' : undefined} className={`flex items-center gap-2 rounded-full px-3 py-2.5 text-xs font-semibold uppercase tracking-wider sm:px-4 ${active ? 'bg-primary text-primary-foreground shadow-md' : 'text-[#607168]'}`}>
              <Icon className="size-4" /><span className="hidden sm:inline">{label}</span>
            </Link>;
          })}
        </div>
      </nav>
    </motion.header>
  );
}
