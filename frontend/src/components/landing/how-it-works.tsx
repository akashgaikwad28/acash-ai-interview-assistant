"use client";

import { motion } from "framer-motion";
import { MessageSquare, CalendarCheck, PhoneCall } from "lucide-react";

export function HowItWorks() {
  const steps = [
    {
      icon: MessageSquare,
      title: "1. Chat & Query",
      description: "Ask technical or behavioral questions to explore my skills. The agent retrieves exact context using RAG."
    },
    {
      icon: PhoneCall,
      title: "2. Voice Interaction",
      description: "Prefer a conversation? Call Aiden directly through the browser for a real-time voice screening."
    },
    {
      icon: CalendarCheck,
      title: "3. Schedule Interview",
      description: "Find an open slot in my calendar and book it instantly. You'll receive a Google Meet invite."
    }
  ];

  return (
    <section className="py-24">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">Experience a fully automated, interactive portfolio review process.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, idx) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.2, duration: 0.5 }}
              className="flex flex-col items-center text-center p-6"
            >
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 text-primary">
                <step.icon className="w-8 h-8" />
              </div>
              <h3 className="font-heading font-semibold text-xl mb-3">{step.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
