"use client";

import { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { chatWithAgent, createFarmProfile } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2, PlusCircle } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([
    { role: "assistant", content: "Hello! I'm AgriGuard AI. You can ask me about crop problems, weather, market prices, or sustainable farming. To get personalised advice, create a farm profile first." },
  ]);
  const [input, setInput] = useState("");
  const [farmProfileId, setFarmProfileId] = useState<number | null>(null);
  const [showCreateProfile, setShowCreateProfile] = useState(false);
  const [newProfile, setNewProfile] = useState({ location: "", crop: "", farm_size_hectares: "", problem: "" });

  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      chatWithAgent({
        username: user?.username || "anonymous",
        farm_profile_id: farmProfileId ?? undefined,
        message,
      }),
    onSuccess: (res) => {
      setMessages((prev) => [
        ...prev,
        { role: "user", content: input },
        { role: "assistant", content: res.data.reply },
      ]);
      setInput("");
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "I could not reach the advisory service. Check that the FastAPI backend is running, then try again." },
      ]);
    },
  });

  const profileMutation = useMutation({
    mutationFn: () =>
      createFarmProfile({
        username: user?.username || "anonymous",
        location: newProfile.location,
        crop: newProfile.crop,
        farm_size_hectares: parseFloat(newProfile.farm_size_hectares),
        problem: newProfile.problem,
      }),
    onSuccess: (res) => {
      setFarmProfileId(res.data.id);
      setShowCreateProfile(false);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Farm profile created! Your ${res.data.crop} farm at ${res.data.location} is now active.` },
      ]);
    },
  });

  const handleSend = () => {
    if (!input.trim()) return;
    chatMutation.mutate(input);
  };

  return (
    <div className="flex flex-col h-[85vh] max-w-3xl mx-auto">
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>AI Chat</CardTitle>
          {!farmProfileId && !showCreateProfile && (
            <Button variant="outline" size="sm" onClick={() => setShowCreateProfile(true)}>
              <PlusCircle className="w-4 h-4 mr-2" />
              Create Farm Profile
            </Button>
          )}
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto space-y-4 p-4">
          {showCreateProfile && (
            <div className="space-y-3 p-4 border rounded-lg">
              <h3 className="font-medium">Create a Farm Profile</h3>
              <Input placeholder="Location (lat,lng)" value={newProfile.location} onChange={(e) => setNewProfile({ ...newProfile, location: e.target.value })} />
              <Input placeholder="Crop (e.g., maize)" value={newProfile.crop} onChange={(e) => setNewProfile({ ...newProfile, crop: e.target.value })} />
              <Input placeholder="Farm size (hectares)" type="number" value={newProfile.farm_size_hectares} onChange={(e) => setNewProfile({ ...newProfile, farm_size_hectares: e.target.value })} />
              <Input placeholder="Problem (optional)" value={newProfile.problem} onChange={(e) => setNewProfile({ ...newProfile, problem: e.target.value })} />
              <div className="flex gap-2">
                <Button onClick={() => profileMutation.mutate()} disabled={profileMutation.isPending}>
                  {profileMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Save"}
                </Button>
                <Button variant="ghost" onClick={() => setShowCreateProfile(false)}>Cancel</Button>
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {chatMutation.isPending && (
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
            placeholder={farmProfileId ? "Ask about your crops..." : "Ask a general farming question..."}
            disabled={chatMutation.isPending}
          />
          <Button onClick={handleSend} disabled={chatMutation.isPending}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </Card>
    </div>
  );
}