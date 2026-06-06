"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Mic, MicOff, PhoneOff, Phone } from "lucide-react";
import Vapi from "@vapi-ai/web";

type CallState = "idle" | "connecting" | "connected";

let vapi: any = null;
if (typeof window !== "undefined") {
  vapi = new Vapi(process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY || "");
}

export function VoiceAgentUI() {
  const [callState, setCallState] = useState<CallState>("idle");
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    vapi.on("call-start", () => {
      setCallState("connected");
    });

    vapi.on("call-end", () => {
      setCallState("idle");
    });

    vapi.on("error", (e: any) => {
      console.error("Vapi Error:", e);
      setCallState("idle");
    });

    return () => {
      vapi.removeAllListeners();
    };
  }, []);

  const handleStartCall = async () => {
    setCallState("connecting");
    const assistantId = process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID;
    if (assistantId) {
      try {
        await vapi.start(assistantId);
      } catch (e) {
        console.error("Failed to start call", e);
        setCallState("idle");
      }
    } else {
      console.error("No Assistant ID configured");
      setCallState("idle");
    }
  };

  const handleEndCall = () => {
    vapi.stop();
  };

  const toggleMute = () => {
    const newMutedState = !isMuted;
    setIsMuted(newMutedState);
    vapi.setMuted(newMutedState);
  };

  return (
    <div className="relative z-10 flex flex-col items-center max-w-md w-full p-8 rounded-3xl bg-background/50 backdrop-blur-xl border border-border/50 shadow-2xl">
      <div className="text-center mb-12">
        <h2 className="font-heading text-3xl font-bold mb-2">Aiden</h2>
        <p className="text-muted-foreground text-sm font-medium h-5">
          {callState === "idle" && "Ready to chat"}
          {callState === "connecting" && "Connecting..."}
          {callState === "connected" && "Listening..."}
        </p>
      </div>

      <div className="relative flex items-center justify-center w-48 h-48 mb-12">
        <AnimatePresence>
          {callState === "connected" && (
            <>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: [0.3, 0.8, 0.3], scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="absolute inset-0 rounded-full bg-primary/20 blur-md"
              />
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: [0.5, 1, 0.5], scale: [1, 1.4, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
                className="absolute inset-4 rounded-full bg-primary/30 blur-sm"
              />
            </>
          )}
        </AnimatePresence>
        
        <div className="relative z-10 w-24 h-24 rounded-full bg-primary flex items-center justify-center shadow-lg shadow-primary/40">
          <Mic className="w-10 h-10 text-primary-foreground" />
        </div>
      </div>

      <div className="flex gap-6 items-center">
        {callState === "idle" ? (
          <Button 
            size="lg" 
            className="w-16 h-16 rounded-full bg-emerald-500 hover:bg-emerald-600 shadow-lg shadow-emerald-500/30"
            onClick={handleStartCall}
          >
            <Phone className="w-6 h-6 text-white" />
          </Button>
        ) : (
          <>
            <Button
              variant="outline"
              size="icon"
              className={`w-14 h-14 rounded-full border-border/50 bg-secondary/50 backdrop-blur-sm ${isMuted ? 'text-destructive border-destructive/50' : 'text-foreground'}`}
              onClick={toggleMute}
            >
              {isMuted ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
            </Button>
            
            <Button 
              size="icon" 
              className="w-16 h-16 rounded-full bg-destructive hover:bg-destructive/90 shadow-lg shadow-destructive/30"
              onClick={handleEndCall}
            >
              <PhoneOff className="w-6 h-6 text-white" />
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
