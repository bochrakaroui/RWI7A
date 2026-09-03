import { Link } from 'react-router';
import { motion } from 'motion/react';
import { ArrowRight, Heart, Sparkles } from 'lucide-react';
import { useFavorites } from '../context/FavoritesContext';
import { PerfumeCard } from '../components/PerfumeCard';

export function FavoritesPage() {
  const { favorites } = useFavorites();

  return (
    <main className="min-h-[calc(100vh-5rem)] bg-background px-5 py-12 text-foreground sm:px-8 lg:px-10 lg:py-16">
      <div className="mx-auto max-w-7xl">
        <motion.header initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col justify-between gap-7 border-b border-border pb-9 sm:flex-row sm:items-end">
          <div className="max-w-3xl">
            <p className="flex items-center gap-3 text-[0.65rem] font-semibold uppercase tracking-[0.3em] text-[#8d6b43]"><span className="h-px w-8 bg-accent" />Your fragrance wardrobe</p>
            <h1 className="mt-5 font-serif text-5xl font-medium leading-[0.95] tracking-[-0.04em] sm:text-7xl">The scents worth <span className="italic text-[#8d6b43]">remembering.</span></h1>
          </div>
          <div className="flex items-center gap-3 rounded-full border border-border bg-card px-4 py-2.5 shadow-sm">
            <Heart className="size-4 fill-[#8d6b43] text-[#8d6b43]" />
            <span className="text-xs font-semibold uppercase tracking-wider">{favorites.length} saved</span>
          </div>
        </motion.header>

        {favorites.length > 0 ? (
          <section className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {favorites.map((perfume, index) => <PerfumeCard key={perfume.id} perfume={perfume} delay={index * 0.08} />)}
          </section>
        ) : (
          <motion.section initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.15 }} className="mx-auto mt-16 max-w-2xl rounded-[2rem] border border-border bg-card px-7 py-14 text-center shadow-[0_25px_70px_rgba(22,35,29,0.07)] sm:px-14">
            <div className="relative mx-auto h-40 w-32">
              <div className="absolute left-1/2 top-0 h-7 w-14 -translate-x-1/2 rounded-t-md bg-[#a88452]" />
              <div className="absolute inset-x-0 bottom-0 h-32 rounded-[1.4rem_1.4rem_2.5rem_2.5rem] bg-primary shadow-[0_22px_45px_rgba(23,56,45,0.22)]">
                <div className="absolute inset-x-4 top-10 border-y border-[#d7bd91]/40 py-4 font-serif text-xl tracking-[0.16em] text-[#f7efdf]">RWI7A</div>
              </div>
              <motion.span animate={{ scale: [1, 1.08, 1] }} transition={{ duration: 2.4, repeat: Infinity }} className="absolute -right-5 top-8 grid size-11 place-items-center rounded-full border border-accent/30 bg-[#f1e7d7] text-[#8d6b43]"><Sparkles className="size-4" /></motion.span>
            </div>
            <h2 className="mt-8 font-serif text-3xl font-semibold">Your wardrobe is waiting.</h2>
            <p className="mx-auto mt-3 max-w-md text-sm leading-7 text-muted-foreground">Explore the collection and save fragrances that deserve a place in your personal edit.</p>
            <Link to="/recommendations" className="group mt-8 inline-flex items-center gap-3 rounded-full bg-primary px-6 py-3.5 text-sm font-semibold text-primary-foreground shadow-lg">
              Discover fragrances <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </motion.section>
        )}
      </div>
    </main>
  );
}
