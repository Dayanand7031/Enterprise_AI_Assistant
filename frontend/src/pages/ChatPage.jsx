import { useState } from "react";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";

function ChatPage() {
  const [conversationId, setConversationId] = useState(null);

  const handleNewChat = () => {
    setConversationId(null);
  };

  const handleSelectConversation = (id) => {
    setConversationId(id);
  };

  return (
    <div className="chat-page">

      <Sidebar
        activeConversationId={conversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
      />

      <ChatWindow
        conversationId={conversationId}
        onConversationCreated={setConversationId}
      />

    </div>
  );
}

export default ChatPage;