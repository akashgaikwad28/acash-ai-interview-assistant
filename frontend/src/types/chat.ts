export interface Citation {
  source: string;
  text_snippet: string;
  score: number;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string | null;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  citations: Citation[];
}
