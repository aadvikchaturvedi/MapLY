"use client";

import { Nav } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { MessageCircle, Star, TrendingUp } from "lucide-react";

const posts = [
  { author: "Priya S.", area: "Koramangala, Bangalore", text: "Felt very safe walking here even at 10 PM. Well-lit streets and police patrolling visible." },
  { author: "Ananya R.", area: "Connaught Place, Delhi", text: "Busy area with good foot traffic. Security guards at most building entrances." },
  { author: "Meera K.", area: "Hitech City, Hyderabad", text: "Well-maintained roads and CCTV cameras throughout. Recommended for late work commutes." },
];

export default function CommunityPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Nav />
      <main className="flex-1 pt-32 pb-20 container max-w-6xl mx-auto px-4">
        <div className="text-center space-y-4 mb-12">
          <h1 className="text-4xl font-bold font-display tracking-tight">Community Reports</h1>
          <p className="text-muted-foreground text-lg">Real experiences shared by women like you</p>
        </div>
        <div className="grid gap-6">
          {posts.map((post, i) => (
            <div key={i} className="rounded-2xl border border-white/10 bg-white/40 dark:bg-white/5 backdrop-blur-xl shadow-xl p-6 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                    {post.author[0]}
                  </div>
                  <div>
                    <p className="font-bold text-sm">{post.author}</p>
                    <p className="text-xs text-muted-foreground">{post.area}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-yellow-500">
                  <Star className="h-4 w-4 fill-current" />
                  <Star className="h-4 w-4 fill-current" />
                  <Star className="h-4 w-4 fill-current" />
                  <Star className="h-4 w-4 fill-current" />
                  <Star className="h-4 w-4 fill-current" />
                </div>
              </div>
              <p className="text-sm text-muted-foreground">{post.text}</p>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  );
}
