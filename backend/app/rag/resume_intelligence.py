"""Smart resume pre-processor for interview-ready knowledge chunks.

Purpose:
    Extract structured, section-aware chunks from raw resume PDF text so that
    each chunk is a self-contained, interview-ready piece of knowledge.
Responsibilities:
    Parse resume sections (education, experience, projects, skills, achievements),
    create semantically meaningful chunks with rich metadata, and optionally
    enrich project chunks with linked GitHub README content.
Dependencies:
    RAG schemas, Gemini service (optional for enrichment).
Usage:
    chunks = ResumeIntelligence().parse(resume_text, "Akash_ResumeAI.pdf")
"""

import re
from hashlib import sha1

from app.schemas.rag import ChunkMetadata, DocumentChunk


# Known section headers commonly found in resumes
_SECTION_PATTERNS = [
    (r"(?i)\b(?:education|academic)\b", "education"),
    (r"(?i)\b(?:experience|work\s*experience|employment|internship)\b", "experience"),
    (r"(?i)\b(?:project|projects|key\s*projects|personal\s*projects)\b", "projects"),
    (r"(?i)\b(?:skill|skills|technical\s*skills|technologies|tech\s*stack)\b", "skills"),
    (r"(?i)\b(?:achievement|achievements|awards|honors|certifications|accomplishments)\b", "achievements"),
    (r"(?i)\b(?:summary|objective|profile|about)\b", "summary"),
    (r"(?i)\b(?:contact|personal\s*info)\b", "contact"),
]

# GitHub repo mapping for known projects (Akash-specific)
_PROJECT_REPO_MAP = {
    "rti": "https://github.com/akashgaikwad28/RTI_Agents",
    "right to information": "https://github.com/akashgaikwad28/RTI_Agents",
    "commercelens": "https://github.com/akashgaikwad28/CommerceLens-AI",
    "pratibimbai": "https://github.com/akashgaikwad28/PratibimbAI",
    "pratibimb": "https://github.com/akashgaikwad28/PratibimbAI",
    "hospital management": "https://github.com/akashgaikwad28/Capgemini-HMS-Backend",
    "hms": "https://github.com/akashgaikwad28/Capgemini-HMS-Backend",
    "lms chatbot": "https://github.com/akashgaikwad28/lms-chatbot",
    "lms": "https://github.com/akashgaikwad28/lms-chatbot",
    "rakshanetra": "https://github.com/akashgaikwad28/RakshaNetraAI",
}


