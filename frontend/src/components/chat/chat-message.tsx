"use client";

import { useState, useEffect } from "react";
import { ChatMessage as ChatMessageModel } from "@/types/chat";
import ReactMarkdown from "react-markdown";
import { CitationBadge } from "./citation-badge";
import { cn } from "@/lib/utils";
import { BrainCircuit, User } from "lucide-react";

export function ChatMessage({ message, isLatest }: { message: ChatMessageModel; isLatest?: boolean }) {
  const isAi = message.role === "assistant";
  
  // Typewriter effect state
  const [displayedContent, setDisplayedContent] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    // Only apply typewriter effect to the latest AI message
    if (isAi && isLatest) {
      setIsTyping(true);
      setDisplayedContent("");
      
      let i = 0;
      // Calculate typing speed based on length (max 1.5s total time, but at least 5ms per chunk)
      const chunkSize = Math.max(1, Math.floor(message.content.length / 100));
      const intervalDelay = Math.max(10, Math.min(30, 1500 / (message.content.length / chunkSize)));
      
      const interval = setInterval(() => {
        if (i < message.content.length) {
          const nextChunk = message.content.substring(i, i + chunkSize);
          setDisplayedContent(prev => prev + nextChunk);
          i += chunkSize;
        } else {
          setDisplayedContent(message.content);
          setIsTyping(false);
          clearInterval(interval);
        }
      }, intervalDelay);
      
      return () => clearInterval(interval);
    } else {
      // Instant render for history or non-latest messages
      setDisplayedContent(message.content);
      setIsTyping(false);
    }
  }, [message.content, isAi, isLatest]);

  return (
    <div className={cn("flex gap-4 shrink-0", isAi ? "flex-row" : "flex-row-reverse")}>
      <div className={cn(
        "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
        isAi ? "bg-primary/20 text-primary" : "bg-secondary text-secondary-foreground"
      )}>
        {isAi ? <BrainCircuit className="w-5 h-5" /> : <User className="w-5 h-5" />}
      </div>
      
      <div className={cn(
        "max-w-[85%] prose prose-neutral dark:prose-invert shrink-0 min-w-0",
        isAi ? "prose-p:leading-relaxed text-foreground/90" : "bg-secondary/50 px-4 py-2 rounded-2xl rounded-tr-sm text-foreground"
      )}>
        <ReactMarkdown>
          {displayedContent + (isTyping ? "▋" : "")}
        </ReactMarkdown>
        
        {(!isTyping && message.citations && message.citations.length > 0) && (
          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-border/50 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {message.citations.map((cite, i) => (
              <CitationBadge key={i} citation={cite} index={i + 1} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
