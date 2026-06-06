"use client";

import { motion } from "framer-motion";

export function SuggestedQuestions({ onSelect }: { onSelect: (q: string) => void }) {
  const questions = [
    "Tell me about the Right To Information (RTI) agent you built.",
    "What technologies did you use for the AI Interview Assistant?",
    "Explain your experience with LangGraph and RAG pipelines.",
    "Walk me through your backend architecture for the SaaS platforms.",
  ];

  return (
    <div className="h-full flex flex-col items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h2 className="text-2xl font-heading font-semibold mb-2">Chat with Akash</h2>
        <p className="text-muted-foreground">Ask me anything about my experience, projects, or technical skills.</p>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl">
        {questions.map((q, i) => (
          <motion.button
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            onClick={() => onSelect(q)}
            className="text-left p-4 rounded-xl border border-border/50 bg-secondary/20 hover:bg-secondary/60 transition-colors group"
          >
            <p className="text-sm font-medium text-foreground/80 group-hover:text-primary transition-colors line-clamp-2">
              "{q}"
            </p>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
