"""
Vernacular Translator — Multi-language output using deep-translator.
"""
from __future__ import annotations
import re

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False

# Skills, URLs, and numbers should NOT be translated
SKIP_PATTERNS = [
    r'https?://\S+',                      # URLs
    r'\b\d+\.?\d*\s*(lpa|%|hrs?|weeks?)\b',  # Numbers with units
    r'\b(python|java|sql|docker|react|node\.js|kubernetes|tensorflow|pytorch|'
    r'fastapi|flask|mongodb|postgresql|github|linux|aws|gcp|azure|'
    r'machine learning|deep learning|nlp|mlops|llm|rag|ci/cd|git|redis|kafka|'
    r'numpy|pandas|scikit-learn|hugging face|transformers|bert|gpt)\b',  # Skill names
]


class VernacularTranslator:
    """Translates analysis output to Indian regional languages."""

    SUPPORTED = {
        "Hindi": "hi",
        "Telugu": "te",
        "Tamil": "ta",
        "Kannada": "kn",
        "Bengali": "bn",
    }

    MAX_CHUNK_CHARS = 4500  # GoogleTranslator limit

    def translate(self, text: str, target_lang: str) -> str:
        """
        Translate text to target language, preserving skill names and URLs.

        Args:
            text: Source text (English).
            target_lang: Language name (e.g., "Hindi") or code (e.g., "hi").

        Returns:
            Translated string, or original if translation fails.
        """
        if not HAS_TRANSLATOR:
            return text

        lang_code = self.SUPPORTED.get(target_lang, target_lang)
        if lang_code == "en" or target_lang == "English":
            return text

        try:
            # Protect skip-patterns with placeholders
            protected, placeholders = self._protect_patterns(text)

            # Chunk and translate
            chunks = self._split_into_chunks(protected)
            translated_chunks = []
            translator = GoogleTranslator(source="en", target=lang_code)
            for chunk in chunks:
                try:
                    translated_chunks.append(translator.translate(chunk) or chunk)
                except Exception:
                    translated_chunks.append(chunk)

            translated = " ".join(translated_chunks)

            # Restore placeholders
            result = self._restore_placeholders(translated, placeholders)
            return result

        except Exception:
            return text  # Silent fallback to English

    def translate_report(self, analysis: dict, lang: str) -> dict:
        """
        Translate human-readable strings in analysis dict.

        Preserves: skill names, URLs, numbers, keys.
        Translates: feedback strings, gap names display, roadmap text.

        Returns new dict with translated strings.
        """
        if lang == "English" or not HAS_TRANSLATOR:
            return analysis

        translated = dict(analysis)

        # Translate roadmap text
        if "roadmap" in translated and translated["roadmap"]:
            translated["roadmap"] = self.translate(translated["roadmap"], lang)

        # Translate ATS recommendations
        ats = translated.get("ats", {})
        if ats.get("recommendations"):
            ats["recommendations"] = [
                self.translate(r, lang) for r in ats["recommendations"]
            ]
            translated["ats"] = ats

        # Translate section score feedback
        section_scores = translated.get("section_scores", {})
        for section, data in section_scores.items():
            if isinstance(data, dict) and data.get("feedback"):
                section_scores[section]["feedback"] = self.translate(data["feedback"], lang)
        translated["section_scores"] = section_scores

        # Translate company tip
        if translated.get("company_tip"):
            translated["company_tip"] = self.translate(translated["company_tip"], lang)

        return translated

    # ------------------------------------------------------------------

    def _protect_patterns(self, text: str) -> tuple[str, dict]:
        """Replace protected patterns with placeholders."""
        placeholders = {}
        result = text

        combined = re.compile(
            "|".join(SKIP_PATTERNS),
            re.IGNORECASE,
        )

        counter = [0]

        def replacer(m):
            key = f"__PROTECT_{counter[0]}__"
            placeholders[key] = m.group(0)
            counter[0] += 1
            return key

        result = combined.sub(replacer, result)
        return result, placeholders

    @staticmethod
    def _restore_placeholders(text: str, placeholders: dict) -> str:
        for key, value in placeholders.items():
            text = text.replace(key, value)
        return text

    def _split_into_chunks(self, text: str) -> list[str]:
        """Split text at sentence boundaries for long texts."""
        if len(text) <= self.MAX_CHUNK_CHARS:
            return [text]

        sentences = re.split(r'(?<=[.!?\n])\s+', text)
        chunks = []
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= self.MAX_CHUNK_CHARS:
                current += " " + sentence if current else sentence
            else:
                if current:
                    chunks.append(current)
                current = sentence
        if current:
            chunks.append(current)
        return chunks or [text[:self.MAX_CHUNK_CHARS]]
