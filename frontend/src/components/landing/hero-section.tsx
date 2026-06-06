"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { MessageSquare, Mic } from "lucide-react";
import Link from "next/link";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden pt-24 pb-32">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
      
      <div className="container relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mx-auto max-w-3xl"
        >
          <h1 className="font-heading text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-8">
            Meet Akash's <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-300">
              AI Interview Assistant
            </span>
          </h1>
          <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
            A production-grade AI agent built to answer your questions, explore my portfolio, and schedule interviews autonomously.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/chat" passHref>
              <Button size="lg" className="w-full sm:w-auto gap-2 text-base h-12 px-8">
                <MessageSquare className="w-5 h-5" />
                Start Chat
              </Button>
            </Link>
            <Link href="/voice" passHref>
              <Button size="lg" variant="outline" className="w-full sm:w-auto gap-2 text-base h-12 px-8 border-primary/20 hover:bg-primary/10">
                <Mic className="w-5 h-5" />
                Call Aiden
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
