"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { ChatMessage as ChatMessageModel } from "@/types/chat";
import { useChat } from "@/hooks/use-chat";
import { ChatMessage } from "./chat-message";
import { ChatInput } from "./chat-input";
import { SuggestedQuestions } from "./suggested-questions";
import { motion, AnimatePresence } from "framer-motion";
import { apiClient } from "@/lib/api-client";

const SESSION_STORAGE_KEY = "acash_chat_session_id";

export function ChatLayout() {
  const [messages, setMessages] = useState<ChatMessageModel[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  
  const { mutate: sendMessage, isPending } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Restore session and fetch history on mount
  useEffect(() => {
    const savedSession = localStorage.getItem(SESSION_STORAGE_KEY);
    if (savedSession) {
      setSessionId(savedSession);
      apiClient
        .get(`/chat/history/${savedSession}`)
        .then((res) => {
          const history = res.data.messages || [];
          const restored: ChatMessageModel[] = history.map((msg: any) => ({
            role: msg.sender_role === "user" ? "user" : "assistant",
            content: msg.text_content,
            citations: msg.citations_json ? JSON.parse(msg.citations_json) : undefined,
            timestamp: msg.created_at,
          }));
          setMessages(restored);
        })
        .catch(() => {
          // Session might not exist anymore, start fresh
          localStorage.removeItem(SESSION_STORAGE_KEY);
        })
        .finally(() => setIsLoadingHistory(false));
    } else {
      setIsLoadingHistory(false);
    }
  }, []);

  // Persist session ID when it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    }
  }, [sessionId]);

  // Auto-scroll when new messages arrive or when they stream/expand
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isPending]);

  // Handle auto-scroll during progressive rendering (typewriter effect)
  useEffect(() => {
    if (!bottomRef.current?.parentElement) return;
    
    // Auto-scroll if we're already near the bottom
    const container = bottomRef.current.closest('.overflow-y-auto');
    
    const observer = new ResizeObserver(() => {
      if (!container) return;
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 150;
      if (isNearBottom) {
        bottomRef.current?.scrollIntoView({ behavior: "auto" });
      }
    });
    
    observer.observe(bottomRef.current.parentElement);
    return () => observer.disconnect();
  }, []);

  const handleSend = useCallback((text: string) => {
    const userMsg: ChatMessageModel = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    
    sendMessage(
      { message: text, session_id: sessionId },
      {
        onSuccess: (data) => {
          setSessionId(data.session_id);
          const aiMsg: ChatMessageModel = {
            role: "assistant",
            content: data.response,
            citations: data.citations,
          };
          setMessages((prev) => [...prev, aiMsg]);
        },
        onError: () => {
          const errorMsg: ChatMessageModel = {
            role: "assistant",
            content: "Sorry, I encountered an error connecting to my knowledge base. Please try again."
          };
          setMessages((prev) => [...prev, errorMsg]);
        }
      }
    );
  }, [sessionId, sendMessage]);

  const handleNewChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    localStorage.removeItem(SESSION_STORAGE_KEY);
  }, []);

  if (isLoadingHistory) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="flex items-center gap-3 text-muted-foreground">
          <div className="w-2 h-2 rounded-full bg-primary/60 animate-bounce" />
          <div className="w-2 h-2 rounded-full bg-primary/60 animate-bounce [animation-delay:0.2s]" />
          <div className="w-2 h-2 rounded-full bg-primary/60 animate-bounce [animation-delay:0.4s]" />
          <span className="text-sm ml-2">Loading conversation...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex relative w-full max-w-5xl mx-auto overflow-hidden">
      <div className="flex-1 flex flex-col w-full min-h-0">
        {/* New Chat button when there are messages */}
        {messages.length > 0 && (
          <div className="shrink-0 flex justify-end p-2 pr-4 bg-background/80 backdrop-blur-sm z-10 border-b border-border/10">
            <button
              onClick={handleNewChat}
              className="text-xs text-muted-foreground hover:text-primary transition-colors px-3 py-1.5 rounded-lg hover:bg-secondary/50"
            >
              + New Chat
            </button>
          </div>
        )}

        {/* Scrollable messages area */}
        <div className="flex-1 overflow-y-auto scroll-smooth p-4 sm:p-6 min-h-0">
          {messages.length === 0 ? (
            <SuggestedQuestions onSelect={handleSend} />
          ) : (
            <div className="max-w-3xl mx-auto space-y-8 pb-4">
              {messages.map((msg, i) => (
                <ChatMessage 
                  key={i} 
                  message={msg} 
                  isLatest={i === messages.length - 1} 
                />
              ))}
              {isPending && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 shrink-0">
                  <div className="w-8 h-8 rounded-lg bg-primary/20 shrink-0 flex items-center justify-center text-primary">
                    <div className="flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary/60 animate-bounce" />
                      <div className="w-1.5 h-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:0.2s]" />
                      <div className="w-1.5 h-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:0.4s]" />
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-sm text-muted-foreground animate-pulse">Thinking...</span>
                  </div>
                </motion.div>
              )}
              <div ref={bottomRef} className="h-4 shrink-0" />
            </div>
          )}
        </div>
        
        {/* Chat Input area (Fixed at bottom, no overlap) */}
        <div className="shrink-0 w-full p-4 bg-background border-t border-border/10">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSend={handleSend} disabled={isPending} />
          </div>
        </div>
      </div>
    </div>
  );
}
