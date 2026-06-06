import * as React from "react";
import { ExternalLink, Terminal, Bot, BrainCircuit, Activity, ChevronRight } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const projects = [
  {
    title: "RTI Agent",
    description: "Multi-agent AI platform automating Right To Information filings. Reduces manual filing process from hours down to under 1 minute.",
    tags: ["LangChain", "LangGraph", "FastAPI", "MongoDB", "Groq", "Gemini"],
    icon: <Bot className="h-8 w-8 text-indigo-500" />,
    github: "https://github.com/akashgaikwad28",
    featured: true,
  },
  {
    title: "PratibimbAI",
    description: "Agentic AI content generation platform. Scrapes and transforms web/YouTube data into structured social media content with fallback logic and memory.",
    tags: ["LangGraph", "FastAPI", "OpenAI", "Gemini", "Groq"],
    icon: <BrainCircuit className="h-8 w-8 text-pink-500" />,
    github: "https://github.com/akashgaikwad28",
    featured: false,
  },
  {
    title: "LMS Chatbot",
    description: "Highly accurate RAG-based academic assistant for contextual question answering.",
    tags: ["LangChain", "RAG", "FastAPI", "Vector DB"],
    icon: <Terminal className="h-8 w-8 text-purple-500" />,
    github: "https://github.com/akashgaikwad28",
    featured: false,
  },
  {
    title: "Hospital Management System (HMS) Backend",
    description: "Robust, modular enterprise backend handling Patient, Physician, Pharmacy, and Room Management.",
    tags: ["Spring Boot", "Java", "MySQL", "JWT", "Hibernate"],
    icon: <Activity className="h-8 w-8 text-blue-500" />,
    github: "https://github.com/akashgaikwad28",
    featured: false,
  }
];

export default function ProjectsPage() {
  return (
    <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-12 md:py-20 animate-in fade-in slide-in-from-bottom-8 duration-700">
      <div className="flex flex-col items-center text-center space-y-4 mb-16">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight font-heading">
          Featured <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">Projects</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl">
          A showcase of my work in Artificial Intelligence, Multi-Agent Systems, and enterprise backend engineering.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {projects.map((project, index) => (
          <div 
            key={index} 
            className={`group relative flex flex-col justify-between rounded-2xl border p-8 shadow-sm transition-all hover:shadow-md dark:hover:shadow-primary/5 ${project.featured ? 'border-primary/50 bg-primary/5' : 'bg-card'}`}
          >
            {project.featured && (
              <div className="absolute -top-3 -right-3">
                <span className="inline-flex items-center rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 px-3 py-1 text-xs font-medium text-white shadow-sm">
                  Top Pick
                </span>
              </div>
            )}
            
            <div>
              <div className="mb-4 inline-flex items-center justify-center rounded-lg bg-background p-3 shadow-sm ring-1 ring-border">
                {project.icon}
              </div>
              <h3 className="mb-2 text-2xl font-bold font-heading group-hover:text-primary transition-colors">
                {project.title}
              </h3>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                {project.description}
              </p>
              <div className="flex flex-wrap gap-2 mb-8">
                {project.tags.map((tag) => (
                  <span 
                    key={tag} 
                    className="inline-flex items-center rounded-md bg-secondary px-2.5 py-0.5 text-xs font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            
            <div className="flex items-center gap-4 mt-auto pt-4 border-t border-border/50">
              <Link href={project.github} target="_blank" rel="noreferrer" className="w-full">
                <Button variant="outline" className="w-full gap-2 hover:bg-primary hover:text-primary-foreground transition-all">
                  <svg viewBox="0 0 24 24" className="h-4 w-4 fill-current"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" /></svg>
                  View Repository
                  <ChevronRight className="h-4 w-4 ml-auto" />
                </Button>
              </Link>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-20 text-center">
        <div className="inline-flex flex-col items-center justify-center space-y-4 rounded-2xl bg-muted/50 p-8 border">
          <h3 className="text-xl font-semibold">Want to discuss these projects?</h3>
          <p className="text-muted-foreground mb-4">Aiden is fully trained on all repository code and architectures.</p>
          <Link href="/voice">
            <Button className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg hover:scale-105 transition-all">
              <Bot className="mr-2 h-5 w-5" />
              Ask Aiden About My Code
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
