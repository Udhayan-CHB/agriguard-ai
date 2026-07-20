"use client";

import { useState, useSyncExternalStore } from "react";
import { useMutation } from "@tanstack/react-query";
import { AlertCircle, CloudSun, FileText, Leaf, Loader2, Stethoscope, TrendingUp } from "lucide-react";
import { generateReport } from "@/lib/api";
import { getActiveProfile, subscribeToActiveProfile, type FarmProfile } from "@/lib/farm-profile";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const sections = [{ key: "weather", title: "Weather outlook", icon: CloudSun }, { key: "diseases", title: "Crop health", icon: Stethoscope }, { key: "market", title: "Market signal", icon: TrendingUp }, { key: "sustainability", title: "Sustainable practice", icon: Leaf }] as const;
type Report = { weather?: string; diseases?: string; market?: string; sustainability?: string; final_recommendation: string };
export default function ReportPage() {
  const profile = useSyncExternalStore(subscribeToActiveProfile, getActiveProfile, () => null) as FarmProfile | null; const [report, setReport] = useState<Report | null>(null);
  const mutation = useMutation({ mutationFn: () => generateReport(profile!.id), onSuccess: (res) => setReport(res.data) });
  return <div className="mx-auto max-w-6xl space-y-6"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-medium text-emerald-400">DECISION BRIEF</p><h1 className="text-3xl font-bold">Farm report</h1><p className="mt-2 text-muted-foreground">Runs Weather, Crop Doctor, Market, and Sustainability agents in one pass.</p></div><Button onClick={() => mutation.mutate()} disabled={!profile || mutation.isPending} className="bg-emerald-400 text-slate-950 hover:bg-emerald-300">{mutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}{mutation.isPending ? "Building report…" : "Generate report"}</Button></div>{profile ? <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-200">Profile: <strong>{profile.crop}</strong> · {profile.location} · {profile.farm_size_hectares} ha</div> : <Card className="border-amber-500/30"><CardContent className="flex gap-3 py-5 text-sm"><AlertCircle className="text-amber-400" />Save a farm profile before generating a report.</CardContent></Card>}{mutation.isError && <p className="text-sm text-rose-400">Report could not be generated. Ensure the backend is running and try again.</p>}{report && <><div className="grid gap-4 md:grid-cols-2">{sections.map(({ key, title, icon: Icon }) => <Card key={key} className="border-white/10"><CardHeader className="flex flex-row items-center gap-3 pb-2"><Icon className="h-5 w-5 text-emerald-400" /><CardTitle className="text-base">{title}</CardTitle></CardHeader><CardContent><p className="whitespace-pre-wrap text-sm leading-6 text-muted-foreground">{report[key]}</p></CardContent></Card>)}</div><Card className="border-emerald-500/30 bg-emerald-500/5"><CardHeader><CardTitle>Recommended next actions</CardTitle></CardHeader><CardContent><p className="whitespace-pre-wrap text-sm leading-7">{report.final_recommendation}</p></CardContent></Card></>}</div>;
}
