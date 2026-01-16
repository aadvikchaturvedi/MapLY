"use client";

import { motion } from "framer-motion";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";
import { Quote } from "lucide-react";

const testimonials = [
  {
    name: "Priya Sharma",
    role: "Student, Delhi University",
    content: "I used to be terrified of my evening coaching classes. SafeHer showed me a route that's slightly longer but so much better lit and crowded. I feel in control now.",
    image: "https://i.pravatar.cc/150?u=priya"
  },
  {
    name: "Anjali Desai",
    role: "Software Engineer, Bangalore",
    content: "The SOS feature is a lifesaver. Literally. Knowing that my location is shared with my husband and the police instantly gives me huge peace of mind during late shifts.",
    image: "https://i.pravatar.cc/150?u=anjali"
  },
  {
    name: "Meera Reddy",
    role: "Journalist, Hyderabad",
    content: "Contributing to the safety map feels empowering. I reported a broken streetlight on my street, and seeing the safety score update made me feel heard.",
    image: "https://i.pravatar.cc/150?u=meera"
  }
];

export function CommunitySection() {
  return (
    <section id="community" className="py-24 bg-primary text-primary-foreground relative overflow-hidden text-center">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>
      
      <div className="container px-4 md:px-6 relative z-10 mx-auto">
        <div className="mb-16 space-y-4 max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold font-display tracking-tight sm:text-4xl">Trusted by 500,000+ Women</h2>
          <p className="text-primary-foreground/80 text-lg">
            We are building a safety net powered by community trust and real experiences.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 justify-items-center">
          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="w-full max-w-sm"
            >
              <Card className="bg-white/10 border-white/10 backdrop-blur-sm text-primary-foreground text-left h-full">
                <CardContent className="pt-6">
                  <Quote className="h-8 w-8 text-accent mb-4 opacity-50" />
                  <p className="text-lg leading-relaxed mb-6 italic opacity-90">"{t.content}"</p>
                  <div className="flex items-center gap-4">
                    <Avatar className="h-10 w-10 border-2 border-accent">
                      <AvatarImage src={t.image} alt={t.name} />
                      <AvatarFallback className="text-primary bg-white">{t.name[0]}</AvatarFallback>
                    </Avatar>
                    <div>
                      <h4 className="font-semibold font-display">{t.name}</h4>
                      <p className="text-xs opacity-70 uppercase tracking-wider">{t.role}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 text-center border-t border-white/20 pt-12">
          <div>
            <div className="text-4xl font-bold font-display mb-1">24/7</div>
            <div className="text-sm opacity-70">Real-time Monitoring</div>
          </div>
          <div>
            <div className="text-4xl font-bold font-display mb-1">12</div>
            <div className="text-sm opacity-70">Cities Covered</div>
          </div>
          <div>
            <div className="text-4xl font-bold font-display mb-1">15k</div>
            <div className="text-sm opacity-70">Safety Reports/Day</div>
          </div>
          <div>
            <div className="text-4xl font-bold font-display mb-1">4.8</div>
            <div className="text-sm opacity-70">App Store Rating</div>
          </div>
        </div>
      </div>
    </section>
  );
}