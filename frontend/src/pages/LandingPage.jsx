import { useNavigate } from "react-router-dom";

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">

      {/* ================= NAVBAR ================= */}

      <nav className="landing-navbar">

        <div
          className="landing-logo"
          onClick={() => navigate("/")}
        >
          <div className="landing-logo-icon">
            ✦
          </div>

          <div>
            <div className="landing-logo-title">
              Enterprise AI
            </div>

            <div className="landing-logo-subtitle">
              Assistant
            </div>
          </div>
        </div>

        <div className="landing-nav-actions">

          <button
            className="nav-login-button"
            onClick={() => navigate("/login")}
          >
            Sign In
          </button>

          <button
            className="nav-signup-button"
            onClick={() => navigate("/signup")}
          >
            Get Started
          </button>

        </div>

      </nav>


      {/* ================= HERO ================= */}

      <section className="landing-hero">

        <div className="hero-badge">
          ✦ AI-powered enterprise workspace
        </div>

        <h1>
          Intelligent AI for
          <span> real workplace tasks.</span>
        </h1>

        <p className="hero-description">
          Enterprise AI Assistant combines company knowledge,
          Retrieval-Augmented Generation, and MCP-based tool
          execution to help employees find information and
          perform real-world tasks.
        </p>

        <div className="hero-actions">

          <button
            className="hero-primary-button"
            onClick={() => navigate("/signup")}
          >
            Get Started
            <span>→</span>
          </button>

          <button
            className="hero-secondary-button"
            onClick={() => navigate("/login")}
          >
            Sign In
          </button>

        </div>


        {/* Architecture preview */}

        <div className="architecture-preview">

          <div className="architecture-node">
            <span>👤</span>
            User
          </div>

          <div className="architecture-line"></div>

          <div className="architecture-node">
            <span>⚡</span>
            AI Orchestrator
          </div>

          <div className="architecture-line"></div>

          <div className="architecture-node-group">

            <div className="architecture-mini-node">
              RAG
            </div>

            <div className="architecture-mini-node">
              MCP
            </div>

            <div className="architecture-mini-node">
              Jira
            </div>

          </div>

        </div>

      </section>


      {/* ================= FEATURES ================= */}

      <section className="landing-section">

        <div className="section-heading">

          <span>
            CURRENT CAPABILITIES
          </span>

          <h2>
            More than a chatbot.
          </h2>

          <p>
            The platform connects AI with enterprise knowledge
            and real operational systems.
          </p>

        </div>


        <div className="feature-grid">

          {/* RAG */}

          <div className="feature-card">

            <div className="feature-number">
              01
            </div>

            <div className="feature-icon">
              📚
            </div>

            <h3>
              Company Knowledge with RAG
            </h3>

            <p>
              Ask questions about internal company policies
              and documents. The assistant retrieves relevant
              information from the organization's knowledge
              base and generates answers grounded in the
              retrieved context.
            </p>

            <div className="feature-tags">
              <span>RAG</span>
              <span>ChromaDB</span>
              <span>Embeddings</span>
            </div>

          </div>


          {/* LOCAL MCP */}

          <div className="feature-card">

            <div className="feature-number">
              02
            </div>

            <div className="feature-icon">
              🔧
            </div>

            <h3>
              MCP Local Tool Integration
            </h3>

            <p>
              Execute ticket operations through MCP-based
              tools connected to a local PostgreSQL-backed
              system. The assistant determines the required
              tool and executes the operation through a
              controlled workflow.
            </p>

            <div className="feature-tags">
              <span>MCP</span>
              <span>PostgreSQL</span>
              <span>Tool Calling</span>
            </div>

          </div>


          {/* JIRA */}

          <div className="feature-card">

            <div className="feature-number">
              03
            </div>

            <div className="feature-icon">
              🎫
            </div>

            <h3>
              Real Jira Cloud MCP
            </h3>

            <p>
              Connect the assistant to a real Jira Cloud
              workspace. Users can retrieve, create, update,
              and list Jira issues through MCP while
              authentication and role-based permissions
              control what actions are allowed.
            </p>

            <div className="feature-tags">
              <span>Jira Cloud</span>
              <span>MCP</span>
              <span>RBAC</span>
            </div>

          </div>

        </div>

      </section>


      {/* ================= PROJECT ================= */}

      <section className="project-section">

        <div className="project-content">

          <div className="section-label">
            THE PROJECT
          </div>

          <h2>
            Connecting LLMs to
            <br />
            real enterprise workflows.
          </h2>

          <p>
            Enterprise AI Assistant is a full-stack AI
            application designed to explore how modern
            LLM systems can move beyond simple question
            answering.
          </p>

          <p>
            The platform combines Retrieval-Augmented
            Generation for company knowledge with MCP-based
            tool execution for operational tasks.
          </p>

          <p>
            A LangGraph workflow orchestrates requests,
            determines the appropriate workflow, executes
            tools or retrieval, and returns the result.
          </p>

        </div>


        <div className="project-stack">

          <div className="stack-item">
            <strong>FastAPI</strong>
            <span>Backend API</span>
          </div>

          <div className="stack-item">
            <strong>LangGraph</strong>
            <span>AI orchestration</span>
          </div>

          <div className="stack-item">
            <strong>RAG</strong>
            <span>Knowledge retrieval</span>
          </div>

          <div className="stack-item">
            <strong>MCP</strong>
            <span>Tool integration</span>
          </div>

          <div className="stack-item">
            <strong>ChromaDB</strong>
            <span>Vector storage</span>
          </div>

          <div className="stack-item">
            <strong>PostgreSQL</strong>
            <span>Application data</span>
          </div>

        </div>

      </section>


      {/* ================= ABOUT ME ================= */}

      <section className="about-section">

        <div className="about-card">

          <div className="about-avatar">
            D
          </div>

          <div className="about-content">

            <div className="section-label">
              ABOUT THE DEVELOPER
            </div>

            <h2>
              Dayanand
            </h2>

            <h3>
              Software Engineer · Python & AI
            </h3>

            <p>
              I am a Software Engineer focused on building
              backend systems, AI-powered applications,
              and intelligent automation using Python.
            </p>

            <p>
              My work spans FastAPI, Django, REST APIs,
              SQL databases, Retrieval-Augmented Generation,
              LLM applications, MCP, LangGraph, and
              enterprise integrations.
            </p>

            <p>
              I enjoy building systems where AI connects
              with real business workflows — not just
              generating text, but retrieving organizational
              knowledge and securely interacting with
              real tools and services.
            </p>

            <div className="tech-stack">

              <span>Python</span>
              <span>FastAPI</span>
              <span>Django</span>
              <span>PostgreSQL</span>
              <span>SQL Server</span>
              <span>Redis</span>
              <span>LangGraph</span>
              <span>RAG</span>
              <span>MCP</span>
              <span>ChromaDB</span>
              <span>LLMs</span>
              <span>React</span>

            </div>

          </div>

        </div>

      </section>


      {/* ================= CTA ================= */}

      <section className="landing-cta">

        <div className="cta-icon">
          ✦
        </div>

        <h2>
          Explore the Enterprise AI Assistant
        </h2>

        <p>
          Create an account and start interacting
          with the system.
        </p>

        <button
          onClick={() => navigate("/signup")}
        >
          Create your account →
        </button>

      </section>


      {/* ================= FOOTER ================= */}

      <footer className="landing-footer">

        <div>
          © {new Date().getFullYear()}
          {" "}
          Enterprise AI Assistant
        </div>

        <div>
          Built with Python · FastAPI · React · AI
        </div>

      </footer>

    </div>
  );
}

export default LandingPage;