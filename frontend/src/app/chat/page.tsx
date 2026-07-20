"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { chatWithAgent } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2 } from "lucide-react";

export default function ChatPage() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([
    { role: "assistant", content: "Hello! I'm your AgriGuard AI assistant. How can I help your farm today?" },
  ]);
  const [input, setInput] = useState("");

  const mutation = useMutation({
    mutationFn: (message: string) =>
      chatWithAgent({ username: "farmer_joe", farm_profile_id: 1, message }),
    onSuccess: (res) => {
    setMessages((prev) => [...prev, { role: "user", content: input }, { role: "assistant", content: res.data.reply }]);
    setInput("");
    },
  });

  const handleSend = () => {
    if (!input.trim()) return;
    // Optimistic UI
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    mutation.mutate(input);
  };

  return (
    <div className="flex flex-col h-[85vh] max-w-3xl mx-auto">
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader>
          <CardTitle>AI Chat</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto space-y-4 p-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {mutation.isPending && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-4 py-2">
                <Loader2 className="w-4 h-4 animate-spin" />
              </div>
            </div>
          )}
        </CardContent>
        <div className="p-4 border-t border-border flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about your crops..."
            disabled={mutation.isPending}
          />
          <Button onClick={handleSend} disabled={mutation.isPending}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </Card>
    </div>
  );
}