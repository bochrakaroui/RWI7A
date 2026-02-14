import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, Sparkles, SlidersHorizontal } from 'lucide-react';
import { perfumes, Perfume } from '../data/perfumes';
import { PerfumeCard } from '../components/PerfumeCard';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Slider } from '../components/ui/slider';

export function RecommendationPage() {
  const [selectedPerfume1, setSelectedPerfume1] = useState('');
  const [selectedPerfume2, setSelectedPerfume2] = useState('');
  const [recommendations, setRecommendations] = useState<Array<Perfume & { score: number }>>([]);
  const [showFilters, setShowFilters] = useState(false);
  
  // Filter states
  const [noteFilter, setNoteFilter] = useState('all');
  const [priceRange, setPriceRange] = useState([0, 200]);
  const [brandFilter, setBrandFilter] = useState('all');

  const brands = Array.from(new Set(perfumes.map(p => p.brand)));
  const allNotes = Array.from(
    new Set(
      perfumes.flatMap(p => [...p.notes.top, ...p.notes.middle, ...p.notes.base])
    )
  );

  const generateRecommendations = () => {
    if (!selectedPerfume1 && !selectedPerfume2) return;

    const selected = perfumes.filter(p => 
      p.id === selectedPerfume1 || p.id === selectedPerfume2
    );

    if (selected.length === 0) return;

    // Calculate similarity scores
    const scored = perfumes
      .filter(p => p.id !== selectedPerfume1 && p.id !== selectedPerfume2)
      .map(perfume => {
        let score = 0;
        
        selected.forEach(sel => {
          // Check matching notes
          const allSelectedNotes = [...sel.notes.top, ...sel.notes.middle, ...sel.notes.base];
          const allPerfumeNotes = [...perfume.notes.top, ...perfume.notes.middle, ...perfume.notes.base];
          const matchingNotes = allSelectedNotes.filter(note => allPerfumeNotes.includes(note));
          score += matchingNotes.length * 10;

          // Brand similarity
          if (perfume.brand === sel.brand) score += 15;

          // Price similarity
          const priceDiff = Math.abs(perfume.price - sel.price);
          score += Math.max(0, 20 - priceDiff / 10);

          // Rating bonus
          score += perfume.rating * 5;
        });

        return { ...perfume, score: Math.min(100, Math.round(score)) };
      })
      .sort((a, b) => b.score - a.score);

    setRecommendations(scored.slice(0, 5));
  };

  const filteredRecommendations = recommendations.filter(perfume => {
    const matchesNote = noteFilter === 'all' || 
      [...perfume.notes.top, ...perfume.notes.middle, ...perfume.notes.base].includes(noteFilter);
    const matchesPrice = perfume.price >= priceRange[0] && perfume.price <= priceRange[1];
    const matchesBrand = brandFilter === 'all' || perfume.brand === brandFilter;
    
    return matchesNote && matchesPrice && matchesBrand;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-serif mb-4 bg-gradient-to-r from-pink-500 to-purple-600 bg-clip-text text-transparent">
            Discover Your Scent
          </h1>
          <p className="text-gray-600 text-lg">
            Select up to 2 perfumes you love, and we'll find similar fragrances for you
          </p>
        </motion.div>

        {/* Input Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-3xl shadow-xl p-8 mb-12"
        >
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* Perfume 1 Select */}
            <div>
              <label className="block text-sm text-gray-600 mb-2">First Perfume</label>
              <Select value={selectedPerfume1} onValueChange={setSelectedPerfume1}>
                <SelectTrigger className="w-full h-12 rounded-xl border-pink-200 focus:border-pink-400">
                  <SelectValue placeholder="Choose a perfume..." />
                </SelectTrigger>
                <SelectContent>
                  {perfumes.map(perfume => (
                    <SelectItem key={perfume.id} value={perfume.id}>
                      {perfume.name} - {perfume.brand}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Perfume 2 Select */}
            <div>
              <label className="block text-sm text-gray-600 mb-2">Second Perfume (Optional)</label>
              <Select value={selectedPerfume2} onValueChange={setSelectedPerfume2}>
                <SelectTrigger className="w-full h-12 rounded-xl border-pink-200 focus:border-pink-400">
                  <SelectValue placeholder="Choose another perfume..." />
                </SelectTrigger>
                <SelectContent>
                  {perfumes.map(perfume => (
                    <SelectItem key={perfume.id} value={perfume.id}>
                      {perfume.name} - {perfume.brand}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Submit Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={generateRecommendations}
            disabled={!selectedPerfume1 && !selectedPerfume2}
            className="w-full py-4 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            <span className="text-lg">Find Recommendations</span>
          </motion.button>
        </motion.div>

        {/* Filters */}
        {recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 text-gray-600 hover:text-pink-500 transition-colors mb-4"
            >
              <SlidersHorizontal className="w-5 h-5" />
              <span>{showFilters ? 'Hide' : 'Show'} Filters</span>
            </button>

            <AnimatePresence>
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-white rounded-2xl shadow-md p-6 mb-6"
                >
                  <div className="grid md:grid-cols-3 gap-6">
                    {/* Note Filter */}
                    <div>
                      <label className="block text-sm text-gray-600 mb-2">Filter by Note</label>
                      <Select value={noteFilter} onValueChange={setNoteFilter}>
                        <SelectTrigger className="w-full rounded-xl">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Notes</SelectItem>
                          {allNotes.map(note => (
                            <SelectItem key={note} value={note}>
                              {note}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Brand Filter */}
                    <div>
                      <label className="block text-sm text-gray-600 mb-2">Filter by Brand</label>
                      <Select value={brandFilter} onValueChange={setBrandFilter}>
                        <SelectTrigger className="w-full rounded-xl">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Brands</SelectItem>
                          {brands.map(brand => (
                            <SelectItem key={brand} value={brand}>
                              {brand}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Price Range */}
                    <div>
                      <label className="block text-sm text-gray-600 mb-2">
                        Price Range: ${priceRange[0]} - ${priceRange[1]}
                      </label>
                      <Slider
                        min={0}
                        max={200}
                        step={10}
                        value={priceRange}
                        onValueChange={setPriceRange}
                        className="mt-4"
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Recommendations Grid */}
        {filteredRecommendations.length > 0 ? (
          <div>
            <h2 className="text-3xl font-serif mb-8 text-gray-800">
              Top Recommendations for You
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {filteredRecommendations.map((perfume, index) => (
                <PerfumeCard
                  key={perfume.id}
                  perfume={perfume}
                  similarityScore={perfume.score}
                  delay={index * 0.1}
                />
              ))}
            </div>
          </div>
        ) : recommendations.length > 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              No perfumes match your current filters. Try adjusting them!
            </p>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center py-12"
          >
            <Search className="w-16 h-16 text-pink-200 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">
              Select your favorite perfumes above to get personalized recommendations
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}