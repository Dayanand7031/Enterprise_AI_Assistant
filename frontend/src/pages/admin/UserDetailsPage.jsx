import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../../services/api";

function UserDetailsPage() {
  const { user_id } = useParams();
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchUser();
  }, [user_id]);

  const fetchUser = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/api/admin/users/${user_id}`
      );

      setUser(response.data);
    } catch (err) {
      console.error(
        "Failed to load user:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to load user."
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // Loading
  // --------------------------------------------------

  if (loading) {
    return (
      <div className="admin-page">
        <div className="admin-loading">
          Loading user...
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // Error
  // --------------------------------------------------

  if (error) {
    return (
      <div className="admin-page">

        <button
          type="button"
          className="admin-back-button"
          onClick={() =>
            navigate("/admin/users")
          }
        >
          ← Back to Users
        </button>

        <div className="admin-error">
          {error}
        </div>

      </div>
    );
  }

  if (!user) {
    return null;
  }

  // --------------------------------------------------
  // Page
  // --------------------------------------------------

  return (
    <div className="admin-page">

      {/* Back */}
      <button
        type="button"
        className="admin-back-button"
        onClick={() =>
          navigate("/admin/users")
        }
      >
        ← Back to Users
      </button>

      {/* Header */}
      <div className="admin-header">
        <h1>
          User Details
        </h1>

        <p>
          View user information and application access.
        </p>
      </div>

      {/* User Information */}
      <div className="admin-card">

        <div className="admin-card-header">
          <h2>
            User Information
          </h2>

          <p>
            Basic account information.
          </p>
        </div>

        <div className="admin-user-grid">

          {/* User ID */}
          <div>
            <div className="admin-info-label">
              User ID
            </div>

            <div className="admin-info-value">
              {user.id}
            </div>
          </div>

          {/* Name */}
          <div>
            <div className="admin-info-label">
              Name
            </div>

            <div className="admin-info-value">
              {user.name}
            </div>
          </div>

          {/* Email */}
          <div>
            <div className="admin-info-label">
              Email
            </div>

            <div className="admin-info-value">
              {user.email}
            </div>
          </div>

          {/* Role */}
          <div>
            <div className="admin-info-label">
              Role
            </div>

            <div className="admin-info-value">

              {user.role ? (

                <span className="admin-role-badge">
                  {user.role}
                </span>

              ) : (

                <span className="admin-no-role">
                  No role assigned
                </span>

              )}

            </div>
          </div>

        </div>

      </div>

      {/* Application Access */}
      <div className="admin-card">

        <div className="admin-card-header">

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "20px",
            }}
          >

            <div>
              <h2>
                Application Access
              </h2>

              <p>
                Manage applications available to this user.
              </p>
            </div>

            <button
              type="button"
              className="admin-button"
              onClick={() =>
                navigate(
                  `/admin/users/${user.id}/access`
                )
              }
            >
              Manage Access
            </button>

          </div>

        </div>

        <div className="admin-access-list">

          {user.applications.map(
            (application) => (

              <div
                key={application.application}
                className="admin-access-row"
              >

                <div>
                  <div className="admin-access-name">
                    {application.application}
                  </div>

                  <div className="admin-access-status">
                    Application access
                  </div>
                </div>

                {application.enabled ? (

                  <span className="admin-status-enabled">
                    Enabled
                  </span>

                ) : (

                  <span className="admin-status-disabled">
                    Disabled
                  </span>

                )}

              </div>

            )
          )}

        </div>

      </div>

    </div>
  );
}

export default UserDetailsPage;