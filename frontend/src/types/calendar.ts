export interface TimeSlot {
  start: string;
  end: string;
}

export interface AvailabilityResponse {
  timezone: string;
  slots: TimeSlot[];
}

export interface BookingRequest {
  recruiter_name: string;
  recruiter_email: string;
  company: string;
  start_time: string;
  end_time: string;
}

export interface BookingResponse {
  status: string;
  booking_id: string;
  google_meet_link: string;
}
