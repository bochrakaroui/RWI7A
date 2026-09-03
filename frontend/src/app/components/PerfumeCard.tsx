import { Heart, Star } from 'lucide-react';
import { motion } from 'motion/react';
import { Perfume } from '../data/perfumes';
import { useFavorites } from '../context/FavoritesContext';

interface PerfumeCardProps {
  perfume: Perfume;
  similarityScore?: number;
  delay?: number;
}

export function PerfumeCard({ perfume, similarityScore, delay = 0 }: PerfumeCardProps) {
  const { addFavorite, removeFavorite, isFavorite } = useFavorites();
  const liked = isFavorite(perfume.id);
  const toggleFavorite = () => liked ? removeFavorite(perfume.id) : addFavorite(perfume);

  return (
    <motion.article initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay, duration: 0.45 }} whileHover={{ y: -6 }} className="group overflow-hidden rounded-[1.6rem] border border-border bg-card shadow-[0_16px_45px_rgba(22,35,29,0.07)]">
      <div className="relative h-72 overflow-hidden bg-secondary">
        <img src={perfume.image} alt={`${perfume.name} by ${perfume.brand}`} className="h-full w-full object-cover transition duration-700 group-hover:scale-105" />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,transparent_45%,rgba(16,35,28,0.52))]" />
        <span className="absolute bottom-5 left-5 text-[0.6rem] font-semibold uppercase tracking-[0.24em] text-white/85">{perfume.brand}</span>
        <button type="button" onClick={toggleFavorite} aria-label={liked ? `Remove ${perfume.name} from favorites` : `Add ${perfume.name} to favorites`} className={`absolute right-4 top-4 grid size-10 place-items-center rounded-full border backdrop-blur-md transition ${liked ? 'border-primary bg-primary text-white' : 'border-white/60 bg-white/80 text-primary hover:bg-white'}`}>
          <Heart className={`size-4 ${liked ? 'fill-current' : ''}`} />
        </button>
        {similarityScore !== undefined && <span className="absolute left-4 top-4 rounded-full border border-white/40 bg-primary/80 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur-md">{similarityScore}% match</span>}
      </div>

      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div><h3 className="font-serif text-2xl font-semibold leading-tight">{perfume.name}</h3><p className="mt-2 text-sm leading-6 text-muted-foreground">{perfume.description}</p></div>
          <span className="whitespace-nowrap font-serif text-xl font-semibold text-[#765936]">${perfume.price}</span>
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          {[...perfume.notes.top.slice(0, 2), ...perfume.notes.middle.slice(0, 1)].map(note => <span key={note} className="rounded-full border border-[#b28a58]/20 bg-[#f3ecdf] px-3 py-1 text-[0.62rem] font-semibold uppercase tracking-wider text-[#765936]">{note}</span>)}
        </div>
        <div className="mt-6 flex items-center justify-between border-t border-border pt-5">
          <span className="flex items-center gap-1.5 text-sm"><Star className="size-3.5 fill-[#b28a58] text-[#b28a58]" />{perfume.rating}</span>
          <span className="text-[0.58rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground">Curated selection</span>
        </div>
      </div>
    </motion.article>
  );
}
