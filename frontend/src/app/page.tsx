import { HeroSection } from "@/components/landing/hero-section";
import { SkillsGrid } from "@/components/landing/skills-grid";
import { ProjectsShowcase } from "@/components/landing/projects-showcase";
import { ExperienceTimeline } from "@/components/landing/experience-timeline";
import { HowItWorks } from "@/components/landing/how-it-works";
import { CtaSection } from "@/components/landing/cta-section";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <HeroSection />
      <SkillsGrid />
      <ProjectsShowcase />
      <ExperienceTimeline />
      <HowItWorks />
      <CtaSection />
    </div>
  );
}
