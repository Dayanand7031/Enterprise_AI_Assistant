import api from "./api";

export const sendMessage = async (message, conversationId = null) => {
  const response = await api.post("/api/chat/", {
    message,
    conversation_id: conversationId,
  });

  return response.data;
};