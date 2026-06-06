import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { AvailabilityResponse } from '@/types/calendar';

export function useAvailability() {
  return useQuery<AvailabilityResponse, Error>({
    queryKey: ['availability'],
    queryFn: async () => {
      const { data } = await apiClient.get<AvailabilityResponse>('/availability');
      return data;
    },
  });
}
