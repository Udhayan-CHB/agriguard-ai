"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { generateReport } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";

export default function ReportPage() {
  const [farmId, setFarmId] = useState(1);
  const [report, setReport] = useState<any>(null);

  const mutation = useMutation({
    mutationFn: () => generateReport(farmId),
    onSuccess: (res) => setReport(res.data),
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Farm Report</h1>

      <div className="flex gap-4 items-end">
        <div className="space-y-2">
          <label className="text-sm font-medium">Farm Profile ID</label>
          <Input
            type="number"
            value={farmId}
            onChange={(e) => setFarmId(Number(e.target.value))}
            className="w-24"
          />
        </div>
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Generate Report"}
        </Button>
      </div>

      {report && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader><CardTitle>Weather</CardTitle></CardHeader>
            <CardContent><pre className="text-sm whitespace-pre-wrap">{report.weather}</pre></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Crop Health</CardTitle></CardHeader>
            <CardContent><pre className="text-sm whitespace-pre-wrap">{report.diseases}</pre></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Market</CardTitle></CardHeader>
            <CardContent><pre className="text-sm whitespace-pre-wrap">{report.market}</pre></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Sustainability</CardTitle></CardHeader>
            <CardContent><pre className="text-sm whitespace-pre-wrap">{report.sustainability}</pre></CardContent>
          </Card>
        </div>
      )}

      {report?.final_recommendation && (
        <Card>
          <CardHeader><CardTitle>Recommendation</CardTitle></CardHeader>
          <CardContent><p className="text-sm whitespace-pre-wrap">{report.final_recommendation}</p></CardContent>
        </Card>
      )}
    </div>
  );
}