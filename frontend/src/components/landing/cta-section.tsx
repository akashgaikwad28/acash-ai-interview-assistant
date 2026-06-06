"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Calendar, MessageSquare } from "lucide-react";
import Link from "next/link";
import { BookingSheet } from "@/components/scheduling/booking-sheet";

export function CtaSection() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-primary/5" />
      <div className="container relative z-10 mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="bg-background border border-border/50 rounded-3xl p-8 md:p-12 shadow-2xl shadow-primary/5"
        >
          <h2 className="font-heading text-3xl md:text-5xl font-bold mb-6">Ready to Collaborate?</h2>
          <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
            Interact with the AI assistant to learn more about my background, or jump straight into scheduling an interview.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link href="/chat" passHref>
              <Button size="lg" className="w-full sm:w-auto gap-2 text-base h-12 px-8">
                <MessageSquare className="w-5 h-5" />
                Chat with Aiden
              </Button>
            </Link>
            <BookingSheet>
              <Button size="lg" variant="secondary" className="w-full sm:w-auto gap-2 text-base h-12 px-8">
                <Calendar className="w-5 h-5" />
                View Availability
              </Button>
            </BookingSheet>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
