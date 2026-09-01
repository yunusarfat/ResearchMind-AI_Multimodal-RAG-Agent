"use client";

import { useParams } from "next/navigation";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { SourcePanel } from "@/components/sources/SourcePanel";
import { useChatSession } from "@/lib/useChatSession";

export default function ChatConversationPage() {
  const params = useParams<{ chatId: string }>();
  const chatId = params.chatId;

  // useChatSession is called exactly ONCE here and its pieces are passed
  // down as props to both ChatWindow and SourcePanel. Calling the hook
  // again inside either child would create a second, independent state
  // instance that never sees this one's live streaming updates.
  const { messages, sources, isStreaming, streamingContent, currentRoute, uploads, sendMessage, uploadFile } =
    useChatSession(chatId);

  return (
    <div className="flex flex-1 overflow-hidden">
      <ChatWindow
        messages={messages}
        isStreaming={isStreaming}
        streamingContent={streamingContent}
        currentRoute={currentRoute}
        uploads={uploads}
        onSend={sendMessage}
        onUploadFile={uploadFile}
      />
      <div className="hidden w-80 shrink-0 lg:block">
        <SourcePanel sources={sources} />
      </div>
    </div>
  );
}
