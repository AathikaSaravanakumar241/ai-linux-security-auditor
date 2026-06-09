import { Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// --- Page Imports ---
import DashboardPage from './pages/DashboardPage';
import NewAuditPage from './pages/NewAuditPage';
import AuditResultsPage from './pages/AuditResultsPage';
import AuditHistoryPage from './pages/AuditHistoryPage';
import LoginPage from './pages/LoginPage';

// --- Layout ---
import MainLayout from './layouts/MainLayout';

/**
 * App — Root component with route definitions in TypeScript.
 */
function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Authenticated routes wrapped in MainLayout */}
      <Route element={<MainLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/audit/new" element={<NewAuditPage />} />
        <Route path="/audit/:id" element={<AuditResultsPage />} />
        <Route path="/history" element={<AuditHistoryPage />} />
      </Route>

      {/* Default redirect */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
