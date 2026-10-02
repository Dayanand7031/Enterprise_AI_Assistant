import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../services/api";

function UsersPage() {
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/api/admin/users");

      setUsers(response.data);
    } catch (err) {
      console.error("Failed to load users:", err);

      setError(
        err.response?.data?.detail ||
        "Failed to load users."
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
          Loading users...
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
        <div className="admin-error">
          {error}
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // Page
  // --------------------------------------------------

  return (
    <div className="admin-page">

      {/* Header */}
      <div className="admin-header">
        <h1>
          Users
        </h1>

        <p>
          Manage users and their application access.
        </p>
      </div>

      {/* Users Table */}
      <div className="admin-table-wrapper">

        <table className="admin-table">

          <thead>
            <tr>

              <th>
                ID
              </th>

              <th>
                Name
              </th>

              <th>
                Email
              </th>

              <th>
                Role
              </th>

              <th>
                Action
              </th>

            </tr>
          </thead>

          <tbody>

            {users.length === 0 ? (

              <tr>
                <td
                  colSpan="5"
                  style={{
                    textAlign: "center",
                    color: "#9ca3af",
                    padding: "30px",
                  }}
                >
                  No users found.
                </td>
              </tr>

            ) : (

              users.map((user) => (

                <tr key={user.id}>

                  {/* ID */}
                  <td>
                    {user.id}
                  </td>

                  {/* Name */}
                  <td>
                    <strong>
                      {user.name}
                    </strong>
                  </td>

                  {/* Email */}
                  <td>
                    {user.email}
                  </td>

                  {/* Role */}
                  <td>

                    {user.role ? (

                      <span className="admin-role-badge">
                        {user.role}
                      </span>

                    ) : (

                      <span className="admin-no-role">
                        No role
                      </span>

                    )}

                  </td>

                  {/* Action */}
                  <td>

                    <button
                      type="button"
                      className="admin-button"
                      onClick={() =>
                        navigate(
                          `/admin/users/${user.id}`
                        )
                      }
                    >
                      View
                    </button>

                  </td>

                </tr>

              ))

            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default UsersPage;