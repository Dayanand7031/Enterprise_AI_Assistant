import Login from "../components/Login";

function LoginPage() {
  const handleLogin = () => {
    window.location.href = "/chat";
  };

  return (
    <div className="login-page">
      <Login onLogin={handleLogin} />
    </div>
  );
}

export default LoginPage;