"use client";

import { Sprout, Cloud, Bug, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import AgentStatus from "@/components/ui/dashboard/agent-status";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Farm Profiles</CardTitle>
            <Sprout className="w-5 h-5 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <p className="text-xs text-muted-foreground">+1 this week</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Weather Alerts</CardTitle>
            <Cloud className="w-5 h-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">Clear skies</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Disease Risks</CardTitle>
            <Bug className="w-5 h-5 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1</div>
            <p className="text-xs text-muted-foreground">Maize leaf spot</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Market Trend</CardTitle>
            <TrendingUp className="w-5 h-5 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+5%</div>
            <p className="text-xs text-muted-foreground">Maize price rising</p>
          </CardContent>
        </Card>
      </div>

      {/* Agent Status */}
      <AgentStatus />
    </div>
  );
}