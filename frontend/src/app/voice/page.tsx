import { VoiceAgentUI } from "@/components/voice/voice-agent-ui";

export default function VoicePage() {
  return (
    <div className="flex-1 flex flex-col w-full h-[calc(100vh-4rem)] items-center justify-center relative overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/20 rounded-full blur-[120px] opacity-50 pointer-events-none" />
      <VoiceAgentUI />
    </div>
  );
}
