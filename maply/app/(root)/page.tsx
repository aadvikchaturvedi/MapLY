import { Nav } from "@/components/layout/Navbar";
import { Hero } from "@/components/Hero";
import { Features } from "@/components/Feature";
import { SafetyMap } from "@/components/SafetyMap";
import { CommunitySection } from "@/components/CommunitySection";
import { Footer } from "@/components/layout/Footer";
import { SOSButton } from "@/components/sos/SOSButton";

export default function Home() {
  return (
    <div className="min-h-screen bg-background font-sans text-foreground selection:bg-accent/20">
      <Nav />
      <main>
        <Hero />
        <Features />
        <SafetyMap />
        <CommunitySection />
      </main>
      <Footer />
      <SOSButton />
    </div>
  );
}