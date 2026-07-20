"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { createFarmProfile } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

export default function ProfilePage() {
  const [form, setForm] = useState({
    username: "farmer_joe",
    location: "40.7128,-74.0060",
    crop: "maize",
    farm_size_hectares: 2.5,
    problem: "leaves turning yellow",
  });

  const mutation = useMutation({
    mutationFn: (data: typeof form) => createFarmProfile(data),
    onSuccess: (res) => alert(`Profile created! ID: ${res.data.id}`),
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => mutation.mutate(form);

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Farm Profile</h1>
      <Card>
        <CardHeader><CardTitle>Create New Profile</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <Input name="username" value={form.username} onChange={handleChange} placeholder="Username" />
          <Input name="location" value={form.location} onChange={handleChange} placeholder="Location (lat,lng)" />
          <Input name="crop" value={form.crop} onChange={handleChange} placeholder="Crop" />
          <Input name="farm_size_hectares" type="number" value={form.farm_size_hectares} onChange={handleChange} placeholder="Farm size (ha)" />
          <Textarea name="problem" value={form.problem} onChange={handleChange} placeholder="Describe your problem..." />
          <Button onClick={handleSubmit} disabled={mutation.isPending}>
            {mutation.isPending? <Loader2 className="w-4 h-4 animate-spin" /> : "Save Profile"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}