import { BrowserRouter, Routes, Route } from 'react-router';
import { FavoritesProvider } from './context/FavoritesContext';
import { Navigation } from './components/Navigation';
import { LandingPage } from './pages/LandingPage';
import { RecommendationPage } from './pages/RecommendationPage';
import { FavoritesPage } from './pages/FavoritesPage';

export default function App() {
  return (
    <BrowserRouter>
      <FavoritesProvider>
        <div className="min-h-screen bg-white">
          <Navigation />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/recommendations" element={<RecommendationPage />} />
            <Route path="/favorites" element={<FavoritesPage />} />
          </Routes>
        </div>
      </FavoritesProvider>
    </BrowserRouter>
  );
}
