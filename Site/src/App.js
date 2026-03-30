import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import ListingDetail from './pages/ListingDetail';
import Login from './pages/Login';
import AdminPanel from './pages/AdminPanel';
import AdminAnalytics from './pages/AdminAnalytics';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <div className="app">
                    <Header />
                    <main className="main-content">
                        <Routes>
                            {/* Публичные маршруты */}
                            <Route path="/" element={<Home />} />
                            <Route path="/listing/:id" element={<ListingDetail />} />
                            <Route path="/login" element={<Login />} />

                            {/* Админские маршруты (только для админа) */}
                            <Route path="/admin" element={
                                <ProtectedRoute requireAdmin={true}>
                                    <AdminPanel />
                                </ProtectedRoute>
                            } />
                            <Route path="/analytics" element={
                                <ProtectedRoute requireAdmin={true}>
                                    <AdminAnalytics />
                                </ProtectedRoute>
                            } />
                        </Routes>
                    </main>
                    <Footer />
                </div>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;