"use client";

import { motion } from "framer-motion";
import { SKILLS } from "@/constants/skills";

export function SkillsGrid() {
  return (
    <section className="py-24 bg-secondary/30 border-y border-border/50">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">Core Technology Stack</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">Tools and frameworks I use to build scalable, production-ready AI systems.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {SKILLS.map((skillGroup, idx) => (
            <motion.div
              key={skillGroup.category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1, duration: 0.5 }}
              className="bg-background rounded-xl p-6 border border-border/50 shadow-sm hover:shadow-primary/5 transition-all duration-300"
            >
              <h3 className="font-heading font-semibold text-lg mb-4 text-foreground/90">{skillGroup.category}</h3>
              <div className="flex flex-wrap gap-2">
                {skillGroup.items.map((item) => (
                  <span
                    key={item}
                    className="px-3 py-1.5 bg-secondary text-secondary-foreground text-sm rounded-md font-medium hover:bg-primary/20 hover:text-primary transition-colors cursor-default"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
