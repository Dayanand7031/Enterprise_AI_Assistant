import { useEffect, useState } from "react";
import { logout } from "../services/authService";
import {
  getConversations,
  deleteConversation,
} from "../services/conversationService";

function Sidebar({
  activeConversationId,
  onSelectConversation,
  onNewChat,
}) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);



const handleDelete = async (conversationId, event) => {
  event.stopPropagation();

  const confirmed = window.confirm(
    "Are you sure you want to delete this conversation?"
  );

  if (!confirmed) {
    return;
  }

  try {
    await deleteConversation(conversationId);

    setConversations((previous) =>
      previous.filter(
        (conversation) =>
          conversation.id !== conversationId
      )
    );

    if (activeConversationId === conversationId) {
      onNewChat();
    }
  } catch (error) {
    console.error(
      "Failed to delete conversation:",
      error
    );
  }
};

  return (
    <aside className="sidebar">

      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-icon">✦</div>

        <div>
          <div className="brand-name">
            Enterprise AI
          </div>

          <div className="brand-subtitle">
            AI Assistant
          </div>
        </div>
      </div>

      {/* New Chat */}
      <div className="new-chat-wrapper">
        <button
          className="new-chat-button"
          onClick={onNewChat}
        >
          <span className="new-chat-icon">＋</span>
          <span>New conversation</span>
        </button>
      </div>

      {/* Conversation heading */}
      <div className="conversation-heading">
        Conversations
      </div>

      {/* Conversations */}
      <div className="conversation-list">

        {loading && (
          <div className="sidebar-message">
            Loading conversations...
          </div>
        )}

        {!loading && conversations.length === 0 && (
          <div className="sidebar-message">
            No conversations yet
          </div>
        )}

        {conversations.map((conversation) => (
          <div
            key={conversation.id}
            className={`conversation-item ${
              activeConversationId === conversation.id
                ? "active"
                : ""
            }`}
            onClick={() =>
              onSelectConversation(conversation.id)
            }
          >

            <div className="conversation-icon">
              ◌
            </div>

            <div className="conversation-info">

              <span className="conversation-title">
                {conversation.title || "New Conversation"}
              </span>

              <span className="conversation-date">
                {new Date(
                  conversation.updated_at
                ).toLocaleDateString()}
              </span>

            </div>

            <button
              className="delete-button"
              onClick={(event) =>
                handleDelete(conversation.id, event)
              }
              title="Delete conversation"
            >
              ×
            </button>

          </div>
        ))}

      </div>

      {/* Bottom user section */}
      <div className="sidebar-footer">

        <div className="user-avatar">
            U
        </div>

        <div className="user-details">
            <div className="user-name">
            User
            </div>

            <div className="user-status">
            ● Online
            </div>
        </div>

        <button
            className="logout-button"
            onClick={() => {
            logout();
            window.location.href = "/login";
            }}
            title="Logout"
        >
            ↪
        </button>

        </div>

    </aside>
  );
}

export default Sidebar;