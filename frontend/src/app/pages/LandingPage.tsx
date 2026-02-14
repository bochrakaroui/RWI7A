import { useNavigate } from 'react-router';
import { motion } from 'motion/react';
import { Sparkles, ArrowRight } from 'lucide-react';
import logo from '../../assets/291f0be50f0ac6a9df16bb3adcc52b03aa062ef3.png';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-pink-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        {/* Hero Section */}
        <div className="text-center">
          {/* Animated Logo */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ 
              scale: 1, 
              opacity: 1,
              y: [0, -10, 0]
            }}
            transition={{ 
              scale: { type: 'spring', duration: 1.2, bounce: 0.4 },
              opacity: { duration: 0.8 },
              y: { 
                duration: 2,
                repeat: Infinity,
                repeatType: "reverse",
                ease: "easeInOut"
              }
            }}
            className="inline-block mb-8"
          >
            <motion.img 
              src={logo}
              alt="RWI7A Perfume Studio Logo" 
              className="w-94 h-94 object-contain drop-shadow-2xl"
              whileHover={{ 
                scale: 1.05,
                rotate: [0, -3, 3, -3, 0],
                transition: { duration: 0.6 }
              }}
            />
          </motion.div>

          {/* Brand Name */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, type: 'spring', bounce: 0.3 }}
            className="text-7xl font-serif mb-4 bg-gradient-to-r from-pink-500 via-purple-600 to-pink-500 bg-clip-text text-transparent"
          >
            RWI7A
          </motion.h1>

          {/* Tagline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, type: 'spring', bounce: 0.3 }}
            className="text-2xl text-gray-600 mb-12"
          >
            Find your perfect fragrance
          </motion.p>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, type: 'spring', bounce: 0.3 }}
            className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto leading-relaxed"
          >
            Discover personalized perfume recommendations based on your unique preferences.
            Let us guide you through a world of luxurious scents tailored just for you.
          </motion.p>

          {/* CTA Button */}
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, type: 'spring', bounce: 0.3 }}
            whileHover={{ scale: 1.05, boxShadow: '0 20px 40px rgba(236, 72, 153, 0.3)' }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/recommendations')}
            className="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-full shadow-lg hover:shadow-2xl transition-all duration-300"
          >
            <span className="text-lg">Get Recommendations</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </motion.button>
        </div>

        {/* Feature Cards */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1, type: 'spring', bounce: 0.3 }}
          className="mt-24 grid md:grid-cols-3 gap-8"
        >
          {[
            {
              title: 'Personalized',
              description: 'Get recommendations based on your favorite scents',
              icon: '✨',
            },
            {
              title: 'Curated',
              description: 'Explore carefully selected luxury fragrances',
              icon: '💐',
            },
            {
              title: 'Simple',
              description: 'Easy to use, beautiful interface',
              icon: '💕',
            },
          ].map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ 
                delay: 1.3 + index * 0.15,
                type: 'spring',
                bounce: 0.4
              }}
              whileHover={{ 
                y: -8,
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
                transition: { type: 'spring', bounce: 0.6 }
              }}
              className="bg-white/60 backdrop-blur-sm rounded-3xl p-8 text-center shadow-md hover:shadow-xl transition-shadow"
            >
              <div className="text-5xl mb-4">{feature.icon}</div>
              <h3 className="text-xl mb-2 text-gray-800">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}