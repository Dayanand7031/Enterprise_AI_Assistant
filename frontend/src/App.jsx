import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import ChatPage from "./pages/ChatPage";
import AdminDashboard from "./pages/admin/AdminDashboard";
import UsersPage from "./pages/admin/UsersPage";
import UserDetailsPage from "./pages/admin/UserDetailsPage";
import AccessManagementPage from "./pages/admin/AccessManagementPage";

import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* Root */}
        <Route
          path="/"
          element={<LandingPage />}
        />

        {/* Login */}
        <Route
          path="/login"
          element={<LoginPage />}
        />

        {/* Signup */}
        <Route
          path="/signup"
          element={<SignupPage />}
        />

        {/* Protected Chat */}
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          }
        />

        {/* Admin Dashboard */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* Admin Users */}
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute>
                <UsersPage />
              </ProtectedRoute>
            }
          />

          {/* Admin User Details */}
          <Route
            path="/admin/users/:user_id"
            element={
              <ProtectedRoute>
                <UserDetailsPage />
              </ProtectedRoute>
            }
          />

          {/* Admin Application Access */}
          <Route
            path="/admin/users/:user_id/access"
            element={
              <ProtectedRoute>
                <AccessManagementPage />
              </ProtectedRoute>
            }
          />

        {/* Unknown route */}
        <Route
          path="*"
          element={
            <Navigate
              to="/login"
              replace
            />
          }
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;