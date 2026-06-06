import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { BookingRequest, BookingResponse } from '@/types/calendar';

export function useSchedule() {
  return useMutation<BookingResponse, Error, BookingRequest>({
    mutationFn: async (payload) => {
      const { data } = await apiClient.post<BookingResponse>('/schedule', payload);
      return data;
    },
  });
}
