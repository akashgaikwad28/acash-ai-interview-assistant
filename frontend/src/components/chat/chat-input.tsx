"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowUp } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText("");
    }
  };

  return (
    <div className="relative w-full shadow-lg shadow-background/20 rounded-3xl border border-border/50 bg-secondary/30 backdrop-blur-md p-2 flex items-end transition-all focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50">
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
        placeholder="Ask anything about my experience or projects..."
        className="min-h-[44px] max-h-48 resize-none border-0 bg-transparent focus-visible:ring-0 px-4 py-3 placeholder:text-muted-foreground/60 overflow-hidden"
        disabled={disabled}
        rows={1}
      />
      <Button
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        size="icon"
        className="shrink-0 rounded-full w-10 h-10 mb-1 mr-1 transition-transform active:scale-95"
      >
        <ArrowUp className="w-5 h-5" />
      </Button>
    </div>
  );
}
