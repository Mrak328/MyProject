import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { FavoritesProvider } from './context/FavoritesContext';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import ListingDetail from './pages/ListingDetail';
import UserProfile from './pages/UserProfile';
import Favorites from './pages/Favorites';
import Login from './pages/Login';
import AdminAnalytics from './pages/AdminAnalytics';  // ← ЭТОТ ИМПОРТ БЫЛ ПРОПУЩЕН!

function App() {
  return (
    <AuthProvider>
      <FavoritesProvider>
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true
          }}
        >
          <div className="app">
            <Header />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/listing/:id" element={<ListingDetail />} />
                <Route path="/user/:id" element={<UserProfile />} />
                <Route path="/favorites" element={<Favorites />} />
                <Route path="/login" element={<Login />} />
                <Route path="/analytics" element={<AdminAnalytics />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </FavoritesProvider>
    </AuthProvider>
  );
}

export default App;