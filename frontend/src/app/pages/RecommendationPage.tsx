import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { ArrowRight, Check, FlaskConical, Loader2, Search, Sparkles, Star, Users, X } from 'lucide-react';
import { getBrands, getRecommendations, PerfumeInfo, searchPerfumes } from '../services/api';

export function RecommendationPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PerfumeInfo[]>([]);
  const [selectedPerfume, setSelectedPerfume] = useState<PerfumeInfo | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [recommendations, setRecommendations] = useState<PerfumeInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [brands, setBrands] = useState<string[]>([]);
  const [selectedBrand, setSelectedBrand] = useState('');
  const [brandInput, setBrandInput] = useState('');
  const [showBrands, setShowBrands] = useState(false);

  useEffect(() => {
    getBrands().then(data => setBrands(data.brands || [])).catch(() => setBrands([]));
  }, []);

  useEffect(() => {
    if (selectedPerfume && searchQuery === selectedPerfume.name.replace(/-/g, ' ')) return;
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    const timer = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const data = await searchPerfumes(searchQuery.trim(), selectedBrand || undefined, 10);
        setSearchResults(data.results || []);
        setShowResults(true);
      } catch {
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedBrand, selectedPerfume]);

  const visibleBrands = useMemo(
    () => brands.filter(brand => brand.toLowerCase().includes(brandInput.toLowerCase())).slice(0, 12),
    [brands, brandInput],
  );

  const selectPerfume = (perfume: PerfumeInfo) => {
    setSelectedPerfume(perfume);
    setSearchQuery(perfume.name.replace(/-/g, ' '));
    setSearchResults([]);
    setShowResults(false);
    setError(null);
  };

  const clearSelection = () => {
    setSelectedPerfume(null);
    setSearchQuery('');
    setRecommendations([]);
    setError(null);
  };

  const findMatches = async () => {
    if (!selectedPerfume) {
      setError('Choose a fragrance from the search results to continue.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getRecommendations(selectedPerfume.name, selectedPerfume.brand, 5, selectedPerfume.perfume_id);
      setRecommendations(data.recommendations || []);
    } catch {
      setError('We could not reach the scent library. Please try again in a moment.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-[calc(100vh-5rem)] bg-background px-5 py-12 text-foreground sm:px-8 lg:px-10 lg:py-16">
      <div className="mx-auto max-w-7xl">
        <motion.header initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl">
          <p className="flex items-center gap-3 text-[0.65rem] font-semibold uppercase tracking-[0.3em] text-[#8d6b43]"><span className="h-px w-8 bg-accent" />Scent concierge</p>
          <h1 className="mt-5 font-serif text-5xl font-medium leading-[0.95] tracking-[-0.04em] sm:text-7xl">Your next signature, <span className="italic text-[#8d6b43]">decoded.</span></h1>
          <p className="mt-6 max-w-2xl leading-7 text-[#647069]">Tell us one fragrance you love. We compare the full note pyramid and accords—not popularity—to uncover genuinely similar compositions.</p>
        </motion.header>

        <div className="mt-12 grid gap-8 lg:grid-cols-[0.38fr_0.62fr]">
          <motion.aside initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="rounded-[2rem] bg-primary p-7 text-primary-foreground shadow-[0_28px_70px_rgba(23,56,45,0.18)] sm:p-9">
            <span className="grid size-12 place-items-center rounded-full border border-white/15 bg-white/10 text-[#dcc49b]"><FlaskConical className="size-5" /></span>
            <h2 className="mt-8 font-serif text-3xl font-semibold">How your match is composed</h2>
            <ol className="mt-8 space-y-7">
              {[
                ['01', 'Choose your reference', 'Select the exact perfume—not just a similar name.'],
                ['02', 'We read every layer', 'Top, heart, base notes and accords are weighted together.'],
                ['03', 'Receive five matches', 'Each result includes a transparent similarity score.'],
              ].map(([number, title, copy]) => <li key={number} className="flex gap-4">
                <span className="font-serif text-xl italic text-[#d5b77f]">{number}</span>
                <div><h3 className="text-sm font-semibold">{title}</h3><p className="mt-1 text-sm leading-6 text-white/55">{copy}</p></div>
              </li>)}
            </ol>
            <div className="mt-10 border-t border-white/15 pt-6 text-xs leading-5 text-white/55">24,063 fragrances · 1,656 notes · No popularity bias</div>
          </motion.aside>

          <motion.section initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="relative rounded-[2rem] border border-border bg-card p-6 shadow-[0_25px_70px_rgba(22,35,29,0.08)] sm:p-9">
            <div className="flex items-center justify-between border-b border-border pb-6">
              <div><p className="text-[0.6rem] font-semibold uppercase tracking-[0.24em] text-[#8d6b43]">Your starting point</p><h2 className="mt-2 font-serif text-3xl font-semibold">Choose a fragrance</h2></div>
              <span className="hidden rounded-full bg-secondary px-3 py-1.5 text-[0.6rem] font-semibold uppercase tracking-wider text-[#6c5a42] sm:block">Step 1 of 1</span>
            </div>

            <div className="mt-7 grid gap-5 sm:grid-cols-[0.38fr_0.62fr]">
              <Field label="Brand" optional>
                <input
                  value={selectedBrand || brandInput}
                  onChange={event => { setBrandInput(event.target.value); setSelectedBrand(''); setShowBrands(true); }}
                  onFocus={() => setShowBrands(true)}
                  onBlur={() => setTimeout(() => setShowBrands(false), 160)}
                  placeholder="Any brand"
                  className="w-full rounded-xl border border-border bg-[#fbf8f2] px-4 py-3.5 text-sm outline-none transition focus:border-accent focus:ring-4 focus:ring-accent/10"
                />
                {showBrands && !selectedBrand && visibleBrands.length > 0 && <div className="absolute z-30 mt-2 max-h-64 w-full overflow-y-auto rounded-xl border border-border bg-card p-1.5 shadow-xl">
                  {visibleBrands.map(brand => <button key={brand} type="button" onMouseDown={() => { setSelectedBrand(brand); setBrandInput(''); setShowBrands(false); }} className="block w-full rounded-lg px-3 py-2.5 text-left text-sm hover:bg-secondary">{brand}</button>)}
                </div>}
              </Field>

              <Field label="Perfume name">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    value={searchQuery}
                    onChange={event => { setSearchQuery(event.target.value); if (selectedPerfume) setSelectedPerfume(null); }}
                    onFocus={() => searchResults.length > 0 && setShowResults(true)}
                    onBlur={() => setTimeout(() => setShowResults(false), 160)}
                    placeholder="Sauvage, Black Opium..."
                    className="w-full rounded-xl border border-border bg-[#fbf8f2] py-3.5 pl-11 pr-11 text-sm outline-none transition focus:border-accent focus:ring-4 focus:ring-accent/10"
                  />
                  {searchLoading && <Loader2 className="absolute right-4 top-1/2 size-4 -translate-y-1/2 animate-spin text-[#8d6b43]" />}
                </div>
                <AnimatePresence>
                  {showResults && searchResults.length > 0 && <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="absolute z-30 mt-2 max-h-72 w-full overflow-y-auto rounded-xl border border-border bg-card p-1.5 shadow-xl">
                    {searchResults.map((perfume, index) => <button key={perfume.perfume_id ?? `${perfume.brand}-${index}`} type="button" onMouseDown={() => selectPerfume(perfume)} className="flex w-full items-center justify-between rounded-lg px-3 py-3 text-left hover:bg-secondary">
                      <span><span className="block font-serif text-lg font-semibold capitalize">{perfume.name.replace(/-/g, ' ')}</span><span className="text-xs text-muted-foreground">{perfume.brand}</span></span>
                      <span className="flex items-center gap-1 text-xs text-[#8d6b43]"><Star className="size-3 fill-current" />{perfume.rating?.toFixed(2) || 'N/A'}</span>
                    </button>)}
                  </motion.div>}
                </AnimatePresence>
              </Field>
            </div>

            <AnimatePresence>
              {selectedPerfume && <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-6 flex items-center justify-between rounded-2xl border border-[#b28a58]/25 bg-[#f2eadc] p-4">
                <div className="flex items-center gap-4"><span className="grid size-10 place-items-center rounded-full bg-primary text-primary-foreground"><Check className="size-4" /></span><div><p className="text-[0.58rem] font-semibold uppercase tracking-[0.2em] text-[#8d6b43]">Selected</p><p className="mt-1 font-serif text-xl font-semibold capitalize">{selectedPerfume.name.replace(/-/g, ' ')}</p><p className="text-xs text-muted-foreground">{selectedPerfume.brand} · {selectedPerfume.rating?.toFixed(2) || 'Unrated'}</p></div></div>
                <button type="button" onClick={clearSelection} aria-label="Clear selection" className="grid size-9 place-items-center rounded-full text-muted-foreground hover:bg-white/70 hover:text-foreground"><X className="size-4" /></button>
              </motion.div>}
            </AnimatePresence>

            {error && <p role="alert" className="mt-5 rounded-xl border border-red-600/15 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

            <button type="button" onClick={findMatches} disabled={!selectedPerfume || loading} className="group mt-7 flex w-full items-center justify-center gap-3 rounded-full bg-primary px-6 py-4 text-sm font-semibold text-primary-foreground shadow-[0_15px_32px_rgba(23,56,45,0.18)] transition hover:-translate-y-0.5 disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-[#d8d3ca] disabled:text-[#8e918f] disabled:shadow-none">
              {loading ? <><Loader2 className="size-4 animate-spin" />Composing your edit...</> : <><Sparkles className="size-4" />Reveal my matches<ArrowRight className="size-4 transition-transform group-hover:translate-x-1" /></>}
            </button>
          </motion.section>
        </div>

        {recommendations.length > 0 && <motion.section initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} className="mt-20">
          <div className="flex flex-col justify-between gap-4 border-b border-border pb-7 sm:flex-row sm:items-end">
            <div><p className="text-[0.65rem] font-semibold uppercase tracking-[0.28em] text-[#8d6b43]">Your private edit</p><h2 className="mt-3 font-serif text-4xl font-semibold sm:text-5xl">Five scents, selected for you.</h2></div>
            <p className="max-w-sm text-sm leading-6 text-muted-foreground">Ranked by note structure, pyramid position, and accord similarity.</p>
          </div>
          <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {recommendations.map((perfume, index) => <ResultCard key={perfume.perfume_id ?? `${perfume.brand}-${index}`} perfume={perfume} rank={index + 1} />)}
          </div>
        </motion.section>}
      </div>
    </main>
  );
}

function Field({ label, optional, children }: { label: string; optional?: boolean; children: React.ReactNode }) {
  return <label className="relative block"><span className="mb-2 flex items-center gap-2 text-xs font-semibold text-foreground">{label}{optional && <span className="font-normal text-muted-foreground">Optional</span>}</span>{children}</label>;
}

function ResultCard({ perfume, rank }: { perfume: PerfumeInfo; rank: number }) {
  const match = Math.round((perfume.similarity || 0) * 100);
  return <motion.article whileHover={{ y: -5 }} className={`relative overflow-hidden rounded-[1.6rem] border border-border bg-card p-6 shadow-[0_14px_40px_rgba(22,35,29,0.06)] ${rank === 1 ? 'md:col-span-2 lg:col-span-1' : ''}`}>
    <div className="flex items-start justify-between"><span className="font-serif text-2xl italic text-[#b5a58d]">0{rank}</span><span className="grid size-14 place-items-center rounded-full border border-[#b28a58]/30 bg-[#f3ecdf] font-serif text-xl font-semibold text-[#765936]">{match}%</span></div>
    <p className="mt-8 text-[0.58rem] font-semibold uppercase tracking-[0.24em] text-[#8d6b43]">{perfume.brand}</p>
    <h3 className="mt-2 min-h-14 font-serif text-2xl font-semibold capitalize leading-tight">{perfume.name.replace(/-/g, ' ')}</h3>
    <div className="mt-6 flex items-center gap-4 border-t border-border pt-5 text-xs text-muted-foreground">
      <span className="flex items-center gap-1.5"><Star className="size-3.5 fill-[#b28a58] text-[#b28a58]" />{perfume.rating?.toFixed(2) || 'N/A'}</span>
      <span className="flex items-center gap-1.5"><Users className="size-3.5" />{perfume.review_count?.toLocaleString() || 0} reviews</span>
    </div>
  </motion.article>;
}
