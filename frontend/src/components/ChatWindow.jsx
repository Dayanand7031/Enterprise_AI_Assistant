import { useEffect, useRef, useState } from "react";
import {
  getConversation,
} from "../services/conversationService";

import {
  sendMessage,
} from "../services/chatService";

function ChatWindow({
  conversationId,
  onConversationCreated,
}) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    const loadConversation = async () => {
      if (!conversationId) {
        setMessages([]);
        return;
      }

      try {
        const conversation =
          await getConversation(conversationId);

        setMessages(conversation.messages);
      } catch (error) {
        console.error(
          "Failed to load conversation:",
          error
        );
      }
    };

    loadConversation();
  }, [conversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleSend = async () => {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    setInput("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
      },
    ]);

    try {
      const response = await sendMessage(
        message,
        conversationId
      );

      if (!conversationId) {
        onConversationCreated(
          response.conversation_id
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: response.answer,
        },
      ]);
    } catch (error) {
      console.error(
        "Failed to send message:",
        error
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <main className="chat-window">

      {/* Header */}
      <header className="chat-header">

        <div>
          <h1>Enterprise AI Assistant</h1>

          <span>
            AI-powered workplace assistant
          </span>
        </div>

        <div className="header-status">
          <span className="status-dot"></span>
          Online
        </div>

      </header>

      {/* Messages */}
      <div className="messages">

        {messages.length === 0 && (
        <div className="empty-chat">

            <div className="empty-chat-icon">
            ✦
            </div>

            <h2>
            Enterprise AI Assistant
            </h2>

            <p>
            Ask about company policies or manage tickets
            through connected MCP tools.
            </p>

            <div className="suggestion-grid">

            {/* Company Policy RAG */}

            <button
                onClick={() =>
                setInput(
                    "What is the company leave policy?"
                )
                }
            >
                <span className="suggestion-icon">
                📄
                </span>

                <span className="suggestion-content">
                <strong>Company Policy</strong>

                <small>
                    Ask about company policies
                </small>
                </span>
            </button>


            {/* Local MCP */}

            <button
                onClick={() =>
                setInput(
                    "Create a ticket titled Login API issue"
                )
                }
            >
                <span className="suggestion-icon">
                🎫
                </span>

                <span className="suggestion-content">
                <strong>Local Tickets</strong>

                <small>
                    Manage PostgreSQL tickets with MCP
                </small>
                </span>
            </button>


            {/* Jira Cloud */}

            <button
                onClick={() =>
                setInput(
                    "Show me Jira Cloud tickets in project KAN"
                )
                }
            >
                <span className="suggestion-icon">
                🔗
                </span>

                <span className="suggestion-content">
                <strong>Jira Cloud</strong>

                <small>
                    Manage Jira issues through MCP
                </small>
                </span>
            </button>


            {/* Capabilities */}

            <button
                onClick={() =>
                setInput(
                    "What can you do?"
                )
                }
            >
                <span className="suggestion-icon">
                ✦
                </span>

                <span className="suggestion-content">
                <strong>Capabilities</strong>

                <small>
                    See available AI capabilities
                </small>
                </span>
            </button>

            </div>

        </div>
        )}

        {messages.map((message, index) => (
          <div
            key={message.id || index}
            className={`message-row ${
              message.role === "user"
                ? "user-row"
                : "assistant-row"
            }`}
          >

            {message.role === "assistant" && (
              <div className="assistant-avatar">
                ✦
              </div>
            )}

            <div
              className={`message ${
                message.role === "user"
                  ? "user-message"
                  : "assistant-message"
              }`}
            >
              <div className="message-content">
                {message.content}
              </div>
            </div>

            {message.role === "user" && (
              <div className="user-message-avatar">
                U
              </div>
            )}

          </div>
        ))}

        {loading && (
          <div className="message-row assistant-row">

            <div className="assistant-avatar">
              ✦
            </div>

            <div className="assistant-message typing-message">
              <span></span>
              <span></span>
              <span></span>
            </div>

          </div>
        )}

        <div ref={messagesEndRef} />

      </div>

      {/* Input */}
      <div className="chat-input-wrapper">

        <div className="chat-input-box">

          <textarea
            value={input}
            onChange={(e) =>
              setInput(e.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Message Enterprise AI Assistant..."
            rows={1}
          />

          <button
            className="send-button"
            onClick={handleSend}
            disabled={loading || !input.trim()}
            title="Send message"
          >
            ↑
          </button>

        </div>

        <div className="input-hint">
          Press Enter to send · Shift + Enter for new line
        </div>

      </div>

    </main>
  );
}

export default ChatWindow;