import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import Home from './pages/Home';
import Screening from './pages/Screening';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import HardwareMLGuide from './pages/HardwareMLGuide';

function App() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar />
      <main className="flex-grow-1 d-flex flex-column">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/screening" element={<Screening />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/hardware-guide" element={<HardwareMLGuide />} />

          {/* Catch-all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
