"use client";

import { useState } from "react";
import { format } from "date-fns";
import { Calendar as CalendarIcon, Clock, User, Building, Mail } from "lucide-react";
import { useAvailability } from "@/hooks/use-availability";
import { useSchedule } from "@/hooks/use-schedule";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { motion, AnimatePresence } from "framer-motion";

export function BookingSheet({ children }: { children: React.ReactElement }) {
  const [open, setOpen] = useState(false);
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({ name: "", email: "", company: "" });

  const { data: availability, isLoading: isLoadingAvailability } = useAvailability();
  const { mutate: scheduleMeeting, isPending: isScheduling, isSuccess } = useSchedule();

  const handleBook = () => {
    if (!date || !selectedTime || !formData.name || !formData.email) return;
    
    // Create UTC string from date + time
    const startStr = `${format(date, 'yyyy-MM-dd')}T${selectedTime}:00Z`;
    // Add 30 mins for end
    const startDate = new Date(startStr);
    const endDate = new Date(startDate.getTime() + 30 * 60000);

    scheduleMeeting({
      recruiter_name: formData.name,
      recruiter_email: formData.email,
      company: formData.company,
      start_time: startDate.toISOString(),
      end_time: endDate.toISOString()
    });
  };

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger render={children} />
      <SheetContent className="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader className="mb-6">
          <SheetTitle className="font-heading text-2xl">Schedule Interview</SheetTitle>
          <SheetDescription>
            Select an available time slot and provide your details to instantly book a meeting.
          </SheetDescription>
        </SheetHeader>

        <AnimatePresence mode="wait">
          {isSuccess ? (
            <motion.div 
              key="success"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center py-12 text-center"
            >
              <div className="w-16 h-16 bg-emerald-500/20 text-emerald-500 rounded-full flex items-center justify-center mb-6">
                <CalendarIcon className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold font-heading mb-2">Meeting Confirmed!</h3>
              <p className="text-muted-foreground mb-8">
                A Google Meet invitation has been sent to your email.
              </p>
              <Button onClick={() => setOpen(false)} className="w-full">Done</Button>
            </motion.div>
          ) : (
            <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-8">
              
              <div className="space-y-4">
                <h4 className="text-sm font-semibold flex items-center gap-2 text-foreground/80">
                  <CalendarIcon className="w-4 h-4" /> Date & Time
                </h4>
                <div className="bg-secondary/30 rounded-xl p-4 border border-border/50">
                  <Calendar
                    mode="single"
                    selected={date}
                    onSelect={setDate}
                    className="rounded-md mx-auto"
                    disabled={(date) => date < new Date() || date.getDay() === 0 || date.getDay() === 6}
                  />
                </div>
                
                {date && (
                  <div className="grid grid-cols-3 gap-2 mt-4">
                    {/* Mock slots for UI if API fails/loads */}
                    {['10:00', '11:30', '14:00', '15:30', '16:00'].map(time => (
                      <button
                        key={time}
                        onClick={() => setSelectedTime(time)}
                        className={`py-2 px-3 text-sm rounded-lg border transition-all ${selectedTime === time ? 'bg-primary text-primary-foreground border-primary shadow-md' : 'bg-background hover:border-primary/50 text-foreground/80'}`}
                      >
                        {time}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <h4 className="text-sm font-semibold flex items-center gap-2 text-foreground/80">
                  <User className="w-4 h-4" /> Your Details
                </h4>
                <div className="space-y-3">
                  <div className="relative">
                    <User className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input 
                      placeholder="Name" 
                      className="pl-9 bg-secondary/30" 
                      value={formData.name}
                      onChange={e => setFormData({...formData, name: e.target.value})}
                    />
                  </div>
                  <div className="relative">
                    <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input 
                      placeholder="Email" 
                      type="email"
                      className="pl-9 bg-secondary/30" 
                      value={formData.email}
                      onChange={e => setFormData({...formData, email: e.target.value})}
                    />
                  </div>
                  <div className="relative">
                    <Building className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input 
                      placeholder="Company" 
                      className="pl-9 bg-secondary/30" 
                      value={formData.company}
                      onChange={e => setFormData({...formData, company: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <Button 
                onClick={handleBook} 
                disabled={!selectedTime || !formData.name || !formData.email || isScheduling}
                className="w-full h-12 text-base font-semibold"
              >
                {isScheduling ? "Scheduling..." : "Confirm Booking"}
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </SheetContent>
    </Sheet>
  );
}
