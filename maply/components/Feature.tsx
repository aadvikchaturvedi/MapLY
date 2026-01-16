"use client";
import { Map, Moon, Phone, Users, Search, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";

const features = [
  {
    icon: Map,
    title: "Safety Heatmap",
    description: "Visual risk zones based on real-time crime data, lighting scores, and user reports. Know before you go.",
    color: "text-blue-500",
    bg: "bg-blue-500/10"
  },
  {
    icon: Search,
    title: "Safe Navigation",
    description: "AI-powered routing that optimizes for safety scores, avoiding poorly lit or isolated areas.",
    color: "text-teal-500",
    bg: "bg-teal-500/10"
  },
  {
    icon: AlertCircle,
    title: "Instant SOS",
    description: "One-tap emergency alert sharing your live location with trusted contacts and nearby authorities.",
    color: "text-red-500",
    bg: "bg-red-500/10"
  },
  {
    icon: Users,
    title: "Community Reporting",
    description: "Anonymously report harassment or unsafe conditions to help protect other women in your city.",
    color: "text-purple-500",
    bg: "bg-purple-500/10"
  },
  {
    icon: Moon,
    title: "Night Mode",
    description: "Specialized low-light routing and 'Walk with Me' digital monitoring for late-night travel.",
    color: "text-indigo-500",
    bg: "bg-indigo-500/10"
  },
  {
    icon: Phone,
    title: "Nearby Help",
    description: "Instantly locate the nearest police stations, women's help desks, and verified safe havens.",
    color: "text-orange-500",
    bg: "bg-orange-500/10"
  }
];

export function Features() {
  return (
    <section id="features" className="relative py-24 overflow-hidden bg-background">
      {/* Sophisticated Grid Background */}
      <div 
        className="absolute inset-0 z-0 opacity-[0.08] dark:opacity-[0.12]"
        style={{
          backgroundImage: `linear-gradient(to right, currentColor 1px, transparent 1px), linear-gradient(to bottom, currentColor 1px, transparent 1px)`,
          backgroundSize: '40px 40px'
        }}
      />
      
      {/* Deep Blue and Indigo Blurs */}
      <div className="absolute top-1/4 -left-20 w-[500px] h-[500px] bg-blue-900/40 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 -right-20 w-[500px] h-[500px] bg-indigo-600/30 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-blue-950/5 pointer-events-none" />

      <div className="container relative z-10 px-4 md:px-6 mx-auto">
        <div className="flex flex-col items-center justify-center space-y-4 text-center mb-16 max-w-3xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-sm text-primary font-semibold border border-primary/20 backdrop-blur-sm"
          >
            Core Features
          </motion.div>
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl font-bold font-display tracking-tight sm:text-4xl md:text-5xl"
          >
            More than just a map. <br />
            <span className="text-primary">A safety ecosystem.</span>
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-muted-foreground md:text-lg max-w-2xl"
          >
            Built with input from over 10,000 women across India, SafeHer addresses real-world safety challenges with intelligent technology.
          </motion.p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 justify-items-center">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="w-full max-w-sm"
            >
              <Card className="h-full border-white/10 dark:border-white/5 bg-white/40 dark:bg-white/5 backdrop-blur-md hover:shadow-2xl transition-all hover:-translate-y-2 hover:border-primary/30 group cursor-pointer overflow-hidden text-center">
                <CardHeader className="flex flex-col items-center">
                  <div className={`w-14 h-14 rounded-2xl ${feature.bg} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-inner`}>
                    <feature.icon className={`h-7 w-7 ${feature.color}`} />
                  </div>
                  <CardTitle className="font-display text-xl tracking-tight">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}