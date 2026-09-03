import { useNavigate } from 'react-router';
import { motion } from 'motion/react';
import { ArrowRight, ChevronRight, Feather, ShieldCheck, Sparkles } from 'lucide-react';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <main className="overflow-hidden bg-background text-foreground">
      <section className="relative isolate min-h-[calc(100vh-5rem)]">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -right-40 top-8 size-[32rem] rounded-full border border-accent/15" />
          <div className="absolute -right-16 top-36 size-[23rem] rounded-full border border-primary/10" />
          <div className="absolute bottom-0 left-0 h-36 w-full bg-[linear-gradient(180deg,transparent,rgba(255,253,248,0.55))]" />
        </div>

        <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 py-16 sm:px-8 md:py-20 lg:grid-cols-[1.06fr_0.94fr] lg:px-10 lg:py-24">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.75 }}>
            <div className="mb-7 flex items-center gap-3 text-[0.68rem] font-semibold uppercase tracking-[0.28em] text-[#8d6b43]">
              <span className="h-px w-10 bg-accent" /> Private fragrance discovery
            </div>
            <h1 className="max-w-3xl font-serif text-[3.9rem] font-medium leading-[0.88] tracking-[-0.055em] sm:text-[5.3rem] lg:text-[6.4rem]">
              Find the scent <span className="mt-2 block italic text-[#8d6b43]">that feels inevitable.</span>
            </h1>
            <p className="mt-8 max-w-xl text-base leading-8 text-[#58665f] sm:text-lg">
              Begin with a fragrance you love. RWI7A reads its notes, structure, and accords to reveal your closest olfactory matches from more than 24,000 compositions.
            </p>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center">
              <motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} onClick={() => navigate('/recommendations')} className="group inline-flex items-center justify-center gap-4 rounded-full bg-primary px-7 py-4 text-sm font-semibold text-primary-foreground shadow-[0_18px_45px_rgba(23,56,45,0.2)]">
                Discover your match
                <span className="grid size-7 place-items-center rounded-full bg-white/10"><ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" /></span>
              </motion.button>
              <button onClick={() => navigate('/recommendations')} className="group inline-flex items-center justify-center gap-1.5 px-4 py-3 text-sm font-semibold text-[#44564d]">
                Explore the collection <ChevronRight className="size-4 transition-transform group-hover:translate-x-1" />
              </button>
            </div>
            <dl className="mt-14 grid max-w-xl grid-cols-3 border-y border-border py-5">
              {[
                ['24K+', 'scents'], ['4-layer', 'analysis'], ['Top 5', 'matches'],
              ].map(([value, label], index) => (
                <div key={label} className={index === 0 ? '' : 'border-l border-border pl-5 sm:pl-7'}>
                  <dt className="font-serif text-2xl font-semibold sm:text-3xl">{value}</dt>
                  <dd className="mt-1 text-[0.58rem] font-semibold uppercase tracking-[0.22em] text-[#7b827e]">{label}</dd>
                </div>
              ))}
            </dl>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15, duration: 0.8 }} className="relative mx-auto min-h-[34rem] w-full max-w-[34rem]">
            <div className="absolute inset-x-8 top-8 h-[29rem] rounded-[50%_50%_48%_52%/43%_48%_52%_57%] bg-[#e6dac9] shadow-[inset_0_0_80px_rgba(255,255,255,0.65)]" />
            <div className="absolute left-1/2 top-5 h-[27rem] w-px -translate-x-1/2 bg-accent/25" />
            <motion.div animate={{ y: [0, -8, 0] }} transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }} className="absolute left-1/2 top-24 -translate-x-1/2">
              <div className="mx-auto h-12 w-24 rounded-t-lg border border-[#d2b98f]/50 bg-[linear-gradient(90deg,#8d6b43,#d7bd91_48%,#80613e)] shadow-lg" />
              <div className="relative h-72 w-52 overflow-hidden rounded-[2rem_2rem_3.7rem_3.7rem] border border-white/30 bg-primary shadow-[0_38px_65px_rgba(23,56,45,0.3)]">
                <div className="absolute inset-y-0 left-0 w-1/3 bg-white/[0.055] blur-xl" />
                <div className="absolute inset-x-5 top-24 border-y border-[#d7bd91]/45 py-7 text-center">
                  <span className="block font-serif text-3xl tracking-[0.2em] text-[#f7efdf]">RWI7A</span>
                  <span className="mt-2 block text-[0.52rem] uppercase tracking-[0.38em] text-[#d7bd91]">Eau de découverte</span>
                </div>
              </div>
            </motion.div>
            <NoteCard className="left-0 top-20" icon={<Feather className="size-4" />} label="Heart note" value="Jasmine" />
            <NoteCard className="bottom-14 right-0" icon={<Sparkles className="size-4" />} label="Signature" value="Warm woods" />
          </motion.div>
        </div>
      </section>

      <section className="border-y border-border bg-card/70">
        <div className="mx-auto grid max-w-7xl gap-px bg-primary/10 sm:grid-cols-3">
          {[
            { icon: Sparkles, number: '01', title: 'Select your signature', copy: 'Choose a perfume you already know and love.' },
            { icon: Feather, number: '02', title: 'Read its composition', copy: 'We compare the notes, pyramid, and accords.' },
            { icon: ShieldCheck, number: '03', title: 'Meet your matches', copy: 'Receive five transparent, explainable results.' },
          ].map(({ icon: Icon, number, title, copy }) => (
            <article key={number} className="bg-card px-7 py-9 lg:px-10">
              <div className="flex items-center justify-between"><Icon className="size-5 text-[#8d6b43]" /><span className="font-serif text-xl italic text-[#b9a991]">{number}</span></div>
              <h2 className="mt-7 font-serif text-2xl font-semibold">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{copy}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function NoteCard({ className, icon, label, value }: { className: string; icon: React.ReactNode; label: string; value: string }) {
  return <div className={`absolute ${className} rounded-2xl border border-white/60 bg-card/85 px-4 py-3 shadow-[0_18px_45px_rgba(22,35,29,0.1)] backdrop-blur-md`}>
    <div className="flex items-center gap-3">
      <span className="grid size-9 place-items-center rounded-full bg-secondary text-[#8d6b43]">{icon}</span>
      <div><p className="text-[0.58rem] uppercase tracking-[0.2em] text-[#8a8f8c]">{label}</p><p className="mt-0.5 font-serif text-lg">{value}</p></div>
    </div>
  </div>;
}
