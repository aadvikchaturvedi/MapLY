"use client";

import { Nav } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { BookOpen, Phone, Shield, Users } from "lucide-react";

const resources = [
  { icon: Phone, title: "Emergency Contacts", desc: "Police, ambulance, and women helpline numbers across India." },
  { icon: Shield, title: "Safety Tips", desc: "Personal safety guidelines and best practices for travel." },
  { icon: Users, title: "Support Groups", desc: "Connect with local women safety organizations." },
  { icon: BookOpen, title: "Know Your Rights", desc: "Legal rights and resources for women in India." },
];

export default function ResourcesPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Nav />
      <main className="flex-1 pt-32 pb-20 container max-w-6xl mx-auto px-4">
        <div className="text-center space-y-4 mb-12">
          <h1 className="text-4xl font-bold font-display tracking-tight">Safety Resources</h1>
          <p className="text-muted-foreground text-lg">Information and tools to help you stay safe</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {resources.map((r, i) => (
            <div key={i} className="rounded-2xl border border-white/10 bg-white/40 dark:bg-white/5 backdrop-blur-xl shadow-xl p-6 space-y-4 hover:shadow-2xl transition-all">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <r.icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">{r.title}</h3>
              <p className="text-muted-foreground text-sm">{r.desc}</p>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  );
}
