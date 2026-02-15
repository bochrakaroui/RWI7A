import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, Sparkles, Loader2 } from 'lucide-react';
import { searchPerfumes, getRecommendations, getBrands, PerfumeInfo } from '../services/api';

export function RecommendationPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PerfumeInfo[]>([]);
  const [selectedPerfume, setSelectedPerfume] = useState<PerfumeInfo | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [recommendations, setRecommendations] = useState<PerfumeInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [brands, setBrands] = useState<string[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [brandInput, setBrandInput] = useState('');
  const [showBrandDropdown, setShowBrandDropdown] = useState(false);
  const [highlightedBrand, setHighlightedBrand] = useState<number>(-1);
  const brandInputRef = useRef<HTMLInputElement>(null);

  // Load brands on mount
  useEffect(() => {
    console.log('Loading brands...');
    getBrands()
      .then(data => {
        console.log('Brands loaded:', data);
        setBrands(data.brands || []);
      })
      .catch(err => console.error('Failed to load brands:', err));
  }, []);

  // Search as user types
  useEffect(() => {
    console.log('Search query changed:', searchQuery);
    
    // Don't search if a perfume is already selected (user selected from dropdown)
    if (selectedPerfume && searchQuery === selectedPerfume.name.replace(/-/g, ' ')) {
      return;
    }
    
    if (searchQuery.length < 2) {
      setSearchResults([]);
      setShowDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      setSearchLoading(true);
      console.log('Searching for:', searchQuery);
      
      try {
        const data = await searchPerfumes(searchQuery, selectedBrand || undefined, 10);
        console.log('Search results:', data);
        setSearchResults(data.results || []);
        setShowDropdown(true);
      } catch (err) {
        console.error('Search failed:', err);
        setSearchResults([]);
      }
      setSearchLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, selectedBrand, selectedPerfume]);

  const handleSelectPerfume = (perfume: PerfumeInfo) => {
    console.log('Selected perfume:', perfume);
    setSelectedPerfume(perfume);
    setSearchQuery(perfume.name.replace(/-/g, ' '));
    setSearchResults([]);  // Clear results to hide dropdown
    setShowDropdown(false);
  };

  const handleGetRecommendations = async () => {
    console.log('Get recommendations clicked, selectedPerfume:', selectedPerfume);
    
    if (!selectedPerfume) {
      setError('Please select a perfume first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getRecommendations(
        selectedPerfume.name,
        selectedPerfume.brand,
        5
      );
      console.log('Recommendations:', data);
      setRecommendations(data.recommendations || []);
    } catch (err) {
      console.error('Recommendations failed:', err);
      setError('Failed to get recommendations. Is the backend running?');
    }

    setLoading(false);
  };

  const handleClear = () => {
    setSelectedPerfume(null);
    setSearchQuery('');
    setRecommendations([]);
    setError(null);
  };

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
            Find Your Perfect Scent
          </h1>
          <p className="text-gray-600 text-lg">
            Search from 24,000+ perfumes and get AI-powered recommendations
          </p>
        </motion.div>

        {/* Search Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-2xl mx-auto mb-12"
        >
          <div className="bg-white rounded-2xl shadow-xl p-6">
            
            {/* Brand Filter Autocomplete */}
            <div className="mb-4 relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Brand (Optional)
              </label>
              <input
                ref={brandInputRef}
                type="text"
                value={selectedBrand ? selectedBrand : brandInput}
                onChange={e => {
                  setBrandInput(e.target.value);
                  setSelectedBrand('');
                  setShowBrandDropdown(true);
                  setHighlightedBrand(0);
                }}
                onFocus={() => {
                  setShowBrandDropdown(true);
                }}
                onBlur={() => {
                  setTimeout(() => setShowBrandDropdown(false), 200);
                }}
                onKeyDown={e => {
                  const filtered = brands.filter(b => b.toLowerCase().includes(brandInput.toLowerCase()));
                  if (!showBrandDropdown || filtered.length === 0) return;
                  if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setHighlightedBrand(prev => (prev + 1) % filtered.length);
                  } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setHighlightedBrand(prev => (prev - 1 + filtered.length) % filtered.length);
                  } else if (e.key === 'Enter') {
                    e.preventDefault();
                    if (highlightedBrand >= 0 && highlightedBrand < filtered.length) {
                      setSelectedBrand(filtered[highlightedBrand]);
                      setBrandInput('');
                      setShowBrandDropdown(false);
                    }
                  }
                }}
                placeholder="Type or select a brand"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
              />
              {showBrandDropdown && (brandInput || !selectedBrand) && brands.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                  <button
                    type="button"
                    className={`w-full px-4 py-2 text-left border-b border-gray-100 last:border-0 ${highlightedBrand === 0 ? 'bg-pink-100' : 'hover:bg-pink-50'}`}
                    onMouseDown={() => {
                      setSelectedBrand('');
                      setBrandInput('');
                      setShowBrandDropdown(false);
                    }}
                  >All Brands</button>
                  {brands
                    .filter(b => b.toLowerCase().includes(brandInput.toLowerCase()))
                    .map((brand, idx) => (
                      <button
                        key={brand}
                        type="button"
                        className={`w-full px-4 py-2 text-left border-b border-gray-100 last:border-0 ${highlightedBrand === idx + 1 ? 'bg-pink-100' : 'hover:bg-pink-50'}`}
                        onMouseDown={() => {
                          setSelectedBrand(brand);
                          setBrandInput('');
                          setShowBrandDropdown(false);
                        }}
                        onMouseEnter={() => setHighlightedBrand(idx + 1)}
                      >{brand}</button>
                    ))}
                </div>
              )}
            </div>

            {/* Search Input */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search for a Perfume
              </label>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    // Clear selection if user edits the input
                   if (selectedPerfume) {
                        setSelectedPerfume(null);
                    }

                  }}
                  onFocus={() => searchResults.length > 0 && setShowDropdown(true)}
                  onBlur={() => {
                    // Delay hiding dropdown to allow click on dropdown items
                    setTimeout(() => setShowDropdown(false), 200);
                  }}
                  placeholder="Type perfume name (e.g., Sauvage, Black Opium...)"
                  className="w-full pl-12 pr-12 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-pink-500 text-lg"
                />
                {searchLoading && (
                  <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pink-500 animate-spin" />
                )}
              </div>

              {/* Dropdown Results - Show only when showDropdown is true and results exist */}
              {showDropdown && searchResults.length > 0 && (
                <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-64 overflow-y-auto">
                  {searchResults.map((perfume, index) => (
                    <button
                      key={`${perfume.brand}-${perfume.name}-${index}`}
                      type="button"
                      onMouseDown={() => handleSelectPerfume(perfume)}
                      className="w-full px-4 py-3 text-left hover:bg-pink-50 flex justify-between items-center border-b border-gray-100 last:border-0"
                    >
                      <div>
                        <div className="font-medium text-gray-900">
                          {perfume.name.replace(/-/g, ' ')}
                        </div>
                        <div className="text-sm text-gray-500">{perfume.brand}</div>
                      </div>
                      <div className="text-sm text-gray-400">
                        ⭐ {perfume.rating?.toFixed(2) || 'N/A'}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Selected Perfume */}
            {selectedPerfume && (
              <div className="mt-4 p-4 bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl border border-pink-200">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-sm text-gray-500">Selected Perfume</div>
                    <div className="font-semibold text-lg text-gray-900">
                      {selectedPerfume.name.replace(/-/g, ' ')}
                    </div>
                    <div className="text-sm text-gray-600">
                      {selectedPerfume.brand} • ⭐ {selectedPerfume.rating?.toFixed(2)}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleClear}
                    className="text-sm text-pink-600 hover:text-pink-800"
                  >
                    Clear
                  </button>
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Get Recommendations Button */}
            <button
              type="button"
              onClick={handleGetRecommendations}
              disabled={!selectedPerfume || loading}
              className={`w-full mt-6 py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-2 transition-all ${
                selectedPerfume && !loading
                  ? 'bg-gradient-to-r from-pink-500 to-purple-600 text-white shadow-lg hover:shadow-xl cursor-pointer'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Finding Recommendations...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Get Recommendations
                </>
              )}
            </button>
          </div>
        </motion.div>

        {/* Recommendations Grid */}
        {recommendations.length > 0 && (
          <div>
            <h2 className="text-3xl font-serif text-center mb-8 text-gray-800">
              Perfumes You'll Love
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {recommendations.map((perfume, index) => (
                <div
                  key={`${perfume.brand}-${perfume.name}-${index}`}
                  className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow p-6"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 capitalize">
                        {perfume.name.replace(/-/g, ' ')}
                      </h3>
                      <p className="text-gray-500">{perfume.brand}</p>
                    </div>
                    {perfume.similarity !== undefined && (
                      <span className="px-3 py-1 bg-gradient-to-r from-pink-500 to-purple-600 text-white text-sm rounded-full">
                        {Math.round(perfume.similarity * 100)}% Match
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    <span>⭐ {perfume.rating?.toFixed(2) || 'N/A'}</span>
                    <span>📝 {perfume.review_count?.toLocaleString() || 0} reviews</span>
                  </div>
                  {perfume.brand_tier && (
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full capitalize">
                      {perfume.brand_tier} tier
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}