import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../../services/api";

function AccessManagementPage() {
  const { user_id } = useParams();
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(null);
  const [error, setError] = useState("");

  // --------------------------------------------------
  // Load user
  // --------------------------------------------------

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
  // Toggle application access
  // --------------------------------------------------

  const handleToggle = async (
    application,
    currentEnabled
  ) => {
    try {
      setUpdating(application);
      setError("");

      await api.put(
        `/api/admin/users/${user_id}/access`,
        {
          application,
          enabled: !currentEnabled,
        }
      );

      // Reload latest state from backend
      await fetchUser();

    } catch (err) {
      console.error(
        "Failed to update application access:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Failed to update application access."
      );
    } finally {
      setUpdating(null);
    }
  };

  // --------------------------------------------------
  // Loading
  // --------------------------------------------------

  if (loading) {
    return (
      <div className="admin-page">
        <div className="admin-loading">
          Loading access settings...
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // Error before user loaded
  // --------------------------------------------------

  if (error && !user) {
    return (
      <div className="admin-page">

        <button
          type="button"
          className="admin-back-button"
          onClick={() =>
            navigate(
              `/admin/users/${user_id}`
            )
          }
        >
          ← Back to User
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
          navigate(
            `/admin/users/${user.id}`
          )
        }
      >
        ← Back to User
      </button>

      {/* Header */}
      <div className="admin-header">

        <h1>
          Application Access
        </h1>

        <p>
          Manage application access for{" "}
          <strong>
            {user.name}
          </strong>
        </p>

        <p>
          {user.email}
        </p>

      </div>

      {/* Error */}
      {error && (
        <div className="admin-error">
          {error}
        </div>
      )}

      {/* Access Card */}
      <div className="admin-card">

        <div className="admin-card-header">

          <h2>
            Applications
          </h2>

          <p>
            Enable or disable application access for this user.
          </p>

        </div>

        <div className="admin-access-list">

          {user.applications.map(
            (application) => {

              const isUpdating =
                updating === application.application;

              return (
                <div
                  key={application.application}
                  className="admin-access-row"
                >

                  {/* Application Information */}
                  <div>

                    <div className="admin-access-name">
                      {application.application}
                    </div>

                    <div className="admin-access-status">
                      {application.enabled
                        ? "User has access"
                        : "User does not have access"}
                    </div>

                  </div>

                  {/* Toggle */}
                  <button
                    type="button"
                    disabled={isUpdating}
                    aria-label={`Toggle ${application.application} access`}
                    aria-pressed={application.enabled}
                    onClick={() =>
                      handleToggle(
                        application.application,
                        application.enabled
                      )
                    }
                    className={`admin-toggle ${
                      application.enabled
                        ? "enabled"
                        : "disabled"
                    }`}
                  >

                    <span className="admin-toggle-knob" />

                  </button>

                </div>
              );
            }
          )}

        </div>

      </div>

    </div>
  );
}

export default AccessManagementPage;