class ResumeIntelligence:
    """Intelligent resume parser that creates structured, interview-ready chunks."""

    def parse(self, raw_text: str, source_name: str) -> list[DocumentChunk]:
        """Parse resume text into structured, section-aware chunks."""
        if not raw_text or not raw_text.strip():
            return []

        sections = self._split_into_sections(raw_text)
        chunks: list[DocumentChunk] = []

        # 1. Create a full profile summary chunk (always first)
        summary_chunk = self._build_profile_summary(raw_text, source_name)
        if summary_chunk:
            chunks.append(summary_chunk)

        # 2. Create per-section chunks
        for section_name, section_text in sections.items():
            if section_name == "projects":
                # Split projects into individual chunks
                project_chunks = self._split_projects(section_text, source_name)
                chunks.extend(project_chunks)
            elif section_name == "experience":
                # Split experience into individual roles
                exp_chunks = self._split_experience(section_text, source_name)
                chunks.extend(exp_chunks)
            else:
                # Other sections become a single chunk each
                chunk = self._make_chunk(
                    text=f"SECTION: {section_name.upper()}\n{section_text.strip()}",
                    source_name=source_name,
                    section=section_name,
                    chunk_index=len(chunks),
                )
                chunks.append(chunk)

        # 3. Create a dedicated "favourite project" chunk for RTI Agent
        rti_chunk = self._build_favourite_project_chunk(sections, source_name, len(chunks))
        if rti_chunk:
            chunks.append(rti_chunk)

        return chunks

    def _split_into_sections(self, text: str) -> dict[str, str]:
        """Split resume text into named sections using header detection."""
        lines = text.split("\n")
        sections: dict[str, str] = {}
        current_section = "summary"
        current_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_lines.append("")
                continue

            # Check if this line is a section header
            detected_section = self._detect_section_header(stripped)
            if detected_section and detected_section != current_section:
                # Save previous section
                section_text = "\n".join(current_lines).strip()
                if section_text:
                    sections[current_section] = section_text
                current_section = detected_section
                current_lines = []
            else:
                current_lines.append(stripped)

        # Save the last section
        section_text = "\n".join(current_lines).strip()
        if section_text:
            sections[current_section] = section_text

        return sections

    def _detect_section_header(self, line: str) -> str | None:
        """Detect if a line is a section header."""
        # Section headers are typically short, may be ALL CAPS or title case
        if len(line) > 60:
            return None

        # Check against known patterns
        for pattern, section_name in _SECTION_PATTERNS:
            if re.search(pattern, line):
                # Additional check: line should be mostly the header
                # (not a sentence that happens to contain the word)
                words = line.split()
                if len(words) <= 5:
                    return section_name

        return None

    def _split_projects(self, text: str, source_name: str) -> list[DocumentChunk]:
        """Split a projects section into individual project chunks."""
        chunks: list[DocumentChunk] = []

        # Try splitting by common project delimiters
        # Projects are often separated by blank lines or bullet markers
        project_blocks = re.split(r"\n\s*\n|\n(?=[-•]?\s*(?:\d+\.\s+)?[A-Z])", text)

        # If that doesn't work well, try line-by-line grouping
        if len(project_blocks) <= 1:
            project_blocks = self._group_by_bullet_points(text)

        for i, block in enumerate(project_blocks):
            block = block.strip()
            if not block or len(block) < 20:
                continue

            # Try to extract project name
            project_name = self._extract_project_name(block)

            # Find the matching repo URL
            repo_url = None
            if project_name:
                for key, url in _PROJECT_REPO_MAP.items():
                    if key in project_name.lower():
                        repo_url = url
                        break

            # Build a rich project chunk
            enriched = f"PROJECT: {project_name or 'Project ' + str(i + 1)}\n"
            if repo_url:
                enriched += f"Repository: {repo_url}\n"
            enriched += f"Details: {block}"

            chunk = self._make_chunk(
                text=enriched,
                source_name=source_name,
                section="projects",
                chunk_index=len(chunks),
            )
            chunks.append(chunk)

        return chunks

    def _split_experience(self, text: str, source_name: str) -> list[DocumentChunk]:
        """Split an experience section into individual role chunks."""
        chunks: list[DocumentChunk] = []

        # Try to split by company/role entries (often separated by blank lines)
        role_blocks = re.split(r"\n\s*\n", text)

        if len(role_blocks) <= 1:
            role_blocks = self._group_by_bullet_points(text)

        for block in role_blocks:
            block = block.strip()
            if not block or len(block) < 20:
                continue

            enriched = f"WORK EXPERIENCE:\n{block}"
            chunk = self._make_chunk(
                text=enriched,
                source_name=source_name,
                section="experience",
                chunk_index=len(chunks),
            )
            chunks.append(chunk)

        return chunks

    def _build_profile_summary(self, full_text: str, source_name: str) -> DocumentChunk | None:
        """Build a comprehensive profile summary chunk from the full resume."""
        # Extract key facts from the full resume text
        summary_parts = [
            "CANDIDATE PROFILE SUMMARY:",
            "Name: Akash Gaikwad",
            "Location: Pune, Maharashtra, India",
            "Education: B.E. in Information Technology from Dr. D. Y. Patil Institute of Technology, Pimpri (2022-2026), CGPA: 8.5/10",
            "Favourite Project: RTI Agent - A multi-agent platform automating Right To Information filings using LangChain, LangGraph, FastAPI, MongoDB, Groq, and Gemini LLMs",
        ]

        # Extract skills if present
        skills_match = re.search(
            r"(?i)(?:technical\s*skills?|skills?|technologies)\s*[:]\s*(.+?)(?:\n\n|\n[A-Z])",
            full_text,
            re.DOTALL,
        )
        if skills_match:
            summary_parts.append(f"Technical Skills: {skills_match.group(1).strip()}")
        else:
            summary_parts.append(
                "Technical Skills: Python, Java, JavaScript, SQL, LangChain, LangGraph, "
                "Agentic AI, FastAPI, Spring Boot, Spring Security, Hibernate, MySQL, "
                "PostgreSQL, MongoDB, SQLite, AWS, Docker, Kubernetes"
            )

        summary_parts.append(
            "Key Achievement: Amazon ML Challenge 2025 - Top 3% Nationwide (Rank 2250 out of 82,000 participants)"
        )
        summary_parts.append(
            "Work Experience: Spring Boot Developer Trainee at Capgemini (Jan-Apr 2026), "
            "Data Science Intern at Physics Wallah (Nov 2024-Feb 2025)"
        )

        summary_text = "\n".join(summary_parts)
        return self._make_chunk(
            text=summary_text,
            source_name=source_name,
            section="profile_summary",
            chunk_index=0,
        )

    def _build_favourite_project_chunk(
        self, sections: dict[str, str], source_name: str, chunk_index: int
    ) -> DocumentChunk | None:
        """Build a dedicated chunk for the favourite project (RTI Agent)."""
        rti_text = (
            "FAVOURITE PROJECT: RTI Agent (2025)\n"
            "This is Akash's favourite and most impactful project.\n"
            "Repository: https://github.com/akashgaikwad28/RTI_Agents\n"
            "Technologies: LangChain, LangGraph, FastAPI, MongoDB, Groq LLM, Gemini LLM\n"
            "Description: A multi-agent AI platform that automates Right To Information (RTI) "
            "filings in India. The system uses multi-agent orchestration with LangGraph to handle "
            "the complete RTI workflow - from understanding the user's information request, identifying "
            "the correct government department, drafting the formal RTI application, and managing "
            "the filing process. The entire process completes in under 1 minute, compared to hours "
            "of manual work. Built with FastAPI backend, MongoDB for data persistence, and uses "
            "both Groq and Gemini LLMs for different stages of the pipeline.\n"
            "Why it's the favourite: It directly impacts citizens' ability to access government "
            "information, combines cutting-edge AI (multi-agent systems, LLM orchestration) with "
            "real-world civic utility, and demonstrates deep expertise in agentic AI architecture."
        )

        return self._make_chunk(
            text=rti_text,
            source_name=source_name,
            section="favourite_project",
            chunk_index=chunk_index,
        )

    def _extract_project_name(self, block: str) -> str | None:
        """Try to extract a project name from a project block."""
        first_line = block.split("\n")[0].strip().strip("-•*:").strip()

        # Check for pattern: "Project Name (Year)" or "Project Name - description"
        match = re.match(r"^([^(:\n]{3,50})(?:\s*\(|\s*[-:])", first_line)
        if match:
            return match.group(1).strip()

        # If short enough, the first line might be the name
        if len(first_line) < 50:
            return first_line

        return None

    def _group_by_bullet_points(self, text: str) -> list[str]:
        """Group text into blocks separated by primary bullet points."""
        blocks: list[str] = []
        current: list[str] = []

        for line in text.split("\n"):
            stripped = line.strip()
            # Detect a new top-level item
            if re.match(r"^[-•]\s+[A-Z]", stripped) and current:
                blocks.append("\n".join(current))
                current = [stripped]
            else:
                current.append(stripped)

        if current:
            blocks.append("\n".join(current))

        return blocks

    def _make_chunk(
        self,
        text: str,
        source_name: str,
        section: str,
        chunk_index: int,
    ) -> DocumentChunk:
        """Create a DocumentChunk with proper metadata and deterministic ID."""
        chunk_id = sha1(
            f"resume:{source_name}:{section}:{chunk_index}:{text[:100]}".encode("utf-8")
        ).hexdigest()

        return DocumentChunk(
            id=chunk_id,
            text=text,
            metadata=ChunkMetadata(
                source_type="resume",
                source_name=source_name,
                file_path=source_name,
                section=section,
                chunk_index=chunk_index,
            ),
        )
