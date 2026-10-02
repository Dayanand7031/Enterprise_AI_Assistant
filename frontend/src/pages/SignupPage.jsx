import Signup from "../components/Signup";

function SignupPage() {
  const handleSignup = () => {
    window.location.href = "/login";
  };

  return (
    <div className="signup-page">
      <Signup onSignup={handleSignup} />
    </div>
  );
}

export default SignupPage;