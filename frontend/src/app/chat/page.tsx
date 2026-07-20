"use client";

import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { AlertCircle, Bot, Send, Sparkles, UserRound } from "lucide-react";
import { chatWithAgent } from "@/lib/api";
import { getActiveProfile, type FarmProfile } from "@/lib/farm-profile";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type Message = { role: "user" | "assistant"; content: string };

export default function ChatPage() {
  const [profile] = useState<FarmProfile | null>(() => getActiveProfile());
  const [messages, setMessages] = useState<Message[]>([{ role: "assistant", content: "Welcome to AgriGuard. Save a farm profile, then ask about crop health, weather, markets, or sustainable practices." }]);
  const [input, setInput] = useState("");
  const bottom = useRef<HTMLDivElement>(null);
  useEffect(() => bottom.current?.scrollIntoView({ behavior: "smooth" }), [messages]);

  const mutation = useMutation({
    mutationFn: (message: string) => chatWithAgent({ username: profile!.username, farm_profile_id: profile!.id, message }),
    onSuccess: (res) => setMessages((prev) => [...prev, { role: "assistant", content: res.data.reply }]),
    onError: () => setMessages((prev) => [...prev, { role: "assistant", content: "I could not reach the advisory service. Check that the FastAPI backend is running, then try again." }]),
  });

  function send() {
    const message = input.trim();
    if (!message || mutation.isPending || !profile) return;
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    mutation.mutate(message);
  }

  return <div className="mx-auto flex h-[calc(100vh-3rem)] max-w-5xl flex-col gap-4">
    <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm font-medium text-emerald-400">MULTI-AGENT FIELD ADVISOR</p><h1 className="text-3xl font-bold">Farm conversation</h1></div>{profile && <div className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300">{profile.crop} · {profile.location}</div>}</div>
    {!profile && <Card className="border-amber-500/30"><CardContent className="flex items-center gap-3 py-5 text-sm"><AlertCircle className="text-amber-400" />Create and save a valid farm profile first. Recommendations use that profile.</CardContent></Card>}
    <Card className="flex min-h-0 flex-1 flex-col border-white/10 bg-card/70"><CardHeader className="border-b border-border py-4"><CardTitle className="flex items-center gap-2 text-base"><Sparkles className="h-4 w-4 text-emerald-400" />Supervisor routes each question to the right specialists</CardTitle></CardHeader><CardContent className="flex-1 space-y-5 overflow-y-auto p-5">
      {messages.map((message, index) => <div key={index} className={`flex gap-3 ${message.role === "user" ? "justify-end" : ""}`}>{message.role === "assistant" && <div className="mt-1 rounded-full bg-emerald-500/15 p-2"><Bot className="h-4 w-4 text-emerald-400" /></div>}<div className={`max-w-[82%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${message.role === "user" ? "bg-emerald-500 text-slate-950" : "bg-muted/70"}`}>{message.content}</div>{message.role === "user" && <div className="mt-1 rounded-full bg-primary/15 p-2"><UserRound className="h-4 w-4" /></div>}</div>)}
      {mutation.isPending && <div className="flex items-center gap-3 text-sm text-muted-foreground"><Bot className="h-4 w-4 animate-pulse text-emerald-400" />Consulting farm specialists…</div>}<div ref={bottom} />
    </CardContent><div className="border-t border-border p-4"><div className="flex gap-3"><Textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(); } }} placeholder="Ask about yellow leaves, rain risk, market timing…" className="min-h-11 resize-none" disabled={!profile || mutation.isPending} /><Button onClick={send} disabled={!profile || mutation.isPending || !input.trim()} className="h-11 bg-emerald-400 text-slate-950 hover:bg-emerald-300"><Send className="h-4 w-4" /></Button></div><p className="mt-2 text-xs text-muted-foreground">Enter to send · Shift+Enter for a new line</p></div></Card>
  </div>;
}
