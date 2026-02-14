import { Star, Heart } from 'lucide-react';
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
  const isLiked = isFavorite(perfume.id);

  const handleToggleFavorite = () => {
    if (isLiked) {
      removeFavorite(perfume.id);
    } else {
      addFavorite(perfume);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ y: -8, transition: { duration: 0.2 } }}
      className="group relative bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-2xl transition-shadow duration-300"
    >
      {/* Image Container */}
      <div className="relative h-64 overflow-hidden bg-gradient-to-br from-pink-50 to-purple-50">
        <img
          src={perfume.image}
          alt={perfume.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        
        {/* Favorite Button */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleToggleFavorite}
          className={`absolute top-4 right-4 w-10 h-10 rounded-full backdrop-blur-md flex items-center justify-center transition-colors ${
            isLiked ? 'bg-pink-500 text-white' : 'bg-white/90 text-gray-600 hover:text-pink-500'
          }`}
        >
          <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
        </motion.button>

        {/* Similarity Score Badge */}
        {similarityScore !== undefined && (
          <div className="absolute top-4 left-4 bg-gradient-to-r from-pink-500 to-purple-500 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg">
            {similarityScore}% Match
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Brand */}
        <p className="text-xs uppercase tracking-wider text-purple-500 mb-1">
          {perfume.brand}
        </p>

        {/* Name */}
        <h3 className="text-xl mb-2 text-gray-800">
          {perfume.name}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-500 mb-4 line-clamp-2">
          {perfume.description}
        </p>

        {/* Notes */}
        <div className="mb-4 space-y-2">
          <div className="flex flex-wrap gap-1">
            {perfume.notes.top.slice(0, 2).map(note => (
              <span
                key={note}
                className="text-xs px-2 py-1 bg-pink-50 text-pink-600 rounded-full"
              >
                {note}
              </span>
            ))}
            {perfume.notes.middle.slice(0, 1).map(note => (
              <span
                key={note}
                className="text-xs px-2 py-1 bg-purple-50 text-purple-600 rounded-full"
              >
                {note}
              </span>
            ))}
          </div>
        </div>

        {/* Rating and Price */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm text-gray-700">{perfume.rating}</span>
          </div>
          <div className="text-lg text-gray-800">
            ${perfume.price}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
