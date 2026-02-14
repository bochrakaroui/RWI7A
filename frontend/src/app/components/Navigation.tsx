import { Link, useLocation } from 'react-router';
import { Heart, Home, Sparkles } from 'lucide-react';
import { motion } from 'motion/react';
import logo from '../../assets/291f0be50f0ac6a9df16bb3adcc52b03aa062ef3.png';

export function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/recommendations', label: 'Discover', icon: Sparkles },
    { path: '/favorites', label: 'Favorites', icon: Heart },
  ];

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-pink-100"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-17">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <motion.img 
              src={logo}
              alt="RWI7A Logo" 
              className="w-24 h-24 object-contain"
              whileHover={{ 
                scale: 1.1,
                rotate: [0, -5, 5, -5, 0],
                transition: { duration: 0.5 }
              }}
            />
            <span className="text-2xl font-serif bg-gradient-to-r from-pink-500 to-purple-600 bg-clip-text text-transparent">
              RWI7A
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            {navItems.map(({ path, label, icon: Icon }) => {
              const isActive = location.pathname === path;
              return (
                <Link
                  key={path}
                  to={path}
                  className="relative px-4 py-2 rounded-full transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-pink-500' : 'text-gray-600'}`} />
                    <span className={`text-sm ${isActive ? 'text-pink-500' : 'text-gray-600'} hover:text-pink-400`}>
                      {label}
                    </span>
                  </div>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 bg-pink-50 rounded-full -z-10"
                      transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}