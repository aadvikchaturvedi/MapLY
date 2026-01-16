"use client";
import { Shield, Heart, MapPin, Phone, Mail, Instagram, Twitter, Linkedin } from "lucide-react";

export function Footer({ variant = "dark" }: { variant?: "dark" | "light" }) {
  const isLight = variant === "light";
  return (
    <footer className={`${isLight ? "bg-white text-black py-32" : "bg-black text-white py-20"} border-t border-black/5 pt-20 pb-10 transition-colors duration-300`}>
      <div className="container px-4 md:px-6">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-4 mb-16">
          <div className="space-y-6">
            <div className={`flex items-center gap-3 font-display font-black text-6xl tracking-tighter ${isLight ? "text-black" : "text-white"} italic`}>
              <Shield className="h-14 w-14 text-primary fill-primary/20" />
              <span>MapLY</span>
            </div>
            <p className={`${isLight ? "text-gray-600" : "text-gray-400"} max-w-xs text-base leading-relaxed`}>
              The next generation of women's safety. Leveraging AI and community intelligence to create a world where every woman can move freely and fearlessly.
            </p>
            <div className="flex gap-4">
              <a href="#" className={`p-2 rounded-full ${isLight ? "bg-black/5 hover:bg-primary/10" : "bg-white/5 hover:bg-primary/20"} transition-colors`}><Twitter className="h-5 w-5" /></a>
              <a href="#" className={`p-2 rounded-full ${isLight ? "bg-black/5 hover:bg-primary/10" : "bg-white/5 hover:bg-primary/20"} transition-colors`}><Instagram className="h-5 w-5" /></a>
              <a href="#" className={`p-2 rounded-full ${isLight ? "bg-black/5 hover:bg-primary/10" : "bg-white/5 hover:bg-primary/20"} transition-colors`}><Linkedin className="h-5 w-5" /></a>
            </div>
          </div>
          
          <div className="space-y-6">
            <h4 className={`text-lg font-bold ${isLight ? "text-black" : "text-white"}`}>Contact Info</h4>
            <ul className={`space-y-4 ${isLight ? "text-gray-600" : "text-gray-400"}`}>
              <li className="flex items-center gap-3"><MapPin className="h-5 w-5 text-primary" /> <span>Hauz Khas, New Delhi, India</span></li>
              <li className="flex items-center gap-3"><Phone className="h-5 w-5 text-primary" /> <span>+91 1800-SAFE-HER</span></li>
              <li className="flex items-center gap-3"><Mail className="h-5 w-5 text-primary" /> <span>support@safeher.in</span></li>
            </ul>
          </div>
          
          <div className="space-y-6">
            <h4 className={`text-lg font-bold ${isLight ? "text-black" : "text-white"}`}>Quick Links</h4>
            <ul className={`space-y-3 ${isLight ? "text-gray-600" : "text-gray-400"}`}>
              <li><a href="#" className="hover:text-primary transition-colors">Safety Heatmap</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Route Planner</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Community Forum</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Safety Methodology</a></li>
            </ul>
          </div>
          
          <div className="space-y-6">
            <h4 className={`text-lg font-bold ${isLight ? "text-black" : "text-white"}`}>Newsletter</h4>
            <p className={`${isLight ? "text-gray-600" : "text-gray-400"} text-sm`}>Join 50,000+ women getting weekly safety updates.</p>
            <div className="flex gap-2">
              <input type="email" placeholder="Email" className={`${isLight ? "bg-black/5 border-black/10" : "bg-white/5 border-white/10"} border rounded-lg px-4 py-2 w-full focus:outline-none focus:border-primary ${isLight ? "text-black" : "text-white"}`} />
              <button className="bg-primary px-4 py-2 rounded-lg font-bold hover:bg-primary/90 transition-all text-white">Join</button>
            </div>
          </div>
        </div>
        
        <div className={`pt-10 border-t ${isLight ? "border-black/5" : "border-white/10"} flex flex-col md:flex-row justify-between items-center gap-6`}>
          <p className={`text-sm ${isLight ? "text-gray-400" : "text-gray-500"} font-medium tracking-wide`}>
            &copy; 2026 SAFE HER TECHNOLOGIES. ALL RIGHTS RESERVED.
          </p>
          <div className={`flex items-center gap-2 text-sm ${isLight ? "text-gray-400" : "text-gray-400"}`}>
            <span>Built with</span>
            <Heart className="h-4 w-4 text-red-500 fill-red-500" />
            <span>for the women of India</span>
          </div>
        </div>
      </div>
    </footer>
  );
}