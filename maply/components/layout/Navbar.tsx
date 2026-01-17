"use client";
import  Link  from "next/link";
import { Shield, Menu, ArrowRight, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
export function Nav() {
  const [isOpen, setIsOpen] = useState(false);

  const links = [
    { href: "#features", label: "Features" },
    { href: "#map", label: "Live Map" },
    { href: "#community", label: "Community" },
    { href: "#resources", label: "Resources" },
  ];

  return (
    <div className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none">
      <motion.nav 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="flex h-16 w-full max-w-5xl items-center justify-between rounded-2xl border border-white/40 bg-white/40 px-6 shadow-2xl backdrop-blur-2xl ring-1 ring-white/20 pointer-events-auto"
      >
        <Link href="/" className="flex items-center gap-2 font-display font-bold text-xl text-primary hover:opacity-80 transition-opacity">
          <motion.div 
            whileHover={{ rotate: 10, scale: 1.1 }}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-lg"
          >
            <Image src="/logo.png" alt="MapLY Logo" width={40} height={70} />
          </motion.div>
          <span className="tracking-tight">MapLY</span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-8">
          {links.map((link) => (
            <motion.a 
              key={link.href} 
              href={link.href}
              whileHover={{ y: -2 }}
              className="text-sm font-semibold text-muted-foreground hover:text-primary transition-colors"
            >
              {link.label}
            </motion.a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-4 mr-2">
            <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
              <Button variant="ghost" size="icon" className="rounded-xl text-muted-foreground hover:text-primary hover:bg-white/20 transition-all relative">
                <Bell className="h-5 w-5" />
                <span className="absolute top-2 right-2 flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                </span>
              </Button>
            </motion.div>
          </div>
          
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button variant="default" className="hidden sm:flex rounded-xl bg-primary/90 px-6 py-5 text-sm font-bold text-primary-foreground hover:bg-primary shadow-lg gap-2 border border-white/20 backdrop-blur-sm transition-all">
              Download <ArrowRight className="h-4 w-4" />
            </Button>
          </motion.div>

          {/* Mobile Nav Trigger */}
          <div className="md:hidden flex items-center">
            <Sheet open={isOpen} onOpenChange={setIsOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-xl">
                  <Menu className="h-5 w-5" />
                  <span className="sr-only">Toggle menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="rounded-l-3xl border-none">
                <div className="flex flex-col gap-6 pt-10">
                  <Link href="/" className="flex items-center gap-2 font-display font-bold text-xl" onClick={() => setIsOpen(false)}>
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                      <Shield className="h-6 w-6" />
                    </div>
                    <span>SafeHer</span>
                  </Link>
                  <div className="flex flex-col gap-4">
                    {links.map((link) => (
                      <a 
                        key={link.href} 
                        href={link.href}
                        className="text-lg font-bold text-foreground hover:text-primary transition-colors"
                        onClick={() => setIsOpen(false)}
                      >
                        {link.label}
                      </a>
                    ))}
                    <Button className="w-full mt-4 rounded-xl py-6 font-bold">Download App</Button>
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </motion.nav>
    </div>
  );
}