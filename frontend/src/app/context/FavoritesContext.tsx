import { createContext, useContext, useState, ReactNode } from 'react';
import { Perfume } from '../data/perfumes';

interface FavoritesContextType {
  favorites: Perfume[];
  addFavorite: (perfume: Perfume) => void;
  removeFavorite: (id: string) => void;
  isFavorite: (id: string) => boolean;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined);

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const [favorites, setFavorites] = useState<Perfume[]>([]);

  const addFavorite = (perfume: Perfume) => {
    setFavorites(prev => {
      if (prev.find(p => p.id === perfume.id)) return prev;
      return [...prev, perfume];
    });
  };

  const removeFavorite = (id: string) => {
    setFavorites(prev => prev.filter(p => p.id !== id));
  };

  const isFavorite = (id: string) => {
    return favorites.some(p => p.id === id);
  };

  return (
    <FavoritesContext.Provider value={{ favorites, addFavorite, removeFavorite, isFavorite }}>
      {children}
    </FavoritesContext.Provider>
  );
}

export function useFavorites() {
  const context = useContext(FavoritesContext);
  if (!context) {
    throw new Error('useFavorites must be used within FavoritesProvider');
  }
  return context;
}
