"use client";

import { ChatMessage as ChatMessageModel } from "@/types/chat";
import { motion } from "framer-motion";
import { X, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SourcesPanelProps {
  messages: ChatMessageModel[];
  onClose: () => void;
}

export function SourcesPanel({ messages, onClose }: SourcesPanelProps) {
  // Extract all unique citations from the messages
  const allCitations = messages.flatMap(m => m.citations || []);
  const uniqueCitations = Array.from(new Set(allCitations.map(c => c.text_snippet)))
    .map(snippet => allCitations.find(c => c.text_snippet === snippet)!);

  return (
    <motion.div
      initial={{ x: "100%" }}
      animate={{ x: 0 }}
      exit={{ x: "100%" }}
      transition={{ type: "spring", damping: 20, stiffness: 200 }}
      className="absolute right-0 top-0 bottom-0 w-80 bg-background border-l border-border/50 shadow-2xl flex flex-col z-20 hidden md:flex"
    >
      <div className="flex items-center justify-between p-4 border-b border-border/50">
        <h3 className="font-heading font-semibold flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary" />
          Retrieved Context
        </h3>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 rounded-full">
          <X className="w-4 h-4" />
        </Button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {uniqueCitations.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center mt-10">No sources retrieved yet.</p>
        ) : (
          uniqueCitations.map((cite, i) => (
            <div key={i} className="p-3 bg-secondary/30 rounded-xl border border-border/50 text-sm">
              <div className="font-medium text-primary mb-2 flex items-center gap-2">
                <span className="bg-primary/20 text-primary w-5 h-5 flex items-center justify-center rounded text-[10px] font-bold">
                  {i + 1}
                </span>
                <span className="truncate">{cite.source}</span>
              </div>
              <p className="text-muted-foreground leading-relaxed line-clamp-6 text-xs">
                "{cite.text_snippet}"
              </p>
            </div>
          ))
        )}
      </div>
    </motion.div>
  );
}
