"use client";

import { useState } from "react";
import type { AxiosError } from "axios";
import { useMutation } from "@tanstack/react-query";
import { CheckCircle2, MapPin, Save, Sprout } from "lucide-react";
import { createFarmProfile } from "@/lib/api";
import { getActiveProfile, saveActiveProfile, type FarmProfile } from "@/lib/farm-profile";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

type Form = Omit<FarmProfile, "id">;
const initial: Form = { username: "", location: "", crop: "", farm_size_hectares: 1, problem: "" };

export default function ProfilePage() {
  const [form, setForm] = useState<Form>(() => getActiveProfile() || initial);
  const [notice, setNotice] = useState("");
  const mutation = useMutation({
    mutationFn: (data: Form) => createFarmProfile({ ...data, farm_size_hectares: Number(data.farm_size_hectares) }),
    onSuccess: (res) => { const profile = { ...form, ...res.data }; saveActiveProfile(profile); setNotice("Farm profile saved. Future saves update this farm instead of adding a duplicate."); },
    onError: (error: AxiosError<{ detail?: { msg?: string }[] }>) => setNotice(error.response?.data?.detail?.[0]?.msg || "Unable to save. Check every required field."),
  });
  function update(name: keyof Form, value: string) { setForm((current) => ({ ...current, [name]: name === "farm_size_hectares" ? Number(value) : value })); setNotice(""); }
  function submit() { if (!form.username.trim() || !form.location.trim() || !form.crop.trim() || Number(form.farm_size_hectares) <= 0) { setNotice("Name, location, crop, and a farm size above zero are required."); return; } mutation.mutate(form); }

  return <div className="mx-auto max-w-4xl space-y-6"><div><p className="text-sm font-medium text-emerald-400">FARM CONTEXT</p><h1 className="text-3xl font-bold">Your farm profile</h1><p className="mt-2 text-muted-foreground">One saved profile powers the chat and report, so every recommendation stays grounded in your field.</p></div><div className="grid gap-6 lg:grid-cols-[1.35fr_.65fr]"><Card><CardHeader><CardTitle>Farm details</CardTitle><CardDescription>Location may be a town/city or coordinates such as 12.9716,77.5946.</CardDescription></CardHeader><CardContent className="grid gap-4 sm:grid-cols-2"><Input value={form.username} onChange={(e) => update("username", e.target.value)} placeholder="Your name or farmer ID" /><Input value={form.crop} onChange={(e) => update("crop", e.target.value)} placeholder="Primary crop (e.g. maize)" /><Input value={form.location} onChange={(e) => update("location", e.target.value)} placeholder="Farm location" /><Input type="number" min="0.1" step="0.1" value={form.farm_size_hectares} onChange={(e) => update("farm_size_hectares", e.target.value)} placeholder="Farm size (hectares)" /><Textarea className="sm:col-span-2" value={form.problem || ""} onChange={(e) => update("problem", e.target.value)} placeholder="Optional: current crop concern (yellowing leaves, pest damage…)" /><div className="sm:col-span-2 flex flex-wrap items-center gap-3"><Button onClick={submit} disabled={mutation.isPending} className="bg-emerald-400 text-slate-950 hover:bg-emerald-300"><Save className="mr-2 h-4 w-4" />{mutation.isPending ? "Saving…" : "Save farm profile"}</Button>{notice && <p className={`text-sm ${notice.startsWith("Farm") ? "text-emerald-400" : "text-amber-400"}`}>{notice}</p>}</div></CardContent></Card><div className="space-y-4"><Card className="border-emerald-500/20"><CardContent className="space-y-3 pt-6"><Sprout className="h-7 w-7 text-emerald-400" /><h2 className="font-semibold">What AgriGuard uses</h2><p className="text-sm text-muted-foreground">Crop, location, size, and the issue you describe are shared with specialist agents.</p></CardContent></Card><Card><CardContent className="space-y-3 pt-6"><MapPin className="h-6 w-6 text-sky-400" /><p className="text-sm text-muted-foreground">Weather is fetched with Open-Meteo, a free service requiring no key.</p></CardContent></Card>{notice.startsWith("Farm") && <div className="flex gap-2 text-sm text-emerald-400"><CheckCircle2 className="h-4 w-4" />Ready for chat and reports.</div>}</div></div></div>;
}
