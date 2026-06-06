"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { BrainCircuit, Mic, MessageSquare, Terminal } from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  const routes = [
    { href: "/chat", label: "Chat", icon: MessageSquare },
    { href: "/projects", label: "Projects", icon: Terminal },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center space-x-2 transition-opacity hover:opacity-80">
          <div className="bg-primary/20 p-1.5 rounded-lg">
            <BrainCircuit className="h-5 w-5 text-primary" />
          </div>
          <span className="font-heading font-bold text-lg hidden sm:inline-block">
            Akash AI
          </span>
        </Link>
        
        <nav className="hidden md:flex items-center gap-6">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-foreground/80",
                pathname === route.href ? "text-foreground" : "text-foreground/60"
              )}
            >
              {route.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-4">
          <Link href="/voice" passHref>
            <Button className="gap-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white hover:opacity-90 hover:scale-105 transition-all shadow-[0_0_20px_rgba(168,85,247,0.4)] animate-pulse hover:animate-none font-bold text-md px-6">
              <Mic className="h-5 w-5" />
              <span className="hidden sm:inline">Call Aiden</span>
              <span className="sm:hidden">Call</span>
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
