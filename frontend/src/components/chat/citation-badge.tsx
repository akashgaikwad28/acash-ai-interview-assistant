"use client";

import { Citation } from "@/types/chat";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { FileText, Code2 } from "lucide-react";

export function CitationBadge({ citation, index }: { citation: Citation, index: number }) {
  const isGitHub = citation.source.startsWith("repo:");
  const Icon = isGitHub ? Code2 : FileText;
  const displayName = isGitHub
    ? citation.source.replace("repo:", "").split("/").pop() || citation.source
    : citation.source;

  return (
    <Tooltip>
      <TooltipTrigger>
        <Badge variant="outline" className="cursor-help gap-1.5 hover:bg-secondary transition-colors">
          <span className="text-primary font-mono text-xs">[{index}]</span>
          <Icon className="w-3 h-3 text-muted-foreground" />
          <span className="max-w-[120px] truncate text-xs">{displayName}</span>
        </Badge>
      </TooltipTrigger>
      <TooltipContent className="max-w-sm p-4 bg-popover border-border">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-primary font-medium text-sm">
            <Icon className="w-4 h-4" />
            {citation.source}
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed line-clamp-4">
            &quot;{citation.text_snippet}&quot;
          </p>
          <div className="text-xs text-muted-foreground/70">
            Relevance: {Math.round(citation.score * 100)}%
          </div>
        </div>
      </TooltipContent>
    </Tooltip>
  );
}
