import api from "./api";

export const getConversations = async () => {
  const response = await api.get("/api/conversations/");
  return response.data;
};

export const getConversation = async (conversationId) => {
  const response = await api.get(
    `/api/conversations/${conversationId}`
  );

  return response.data;
};

export const createConversation = async (title = "New Conversation") => {
  const response = await api.post("/api/conversations/", {
    title,
  });

  return response.data;
};

export const deleteConversation = async (conversationId) => {
  const response = await api.delete(
    `/api/conversations/${conversationId}`
  );

  return response.data;
};