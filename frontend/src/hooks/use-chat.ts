import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ChatRequest, ChatResponse } from '@/types/chat';

export function useChat() {
  return useMutation<ChatResponse, Error, ChatRequest>({
    mutationFn: async (payload) => {
      const { data } = await apiClient.post<ChatResponse>('/chat', payload);
      return data;
    },
  });
}
