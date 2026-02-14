import { motion } from 'motion/react';
import { Heart, Trash2 } from 'lucide-react';
import { useFavorites } from '../context/FavoritesContext';
import { PerfumeCard } from '../components/PerfumeCard';

export function FavoritesPage() {
  const { favorites } = useFavorites();

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', bounce: 0.5, duration: 0.8 }}
            className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full mb-4 shadow-lg relative"
          >
            <Heart className="w-10 h-10 text-white fill-current" />
            <motion.div
              className="absolute inset-0 rounded-full"
              animate={{
                boxShadow: [
                  '0 0 0 0 rgba(236, 72, 153, 0.4)',
                  '0 0 0 20px rgba(236, 72, 153, 0)',
                ],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeOut',
              }}
            />
          </motion.div>
          <h1 className="text-5xl font-serif mb-4 bg-gradient-to-r from-pink-500 to-purple-600 bg-clip-text text-transparent">
            Your Favorites
          </h1>
          <p className="text-gray-600 text-lg">
            {favorites.length === 0 
              ? 'You haven\'t added any favorites yet'
              : `${favorites.length} ${favorites.length === 1 ? 'perfume' : 'perfumes'} saved`
            }
          </p>
        </motion.div>

        {/* Favorites Grid */}
        {favorites.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {favorites.map((perfume, index) => (
              <PerfumeCard
                key={perfume.id}
                perfume={perfume}
                delay={index * 0.1}
              />
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', bounce: 0.4 }}
            className="max-w-md mx-auto text-center py-16"
          >
            <motion.img
              src={"C:\\Users\\Bochra\\RWI7A\\frontend\\src\\assets\\291f0be50f0ac6a9df16bb3adcc52b03aa062ef3.png"}
              alt="RWI7A Logo"
              className="w-32 h-32 mx-auto mb-6 opacity-40"
              animate={{ 
                y: [0, -10, 0],
                opacity: [0.3, 0.5, 0.3]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
            <h3 className="text-2xl mb-4 text-gray-700">No favorites yet</h3>
            <p className="text-gray-500 mb-8">
              Start exploring perfumes and click the heart icon to save your favorites here.
            </p>
            <motion.a
              href="/recommendations"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-block px-8 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all"
            >
              Discover Perfumes
            </motion.a>
          </motion.div>
        )}
      </div>
    </div>
  );
}