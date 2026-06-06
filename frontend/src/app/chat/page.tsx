import { ChatLayout } from "@/components/chat/chat-layout";

export default function ChatPage() {
  return (
    <div className="flex-1 flex flex-col w-full h-[calc(100vh-4rem)]">
      <ChatLayout />
    </div>
  );
}
