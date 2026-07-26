"""
Resume Parser — Extracts and structures text from PDF resumes.
"""
from __future__ import annotations
import re
import io
from typing import Optional
import fitz  # PyMuPDF


class ResumeParser:
    """Parses PDF resumes into structured sections."""

    SECTION_HEADERS = {
        "summary": [
            r"(summary|profile|objective|about me|career objective|professional summary)",
        ],
        "skills": [
            r"(skills|technical skills|core competencies|technologies|tech stack|expertise)",
        ],
        "experience": [
            r"(experience|work experience|employment|professional experience|internship)",
        ],
        "education": [
            r"(education|academic|qualifications|degrees?|university|college)",
        ],
        "projects": [
            r"(projects?|personal projects?|academic projects?|key projects?)",
        ],
        "certifications": [
            r"(certifications?|certificates?|courses?|achievements?|awards?)",
        ],
    }

    def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract raw text from PDF bytes using PyMuPDF."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages_text = []
            for page in doc:
                pages_text.append(page.get_text())
            doc.close()
            return "\n".join(pages_text)
        except Exception as e:
            return ""

    def clean_text(self, text: str) -> str:
        """Clean extracted text: normalise whitespace and special characters."""
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        return text.strip()

    def extract_sections(self, text: str) -> dict:
        """
        Parse resume text into named sections using regex heuristics.

        Returns:
            dict with keys: summary, skills, experience, education, projects, certifications
        """
        sections = {k: "" for k in self.SECTION_HEADERS}
        lines = text.split("\n")
        current_section = "summary"
        section_content: dict[str, list[str]] = {k: [] for k in self.SECTION_HEADERS}

        for line in lines:
            stripped = line.strip()
            matched_section = self._match_section_header(stripped)
            if matched_section:
                current_section = matched_section
            else:
                if current_section in section_content:
                    section_content[current_section].append(stripped)

        for key, content_lines in section_content.items():
            sections[key] = "\n".join(l for l in content_lines if l).strip()

        # Fallback: if summary is empty, use first 3 lines of the whole text
        if not sections["summary"]:
            first_lines = [l.strip() for l in lines[:5] if l.strip()]
            sections["summary"] = " ".join(first_lines[:3])

        return sections

    def _match_section_header(self, line: str) -> Optional[str]:
        """Match a line to a section header. Returns section name or None."""
        lower = line.lower().strip()
        # Remove common formatting characters
        lower = re.sub(r'[:\-_=\*\|]+', '', lower).strip()
        for section, patterns in self.SECTION_HEADERS.items():
            for pattern in patterns:
                if re.fullmatch(pattern, lower):
                    return section
                # Also match if the header is short (≤ 6 words) and contains the pattern
                if len(lower.split()) <= 6 and re.search(pattern, lower):
                    return section
        return None

    def detect_format_issues(self, pdf_bytes: bytes) -> list[str]:
        """
        Detect ATS-unfriendly formatting in the PDF.

        Returns:
            List of issue description strings.
        """
        issues = []
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            for page_num, page in enumerate(doc, 1):
                # Check for images (not ideal for ATS)
                image_list = page.get_images(full=True)
                if image_list:
                    issues.append(
                        f"Page {page_num}: Contains {len(image_list)} image(s) — "
                        "ATS parsers may skip or misread text near images."
                    )

                # Check for tables (blocks with multiple columns)
                blocks = page.get_text("dict")["blocks"]
                multi_col_count = sum(
                    1 for b in blocks
                    if b.get("type") == 0 and len(b.get("lines", [])) > 0
                )

                # Heuristic: detect two-column layout using x-coordinates
                x_positions = []
                for b in blocks:
                    if b.get("type") == 0:
                        x_positions.append(b.get("bbox", [0])[0])

                if x_positions:
                    left_col = sum(1 for x in x_positions if x < 250)
                    right_col = sum(1 for x in x_positions if x >= 250)
                    if left_col > 2 and right_col > 2:
                        issues.append(
                            f"Page {page_num}: Two-column layout detected — "
                            "many ATS systems parse columns incorrectly, scrambling content."
                        )

                # Check for very small font (header/footer)
                for block in blocks:
                    if block.get("type") == 0:
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                if span.get("size", 12) < 8:
                                    issues.append(
                                        f"Page {page_num}: Very small text detected (size {span.get('size'):.0f}pt) — "
                                        "may indicate header/footer text that breaks ATS parsing."
                                    )
                                    break

            # Check if text extraction yields very little (scanned PDF)
            doc2 = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_text = "".join(p.get_text() for p in doc2)
            doc2.close()
            if len(total_text.strip()) < 200:
                issues.append(
                    "Resume appears to be a scanned image — no readable text found. "
                    "ATS systems cannot parse this. Please use a text-based PDF."
                )

            doc.close()
        except Exception:
            issues.append("Could not fully inspect PDF for formatting issues.")

        return list(dict.fromkeys(issues))  # deduplicate
