"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";
import { Brain, Cloud, Bug, TrendingUp, Leaf } from "lucide-react";

const agents = [
  { name: "Supervisor", icon: Brain, color: "text-purple-500", status: "online" },
  { name: "Weather Analyzer", icon: Cloud, color: "text-blue-500", status: "online" },
  { name: "Crop Doctor", icon: Bug, color: "text-green-500", status: "online" },
  { name: "Market Optimizer", icon: TrendingUp, color: "text-yellow-500", status: "online" },
  { name: "Sustainability Advisor", icon: Leaf, color: "text-emerald-500", status: "online" },
];

export default function AgentStatus() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {agents.map((agent, i) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex flex-col items-center gap-2 p-3 rounded-lg bg-muted/50"
            >
              <agent.icon className={`w-8 h-8 ${agent.color}`} />
              <span className="text-sm font-medium text-center">{agent.name}</span>
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                {agent.status}
              </span>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}