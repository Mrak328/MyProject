import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider, FavoritesProvider } from './context';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import ListingDetail from './pages/ListingDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import Favorites from './pages/Favorites';
import CreateListing from './pages/CreateListing';
import UserProfile from './pages/UserProfile';
import AdminPanel from './pages/AdminPanel';
import AdminAnalytics from './pages/AdminAnalytics';
import Moderation from './pages/Moderation';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <AuthProvider>
            <FavoritesProvider>
                <BrowserRouter>
                    <div className="app">
                        <Header />
                        <main className="main-content">
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/listing/:id" element={<ListingDetail />} />
                                <Route path="/login" element={<Login />} />
                                <Route path="/register" element={<Register />} />
                                <Route path="/favorites" element={
                                    <ProtectedRoute><Favorites /></ProtectedRoute>
                                } />
                                <Route path="/create-listing" element={
                                    <ProtectedRoute><CreateListing /></ProtectedRoute>
                                } />
                                <Route path="/user/:id" element={<UserProfile />} />

                                {/* Админ */}
                                <Route path="/admin" element={
                                    <ProtectedRoute roles={[1]}><AdminPanel /></ProtectedRoute>
                                } />
                                <Route path="/admin/analytics" element={
                                    <ProtectedRoute roles={[1]}><AdminAnalytics /></ProtectedRoute>
                                } />

                                {/* Модерация */}
                                <Route path="/moderation" element={
                                    <ProtectedRoute roles={[1, 2]}><Moderation /></ProtectedRoute>
                                } />
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