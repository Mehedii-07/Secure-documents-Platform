import { Routes, Route } from 'react-router-dom'
import './App.css'

/**
 * Root application component.
 *
 * Routes are added issue-by-issue:
 * Issue #5  → /login, /register
 * Issue #6  → /profile
 * Issue #10 → /documents
 * Issue #22 → /ai/chat
 * Issue #23 → /compliance
 */
function App() {
  return (
    <Routes>
      {/* Placeholder — replaced in Issue #4 Frontend Architecture */}
      <Route
        path="*"
        element={
          <div className="app-placeholder">
            <div className="placeholder-card">
              <div className="placeholder-icon">🔒</div>
              <h1>AI Document & Compliance Platform</h1>
              <p>Platform is starting up. Backend and frontend scaffolding complete.</p>
              <p className="placeholder-status">
                <span className="status-dot" />
                Issue #1: Project Setup — Complete
              </p>
            </div>
          </div>
        }
      />
    </Routes>
  )
}

export default App
