import { useNavigate } from "react-router-dom";

function AdminDashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-full bg-gray-50 p-8">

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">
          Admin Dashboard
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Manage users, application access, roles, and system administration.
        </p>
      </div>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">

        {/* Users */}
        <button
          onClick={() => navigate("/admin/users")}
          className="rounded-xl border bg-white p-6 text-left transition hover:-translate-y-0.5 hover:shadow-md"
        >
          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-lg">👥</span>
          </div>

          <h2 className="text-lg font-semibold text-gray-900">
            Users
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            View users and manage their application access.
          </p>

          <div className="mt-4 text-sm font-medium text-gray-900">
            Manage Users →
          </div>
        </button>

        {/* Application Access */}
        <button
          onClick={() => navigate("/admin/users")}
          className="rounded-xl border bg-white p-6 text-left transition hover:-translate-y-0.5 hover:shadow-md"
        >
          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-lg">🔐</span>
          </div>

          <h2 className="text-lg font-semibold text-gray-900">
            Application Access
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Grant or revoke LOCAL_MCP, JIRA_CLOUD, and RAG access.
          </p>

          <div className="mt-4 text-sm font-medium text-gray-900">
            Manage Access →
          </div>
        </button>

        {/* Roles */}
        <button
          onClick={() => navigate("/admin/roles")}
          className="rounded-xl border bg-white p-6 text-left transition hover:-translate-y-0.5 hover:shadow-md"
        >
          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-lg">🛡️</span>
          </div>

          <h2 className="text-lg font-semibold text-gray-900">
            Roles & Permissions
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Manage roles and their permissions.
          </p>

          <div className="mt-4 text-sm font-medium text-gray-900">
            Manage Roles →
          </div>
        </button>

        {/* Audit Logs */}
        <button
          onClick={() => navigate("/admin/audit-logs")}
          className="rounded-xl border bg-white p-6 text-left transition hover:-translate-y-0.5 hover:shadow-md"
        >
          <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-lg">📋</span>
          </div>

          <h2 className="text-lg font-semibold text-gray-900">
            Audit Logs
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Review administrative and MCP activity.
          </p>

          <div className="mt-4 text-sm font-medium text-gray-900">
            View Logs →
          </div>
        </button>

      </div>

      {/* Current Architecture */}
      <div className="mt-10 rounded-xl border bg-white p-6">

        <h2 className="text-lg font-semibold text-gray-900">
          Application Access
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Application access is separate from role permissions.
        </p>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">

          <div className="rounded-lg border p-4">
            <p className="font-medium">
              LOCAL_MCP
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Local MCP tools and ticket operations.
            </p>
          </div>

          <div className="rounded-lg border p-4">
            <p className="font-medium">
              JIRA_CLOUD
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Jira Cloud integration and issue operations.
            </p>
          </div>

          <div className="rounded-lg border p-4">
            <p className="font-medium">
              RAG
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Company document retrieval and knowledge access.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}

export default AdminDashboard;