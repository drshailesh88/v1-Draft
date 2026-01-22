"""
Citation Generator API
Implements DOI auto-fetch, 20+ citation styles, batch generation, and export formats.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import httpx
import re
from datetime import datetime
from core.database import supabase

router = APIRouter()

# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class CitationStyle(str, Enum):
    """Supported citation styles - 20+ styles using CSL approach"""
    APA = "apa"
    APA_7TH = "apa-7th"
    MLA = "mla"
    MLA_9TH = "mla-9th"
    CHICAGO_AUTHOR_DATE = "chicago-author-date"
    CHICAGO_NOTES = "chicago-notes"
    HARVARD = "harvard"
    IEEE = "ieee"
    VANCOUVER = "vancouver"
    AMA = "ama"
    ACS = "acs"
    NATURE = "nature"
    SCIENCE = "science"
    CELL = "cell"
    PLOS = "plos"
    ELSEVIER_HARVARD = "elsevier-harvard"
    SPRINGER_BASIC = "springer-basic"
    TAYLOR_FRANCIS = "taylor-francis"
    BMJ = "bmj"
    LANCET = "lancet"
    JAMA = "jama"
    OSCOLA = "oscola"
    BLUEBOOK = "bluebook"
    TURABIAN = "turabian"


class ExportFormat(str, Enum):
    """Supported export formats"""
    BIBTEX = "bibtex"
    RIS = "ris"
    ENDNOTE = "endnote"
    PLAIN_TEXT = "plain"
    JSON = "json"
    CSL_JSON = "csl-json"


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class Author(BaseModel):
    """Author model with structured name components"""
    given: Optional[str] = ""
    family: Optional[str] = ""
    literal: Optional[str] = None  # For organizations or single-name authors

    def format_full(self) -> str:
        if self.literal:
            return self.literal
        return f"{self.given} {self.family}".strip()

    def format_family_first(self) -> str:
        if self.literal:
            return self.literal
        if self.given and self.family:
            return f"{self.family}, {self.given}"
        return self.family or self.given or ""

    def format_initials(self) -> str:
        if self.literal:
            return self.literal
        initials = "".join([n[0] + "." for n in (self.given or "").split() if n])
        return f"{self.family} {initials}".strip()


class CitationMetadata(BaseModel):
    """Complete metadata for a citation"""
    title: str
    authors: List[Union[Author, str]] = []
    year: Optional[str] = ""
    month: Optional[str] = ""
    day: Optional[str] = ""
    journal: Optional[str] = ""
    volume: Optional[str] = ""
    issue: Optional[str] = ""
    pages: Optional[str] = ""
    doi: Optional[str] = ""
    url: Optional[str] = ""
    publisher: Optional[str] = ""
    isbn: Optional[str] = ""
    issn: Optional[str] = ""
    abstract: Optional[str] = ""
    keywords: List[str] = []
    type: Optional[str] = "article"  # article, book, chapter, conference, etc.
    container_title: Optional[str] = ""  # For book chapters, conference proceedings
    edition: Optional[str] = ""
    editor: List[Union[Author, str]] = []
    place: Optional[str] = ""  # Publication location
    accessed_date: Optional[str] = ""
    language: Optional[str] = "en"

    def get_authors(self) -> List[Author]:
        """Convert mixed author list to Author objects"""
        result = []
        for author in self.authors:
            if isinstance(author, str):
                parts = author.split()
                if len(parts) >= 2:
                    result.append(Author(given=" ".join(parts[:-1]), family=parts[-1]))
                else:
                    result.append(Author(literal=author))
            else:
                result.append(author)
        return result


class DOILookupRequest(BaseModel):
    """Request for DOI lookup"""
    doi: str


class CitationRequest(BaseModel):
    """Request to generate a citation"""
    metadata: CitationMetadata
    style: CitationStyle = CitationStyle.APA


class BatchCitationRequest(BaseModel):
    """Request for batch citation generation"""
    items: List[CitationMetadata]
    style: CitationStyle = CitationStyle.APA


class BatchDOIRequest(BaseModel):
    """Request for batch DOI lookup"""
    dois: List[str]


class SaveCitationRequest(BaseModel):
    """Request to save a citation"""
    metadata: CitationMetadata
    style: CitationStyle = CitationStyle.APA
    formatted: Optional[str] = None
    project_id: Optional[str] = None
    tags: List[str] = []


class BibliographyRequest(BaseModel):
    """Request to generate a bibliography"""
    citation_ids: List[str]
    style: CitationStyle = CitationStyle.APA
    sort_by: str = "author"  # author, year, title


class ExportRequest(BaseModel):
    """Request to export citations"""
    citation_ids: List[str]
    format: ExportFormat = ExportFormat.BIBTEX


class CitationResponse(BaseModel):
    """Response with formatted citation"""
    formatted: str
    style: str
    metadata: Dict[str, Any]


class BatchCitationResponse(BaseModel):
    """Response for batch citation generation"""
    citations: List[CitationResponse]
    count: int


class SavedCitation(BaseModel):
    """A citation saved in the database"""
    id: str
    metadata: Dict[str, Any]
    style: str
    formatted: str
    created_at: str
    tags: List[str] = []
    project_id: Optional[str] = None


# =============================================================================
# CITATION STYLE LANGUAGE (CSL) IMPLEMENTATION
# =============================================================================

class CitationFormatter:
    """
    Citation Style Language formatter.
    Implements 20+ citation styles with proper formatting rules.
    """

    @staticmethod
    def format(metadata: CitationMetadata, style: CitationStyle) -> str:
        """Format citation according to specified style"""
        formatters = {
            CitationStyle.APA: CitationFormatter._format_apa,
            CitationStyle.APA_7TH: CitationFormatter._format_apa_7th,
            CitationStyle.MLA: CitationFormatter._format_mla,
            CitationStyle.MLA_9TH: CitationFormatter._format_mla_9th,
            CitationStyle.CHICAGO_AUTHOR_DATE: CitationFormatter._format_chicago_author_date,
            CitationStyle.CHICAGO_NOTES: CitationFormatter._format_chicago_notes,
            CitationStyle.HARVARD: CitationFormatter._format_harvard,
            CitationStyle.IEEE: CitationFormatter._format_ieee,
            CitationStyle.VANCOUVER: CitationFormatter._format_vancouver,
            CitationStyle.AMA: CitationFormatter._format_ama,
            CitationStyle.ACS: CitationFormatter._format_acs,
            CitationStyle.NATURE: CitationFormatter._format_nature,
            CitationStyle.SCIENCE: CitationFormatter._format_science,
            CitationStyle.CELL: CitationFormatter._format_cell,
            CitationStyle.PLOS: CitationFormatter._format_plos,
            CitationStyle.ELSEVIER_HARVARD: CitationFormatter._format_elsevier_harvard,
            CitationStyle.SPRINGER_BASIC: CitationFormatter._format_springer,
            CitationStyle.TAYLOR_FRANCIS: CitationFormatter._format_taylor_francis,
            CitationStyle.BMJ: CitationFormatter._format_bmj,
            CitationStyle.LANCET: CitationFormatter._format_lancet,
            CitationStyle.JAMA: CitationFormatter._format_jama,
            CitationStyle.OSCOLA: CitationFormatter._format_oscola,
            CitationStyle.BLUEBOOK: CitationFormatter._format_bluebook,
            CitationStyle.TURABIAN: CitationFormatter._format_turabian,
        }

        formatter = formatters.get(style, CitationFormatter._format_apa)
        return formatter(metadata)

    @staticmethod
    def _get_author_string(authors: List[Author], style: str = "apa", max_authors: int = 7) -> str:
        """Format authors according to style rules"""
        if not authors:
            return ""

        if style == "apa":
            if len(authors) == 1:
                return authors[0].format_family_first()
            elif len(authors) == 2:
                return f"{authors[0].format_family_first()}, & {authors[1].format_family_first()}"
            elif len(authors) <= max_authors:
                parts = [a.format_family_first() for a in authors[:-1]]
                return ", ".join(parts) + f", & {authors[-1].format_family_first()}"
            else:
                parts = [a.format_family_first() for a in authors[:6]]
                return ", ".join(parts) + ", ... " + authors[-1].format_family_first()

        elif style == "mla":
            if len(authors) == 1:
                return authors[0].format_family_first()
            elif len(authors) == 2:
                return f"{authors[0].format_family_first()}, and {authors[1].format_full()}"
            else:
                return f"{authors[0].format_family_first()}, et al."

        elif style == "chicago":
            if len(authors) == 1:
                return authors[0].format_family_first()
            elif len(authors) <= 3:
                parts = [a.format_family_first() if i == 0 else a.format_full()
                        for i, a in enumerate(authors[:-1])]
                return ", ".join(parts) + f", and {authors[-1].format_full()}"
            else:
                return f"{authors[0].format_family_first()}, et al."

        elif style == "vancouver":
            names = []
            for a in authors[:6]:
                names.append(a.format_initials())
            result = ", ".join(names)
            if len(authors) > 6:
                result += ", et al"
            return result

        elif style == "nature":
            names = [a.format_initials() for a in authors[:5]]
            if len(authors) > 5:
                return ", ".join(names) + " et al."
            return ", ".join(names[:-1]) + " & " + names[-1] if len(names) > 1 else names[0]

        elif style == "ieee":
            names = []
            for a in authors[:6]:
                initials = "".join([n[0] + ". " for n in (a.given or "").split() if n])
                names.append(f"{initials}{a.family}")
            if len(authors) > 6:
                return ", ".join(names) + ", et al."
            elif len(names) > 1:
                return ", ".join(names[:-1]) + ", and " + names[-1]
            return names[0] if names else ""

        else:
            # Default
            return ", ".join([a.format_family_first() for a in authors[:3]]) + \
                   (", et al." if len(authors) > 3 else "")

    @staticmethod
    def _format_apa(m: CitationMetadata) -> str:
        """APA 6th Edition format"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "apa")

        parts = [author_str]
        if m.year:
            parts.append(f"({m.year}).")
        parts.append(f"{m.title}.")

        if m.journal:
            journal_part = f"<i>{m.journal}</i>"
            if m.volume:
                journal_part += f", <i>{m.volume}</i>"
            if m.issue:
                journal_part += f"({m.issue})"
            if m.pages:
                journal_part += f", {m.pages}"
            parts.append(journal_part + ".")

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_apa_7th(m: CitationMetadata) -> str:
        """APA 7th Edition format"""
        authors = m.get_authors()

        # APA 7th shows up to 20 authors
        if len(authors) <= 20:
            author_str = CitationFormatter._get_author_string(authors, "apa", max_authors=20)
        else:
            names = [a.format_family_first() for a in authors[:19]]
            author_str = ", ".join(names) + ", ... " + authors[-1].format_family_first()

        parts = [author_str]
        if m.year:
            parts.append(f"({m.year}).")
        parts.append(f"{m.title}.")

        if m.journal:
            journal_part = f"<i>{m.journal}</i>"
            if m.volume:
                journal_part += f", <i>{m.volume}</i>"
            if m.issue:
                journal_part += f"({m.issue})"
            if m.pages:
                journal_part += f", {m.pages}"
            parts.append(journal_part + ".")

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_mla(m: CitationMetadata) -> str:
        """MLA 8th Edition format"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "mla")

        parts = [author_str + "."]
        parts.append(f'"{m.title}."')

        if m.journal:
            parts.append(f"<i>{m.journal}</i>,")
            if m.volume:
                parts.append(f"vol. {m.volume},")
            if m.issue:
                parts.append(f"no. {m.issue},")
            if m.year:
                parts.append(f"{m.year},")
            if m.pages:
                parts.append(f"pp. {m.pages}.")

        if m.doi:
            parts.append(f"doi:{m.doi}.")

        return " ".join(parts)

    @staticmethod
    def _format_mla_9th(m: CitationMetadata) -> str:
        """MLA 9th Edition format"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "mla")

        parts = [author_str + "."]
        parts.append(f'"{m.title}."')

        if m.journal:
            parts.append(f"<i>{m.journal}</i>,")
            if m.volume:
                parts.append(f"vol. {m.volume},")
            if m.issue:
                parts.append(f"no. {m.issue},")
            if m.year:
                parts.append(f"{m.year},")
            if m.pages:
                parts.append(f"pp. {m.pages}.")

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}.")

        return " ".join(parts)

    @staticmethod
    def _format_chicago_author_date(m: CitationMetadata) -> str:
        """Chicago Manual of Style - Author-Date format"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "chicago")

        parts = [author_str + "."]
        if m.year:
            parts.append(f"{m.year}.")
        parts.append(f'"{m.title}."')

        if m.journal:
            parts.append(f"<i>{m.journal}</i>")
            if m.volume:
                parts[-1] += f" {m.volume}"
            if m.issue:
                parts[-1] += f", no. {m.issue}"
            if m.pages:
                parts[-1] += f": {m.pages}"
            parts[-1] += "."

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}.")

        return " ".join(parts)

    @staticmethod
    def _format_chicago_notes(m: CitationMetadata) -> str:
        """Chicago Manual of Style - Notes-Bibliography format"""
        authors = m.get_authors()

        if authors:
            author_names = [a.format_full() for a in authors[:3]]
            if len(authors) > 3:
                author_str = ", ".join(author_names) + ", et al."
            elif len(authors) > 1:
                author_str = ", ".join(author_names[:-1]) + ", and " + author_names[-1]
            else:
                author_str = author_names[0]
        else:
            author_str = ""

        parts = [author_str + ","]
        parts.append(f'"{m.title},"')

        if m.journal:
            parts.append(f"<i>{m.journal}</i>")
            if m.volume:
                parts[-1] += f" {m.volume}"
            if m.issue:
                parts[-1] += f", no. {m.issue}"
            if m.year:
                parts[-1] += f" ({m.year})"
            if m.pages:
                parts[-1] += f": {m.pages}"
            parts[-1] += "."

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}.")

        return " ".join(parts)

    @staticmethod
    def _format_harvard(m: CitationMetadata) -> str:
        """Harvard referencing style"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "apa")

        parts = [author_str]
        if m.year:
            parts.append(f"({m.year})")
        parts.append(f"'{m.title}',")

        if m.journal:
            parts.append(f"<i>{m.journal}</i>,")
            if m.volume:
                parts.append(f"vol. {m.volume},")
            if m.issue:
                parts.append(f"no. {m.issue},")
            if m.pages:
                parts.append(f"pp. {m.pages}.")

        if m.doi:
            parts.append(f"Available at: https://doi.org/{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_ieee(m: CitationMetadata) -> str:
        """IEEE citation style"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "ieee")

        parts = [author_str + ","]
        parts.append(f'"{m.title},"')

        if m.journal:
            parts.append(f"<i>{m.journal}</i>,")
            if m.volume:
                parts.append(f"vol. {m.volume},")
            if m.issue:
                parts.append(f"no. {m.issue},")
            if m.pages:
                parts.append(f"pp. {m.pages},")
            if m.year:
                parts.append(f"{m.year}.")

        if m.doi:
            parts.append(f"doi: {m.doi}.")

        return " ".join(parts)

    @staticmethod
    def _format_vancouver(m: CitationMetadata) -> str:
        """Vancouver citation style (medical/scientific)"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "vancouver")

        parts = [author_str + "."]
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"{m.journal}.")
            if m.year:
                parts.append(f"{m.year};")
            if m.volume:
                parts[-1] = parts[-1].rstrip(";") + f"{m.volume}"
            if m.issue:
                parts[-1] += f"({m.issue})"
            if m.pages:
                parts[-1] += f":{m.pages}."

        if m.doi:
            parts.append(f"doi:{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_ama(m: CitationMetadata) -> str:
        """American Medical Association style"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "vancouver")

        parts = [author_str + "."]
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"<i>{m.journal}</i>.")
            year_vol = ""
            if m.year:
                year_vol = f"{m.year};"
            if m.volume:
                year_vol += m.volume
            if m.issue:
                year_vol += f"({m.issue})"
            if m.pages:
                year_vol += f":{m.pages}"
            if year_vol:
                parts.append(year_vol + ".")

        if m.doi:
            parts.append(f"doi:{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_acs(m: CitationMetadata) -> str:
        """American Chemical Society style"""
        authors = m.get_authors()

        names = []
        for a in authors[:10]:
            initials = "".join([n[0] + "." for n in (a.given or "").split() if n])
            names.append(f"{a.family}, {initials}")
        author_str = "; ".join(names)
        if len(authors) > 10:
            author_str += "; et al."

        parts = [author_str]
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"<i>{m.journal}</i>")
            if m.year:
                parts[-1] += f" <b>{m.year}</b>,"
            if m.volume:
                parts[-1] += f" <i>{m.volume}</i>"
            if m.issue:
                parts[-1] += f" ({m.issue})"
            if m.pages:
                parts[-1] += f", {m.pages}"
            parts[-1] += "."

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_nature(m: CitationMetadata) -> str:
        """Nature journal style"""
        authors = m.get_authors()
        author_str = CitationFormatter._get_author_string(authors, "nature")

        parts = [author_str]
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"<i>{m.journal}</i>")
            if m.volume:
                parts[-1] += f" <b>{m.volume}</b>,"
            if m.pages:
                parts[-1] += f" {m.pages}"
            if m.year:
                parts[-1] += f" ({m.year})."

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_science(m: CitationMetadata) -> str:
        """Science journal style"""
        authors = m.get_authors()

        names = []
        for a in authors[:10]:
            initials = " ".join([n[0] + "." for n in (a.given or "").split() if n])
            names.append(f"{a.family} {initials}".strip())

        if len(authors) > 10:
            author_str = ", ".join(names) + ", et al."
        else:
            author_str = ", ".join(names)

        parts = [author_str + ","]
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"<i>{m.journal}</i>")
            if m.volume:
                parts[-1] += f" <b>{m.volume}</b>,"
            if m.pages:
                parts[-1] += f" {m.pages}"
            if m.year:
                parts[-1] += f" ({m.year})."

        if m.doi:
            parts.append(f"doi:{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_cell(m: CitationMetadata) -> str:
        """Cell journal style"""
        authors = m.get_authors()

        names = []
        for a in authors[:10]:
            initials = "".join([n[0] + "." for n in (a.given or "").split() if n])
            names.append(f"{a.family}, {initials}")

        if len(authors) > 10:
            author_str = ", ".join(names) + ", et al."
        elif len(names) > 1:
            author_str = ", ".join(names[:-1]) + ", and " + names[-1]
        else:
            author_str = names[0] if names else ""

        parts = [author_str]
        if m.year:
            parts.append(f"({m.year}).")
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"<i>{m.journal}</i>")
            if m.volume:
                parts[-1] += f" <i>{m.volume}</i>,"
            if m.pages:
                parts[-1] += f" {m.pages}."

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}.")

        return " ".join(parts)

    @staticmethod
    def _format_plos(m: CitationMetadata) -> str:
        """PLOS journals style"""
        authors = m.get_authors()

        names = []
        for a in authors:
            initials = "".join([n[0] for n in (a.given or "").split() if n])
            names.append(f"{a.family} {initials}")

        if len(names) > 1:
            author_str = ", ".join(names[:-1]) + ", " + names[-1]
        else:
            author_str = names[0] if names else ""

        parts = [author_str]
        if m.year:
            parts.append(f"({m.year})")
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"{m.journal}")
            if m.volume:
                parts[-1] += f" {m.volume}"
            if m.issue:
                parts[-1] += f"({m.issue}):"
            if m.pages:
                parts[-1] += f" {m.pages}."

        if m.doi:
            parts.append(f"https://doi.org/{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_elsevier_harvard(m: CitationMetadata) -> str:
        """Elsevier Harvard style"""
        return CitationFormatter._format_harvard(m)

    @staticmethod
    def _format_springer(m: CitationMetadata) -> str:
        """Springer Basic style"""
        authors = m.get_authors()

        names = []
        for a in authors[:3]:
            initials = "".join([n[0] for n in (a.given or "").split() if n])
            names.append(f"{a.family} {initials}")

        if len(authors) > 3:
            author_str = ", ".join(names) + " et al"
        else:
            author_str = ", ".join(names)

        parts = [author_str]
        if m.year:
            parts.append(f"({m.year})")
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"{m.journal}")
            if m.volume:
                parts[-1] += f" {m.volume}:"
            if m.pages:
                parts[-1] += m.pages

        if m.doi:
            parts.append(f". https://doi.org/{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_taylor_francis(m: CitationMetadata) -> str:
        """Taylor & Francis style"""
        return CitationFormatter._format_apa(m)

    @staticmethod
    def _format_bmj(m: CitationMetadata) -> str:
        """BMJ (British Medical Journal) style"""
        return CitationFormatter._format_vancouver(m)

    @staticmethod
    def _format_lancet(m: CitationMetadata) -> str:
        """The Lancet style"""
        authors = m.get_authors()

        names = []
        for a in authors[:6]:
            initials = "".join([n[0] for n in (a.given or "").split() if n])
            names.append(f"{a.family} {initials}")

        if len(authors) > 6:
            author_str = ", ".join(names) + ", et al."
        else:
            author_str = ", ".join(names) + "."

        parts = [author_str]
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"<i>{m.journal}</i>")
            if m.year:
                parts[-1] += f" {m.year};"
            if m.volume:
                parts[-1] += f" {m.volume}:"
            if m.pages:
                parts[-1] += f" {m.pages}."

        return " ".join(parts)

    @staticmethod
    def _format_jama(m: CitationMetadata) -> str:
        """JAMA (Journal of the American Medical Association) style"""
        authors = m.get_authors()

        names = []
        for a in authors[:6]:
            initials = "".join([n[0] for n in (a.given or "").split() if n])
            names.append(f"{a.family} {initials}")

        if len(authors) > 6:
            author_str = ", ".join(names) + ", et al."
        else:
            author_str = ", ".join(names) + "."

        parts = [author_str]
        parts.append(f"{m.title}.")

        if m.journal:
            parts.append(f"<i>{m.journal}</i>.")
            year_vol = ""
            if m.year:
                year_vol = f"{m.year};"
            if m.volume:
                year_vol += m.volume
            if m.issue:
                year_vol += f"({m.issue})"
            if m.pages:
                year_vol += f":{m.pages}"
            if year_vol:
                parts.append(year_vol + ".")

        if m.doi:
            parts.append(f"doi:{m.doi}")

        return " ".join(parts)

    @staticmethod
    def _format_oscola(m: CitationMetadata) -> str:
        """OSCOLA (Oxford University Standard for Citation of Legal Authorities)"""
        authors = m.get_authors()

        if authors:
            author_str = " and ".join([a.format_full() for a in authors[:3]])
            if len(authors) > 3:
                author_str += " and others"
        else:
            author_str = ""

        parts = [author_str + ","]
        parts.append(f"'{m.title}'")

        if m.journal:
            if m.year:
                parts.append(f"({m.year})")
            if m.volume:
                parts.append(m.volume)
            parts.append(f"<i>{m.journal}</i>")
            if m.pages:
                parts.append(m.pages)

        return " ".join(parts)

    @staticmethod
    def _format_bluebook(m: CitationMetadata) -> str:
        """Bluebook legal citation style"""
        authors = m.get_authors()

        if authors:
            author_str = " & ".join([a.format_full() for a in authors[:2]])
            if len(authors) > 2:
                author_str += " et al."
        else:
            author_str = ""

        parts = [author_str + ","]
        parts.append(f"<i>{m.title}</i>,")

        if m.volume:
            parts.append(m.volume)
        if m.journal:
            parts.append(f"{m.journal}")
        if m.pages:
            parts.append(m.pages)
        if m.year:
            parts.append(f"({m.year}).")

        return " ".join(parts)

    @staticmethod
    def _format_turabian(m: CitationMetadata) -> str:
        """Turabian style (similar to Chicago)"""
        return CitationFormatter._format_chicago_author_date(m)


# =============================================================================
# EXPORT FORMAT GENERATORS
# =============================================================================

class ExportGenerator:
    """Generate citations in various export formats"""

    @staticmethod
    def to_bibtex(metadata: CitationMetadata) -> str:
        """Generate BibTeX format"""
        authors = metadata.get_authors()
        first_author = authors[0].family if authors else "Unknown"
        year = metadata.year or "0000"
        cite_key = re.sub(r'[^a-zA-Z0-9]', '', f"{first_author}{year}")

        entry_type = metadata.type or "article"
        if entry_type == "article":
            bibtex_type = "article"
        elif entry_type in ["book", "monograph"]:
            bibtex_type = "book"
        elif entry_type == "chapter":
            bibtex_type = "incollection"
        elif entry_type in ["conference", "proceedings"]:
            bibtex_type = "inproceedings"
        else:
            bibtex_type = "misc"

        lines = [f"@{bibtex_type}{{{cite_key},"]

        if authors:
            author_str = " and ".join([a.format_full() for a in authors])
            lines.append(f"  author = {{{author_str}}},")

        lines.append(f"  title = {{{metadata.title}}},")

        if metadata.journal:
            lines.append(f"  journal = {{{metadata.journal}}},")
        if metadata.year:
            lines.append(f"  year = {{{metadata.year}}},")
        if metadata.volume:
            lines.append(f"  volume = {{{metadata.volume}}},")
        if metadata.issue:
            lines.append(f"  number = {{{metadata.issue}}},")
        if metadata.pages:
            lines.append(f"  pages = {{{metadata.pages}}},")
        if metadata.doi:
            lines.append(f"  doi = {{{metadata.doi}}},")
        if metadata.publisher:
            lines.append(f"  publisher = {{{metadata.publisher}}},")
        if metadata.isbn:
            lines.append(f"  isbn = {{{metadata.isbn}}},")
        if metadata.url:
            lines.append(f"  url = {{{metadata.url}}},")
        if metadata.abstract:
            lines.append(f"  abstract = {{{metadata.abstract}}},")
        if metadata.keywords:
            lines.append(f"  keywords = {{{', '.join(metadata.keywords)}}},")

        # Remove trailing comma from last field
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]

        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def to_ris(metadata: CitationMetadata) -> str:
        """Generate RIS format"""
        lines = []

        # Type mapping
        type_map = {
            "article": "JOUR",
            "book": "BOOK",
            "chapter": "CHAP",
            "conference": "CONF",
            "thesis": "THES",
            "report": "RPRT",
            "webpage": "ELEC",
        }
        ris_type = type_map.get(metadata.type or "article", "GEN")
        lines.append(f"TY  - {ris_type}")

        # Authors
        for author in metadata.get_authors():
            lines.append(f"AU  - {author.format_family_first()}")

        lines.append(f"TI  - {metadata.title}")

        if metadata.journal:
            lines.append(f"JO  - {metadata.journal}")
            lines.append(f"T2  - {metadata.journal}")
        if metadata.year:
            lines.append(f"PY  - {metadata.year}")
            lines.append(f"Y1  - {metadata.year}")
        if metadata.volume:
            lines.append(f"VL  - {metadata.volume}")
        if metadata.issue:
            lines.append(f"IS  - {metadata.issue}")
        if metadata.pages:
            if "-" in metadata.pages:
                sp, ep = metadata.pages.split("-", 1)
                lines.append(f"SP  - {sp.strip()}")
                lines.append(f"EP  - {ep.strip()}")
            else:
                lines.append(f"SP  - {metadata.pages}")
        if metadata.doi:
            lines.append(f"DO  - {metadata.doi}")
        if metadata.url:
            lines.append(f"UR  - {metadata.url}")
        if metadata.publisher:
            lines.append(f"PB  - {metadata.publisher}")
        if metadata.isbn:
            lines.append(f"SN  - {metadata.isbn}")
        if metadata.issn:
            lines.append(f"SN  - {metadata.issn}")
        if metadata.abstract:
            lines.append(f"AB  - {metadata.abstract}")
        for kw in metadata.keywords:
            lines.append(f"KW  - {kw}")
        if metadata.language:
            lines.append(f"LA  - {metadata.language}")

        lines.append("ER  - ")
        return "\n".join(lines)

    @staticmethod
    def to_endnote(metadata: CitationMetadata) -> str:
        """Generate EndNote format (similar to RIS)"""
        return ExportGenerator.to_ris(metadata)

    @staticmethod
    def to_plain_text(metadata: CitationMetadata, style: CitationStyle = CitationStyle.APA) -> str:
        """Generate plain text citation (strips HTML)"""
        formatted = CitationFormatter.format(metadata, style)
        # Remove HTML tags
        plain = re.sub(r'<[^>]+>', '', formatted)
        return plain

    @staticmethod
    def to_csl_json(metadata: CitationMetadata) -> Dict[str, Any]:
        """Generate CSL-JSON format"""
        authors = metadata.get_authors()

        csl = {
            "type": "article-journal" if metadata.type == "article" else metadata.type,
            "title": metadata.title,
            "author": [
                {"family": a.family, "given": a.given} if not a.literal
                else {"literal": a.literal}
                for a in authors
            ],
        }

        if metadata.journal:
            csl["container-title"] = metadata.journal
        if metadata.year:
            csl["issued"] = {"date-parts": [[int(metadata.year)]]}
        if metadata.volume:
            csl["volume"] = metadata.volume
        if metadata.issue:
            csl["issue"] = metadata.issue
        if metadata.pages:
            csl["page"] = metadata.pages
        if metadata.doi:
            csl["DOI"] = metadata.doi
        if metadata.url:
            csl["URL"] = metadata.url
        if metadata.publisher:
            csl["publisher"] = metadata.publisher
        if metadata.isbn:
            csl["ISBN"] = metadata.isbn
        if metadata.issn:
            csl["ISSN"] = metadata.issn
        if metadata.abstract:
            csl["abstract"] = metadata.abstract

        return csl

    @staticmethod
    def export(metadata: CitationMetadata, format: ExportFormat, style: CitationStyle = CitationStyle.APA) -> str:
        """Export citation in specified format"""
        if format == ExportFormat.BIBTEX:
            return ExportGenerator.to_bibtex(metadata)
        elif format == ExportFormat.RIS:
            return ExportGenerator.to_ris(metadata)
        elif format == ExportFormat.ENDNOTE:
            return ExportGenerator.to_endnote(metadata)
        elif format == ExportFormat.PLAIN_TEXT:
            return ExportGenerator.to_plain_text(metadata, style)
        elif format == ExportFormat.JSON:
            return str(metadata.model_dump())
        elif format == ExportFormat.CSL_JSON:
            import json
            return json.dumps(ExportGenerator.to_csl_json(metadata), indent=2)
        else:
            return ExportGenerator.to_plain_text(metadata, style)


# =============================================================================
# DOI LOOKUP SERVICE
# =============================================================================

class DOIService:
    """Service for fetching metadata from DOI using CrossRef API"""

    CROSSREF_API = "https://api.crossref.org/works"

    @staticmethod
    async def lookup(doi: str) -> CitationMetadata:
        """Fetch paper metadata from CrossRef API using DOI"""
        # Clean DOI
        doi = doi.strip()
        if doi.startswith("https://doi.org/"):
            doi = doi[16:]
        elif doi.startswith("http://doi.org/"):
            doi = doi[15:]
        elif doi.startswith("doi:"):
            doi = doi[4:]

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{DOIService.CROSSREF_API}/{doi}",
                    headers={
                        "User-Agent": "SciSpace-Clone/1.0 (mailto:support@example.com)",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                data = response.json()

                return DOIService._parse_crossref_response(data, doi)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"DOI not found: {doi}")
                raise HTTPException(status_code=502, detail=f"CrossRef API error: {str(e)}")
            except httpx.RequestError as e:
                raise HTTPException(status_code=502, detail=f"Failed to connect to CrossRef: {str(e)}")

    @staticmethod
    def _parse_crossref_response(data: Dict[str, Any], doi: str) -> CitationMetadata:
        """Parse CrossRef API response into CitationMetadata"""
        message = data.get("message", {})

        # Parse authors
        authors = []
        for author in message.get("author", []):
            authors.append(Author(
                given=author.get("given", ""),
                family=author.get("family", ""),
                literal=author.get("name")  # For organizations
            ))

        # Parse date
        date_parts = message.get("published-print", message.get("published-online", {}))
        date_parts = date_parts.get("date-parts", [[]])[0]
        year = str(date_parts[0]) if len(date_parts) > 0 else ""
        month = str(date_parts[1]) if len(date_parts) > 1 else ""
        day = str(date_parts[2]) if len(date_parts) > 2 else ""

        # Parse pages
        pages = message.get("page", "")

        # Parse type
        type_mapping = {
            "journal-article": "article",
            "book": "book",
            "book-chapter": "chapter",
            "proceedings-article": "conference",
            "dissertation": "thesis",
            "report": "report",
        }
        pub_type = type_mapping.get(message.get("type", ""), "article")

        # Get container title (journal name)
        container = message.get("container-title", [])
        journal = container[0] if container else ""

        # Get short container title as alternative
        if not journal:
            short_container = message.get("short-container-title", [])
            journal = short_container[0] if short_container else ""

        return CitationMetadata(
            title=message.get("title", [""])[0],
            authors=authors,
            year=year,
            month=month,
            day=day,
            journal=journal,
            volume=message.get("volume", ""),
            issue=message.get("issue", ""),
            pages=pages,
            doi=doi,
            url=message.get("URL", f"https://doi.org/{doi}"),
            publisher=message.get("publisher", ""),
            issn=message.get("ISSN", [""])[0] if message.get("ISSN") else "",
            abstract=message.get("abstract", ""),
            type=pub_type,
            language=message.get("language", "en"),
        )

    @staticmethod
    async def batch_lookup(dois: List[str]) -> List[Dict[str, Any]]:
        """Fetch metadata for multiple DOIs"""
        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for doi in dois:
                try:
                    metadata = await DOIService.lookup(doi)
                    results.append({
                        "doi": doi,
                        "success": True,
                        "metadata": metadata.model_dump()
                    })
                except HTTPException as e:
                    results.append({
                        "doi": doi,
                        "success": False,
                        "error": e.detail
                    })
                except Exception as e:
                    results.append({
                        "doi": doi,
                        "success": False,
                        "error": str(e)
                    })
        return results


# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

async def save_citation_to_db(
    metadata: CitationMetadata,
    style: str,
    formatted: str,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    tags: List[str] = []
) -> Dict[str, Any]:
    """Save citation to database"""
    try:
        citation_data = {
            "metadata": metadata.model_dump(),
            "style": style,
            "formatted": formatted,
        }

        # Add optional fields only if provided
        if user_id:
            citation_data["user_id"] = user_id
        if project_id:
            citation_data["project_id"] = project_id
        if tags:
            citation_data["tags"] = tags

        result = supabase.table("citations").insert(citation_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save citation: {str(e)}")


async def get_citations_from_db(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    style: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get citations from database with filtering"""
    try:
        query = supabase.table("citations").select("*")

        if user_id:
            query = query.eq("user_id", user_id)
        if project_id:
            query = query.eq("project_id", project_id)
        if style:
            query = query.eq("style", style)

        query = query.order("created_at", desc=True)
        query = query.range(offset, offset + limit - 1)

        result = query.execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch citations: {str(e)}")


async def get_citation_by_id(citation_id: str) -> Dict[str, Any]:
    """Get a single citation by ID"""
    try:
        result = supabase.table("citations").select("*").eq("id", citation_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Citation not found")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch citation: {str(e)}")


async def delete_citation_from_db(citation_id: str) -> bool:
    """Delete a citation from database"""
    try:
        result = supabase.table("citations").delete().eq("id", citation_id).execute()
        return len(result.data) > 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete citation: {str(e)}")


async def update_citation_in_db(citation_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update a citation in database"""
    try:
        result = supabase.table("citations").update(updates).eq("id", citation_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Citation not found")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update citation: {str(e)}")


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.get("/styles")
async def list_citation_styles():
    """List all available citation styles"""
    return {
        "styles": [
            {"id": style.value, "name": style.name.replace("_", " ").title()}
            for style in CitationStyle
        ],
        "count": len(CitationStyle)
    }


@router.get("/formats")
async def list_export_formats():
    """List all available export formats"""
    return {
        "formats": [
            {"id": fmt.value, "name": fmt.name.replace("_", " ").title()}
            for fmt in ExportFormat
        ],
        "count": len(ExportFormat)
    }


@router.post("/doi/lookup")
async def lookup_doi(request: DOILookupRequest):
    """
    Lookup paper metadata from DOI using CrossRef API.
    Auto-fetches title, authors, journal, year, volume, issue, pages, etc.
    """
    metadata = await DOIService.lookup(request.doi)
    return {
        "doi": request.doi,
        "metadata": metadata.model_dump()
    }


@router.post("/doi/batch-lookup")
async def batch_lookup_dois(request: BatchDOIRequest):
    """
    Lookup metadata for multiple DOIs in batch.
    Returns results for each DOI including success/failure status.
    """
    results = await DOIService.batch_lookup(request.dois)
    return {
        "results": results,
        "total": len(request.dois),
        "successful": sum(1 for r in results if r.get("success"))
    }


@router.post("/generate", response_model=CitationResponse)
async def generate_citation(request: CitationRequest):
    """
    Generate a formatted citation in the specified style.
    Supports 20+ citation styles including APA, MLA, Chicago, IEEE, Harvard, etc.
    """
    formatted = CitationFormatter.format(request.metadata, request.style)

    return CitationResponse(
        formatted=formatted,
        style=request.style.value,
        metadata=request.metadata.model_dump()
    )


@router.post("/batch-generate", response_model=BatchCitationResponse)
async def batch_generate_citations(request: BatchCitationRequest):
    """
    Generate formatted citations for multiple items in batch.
    All citations use the same style.
    """
    citations = []
    for item in request.items:
        formatted = CitationFormatter.format(item, request.style)
        citations.append(CitationResponse(
            formatted=formatted,
            style=request.style.value,
            metadata=item.model_dump()
        ))

    return BatchCitationResponse(
        citations=citations,
        count=len(citations)
    )


@router.post("/save")
async def save_citation(request: SaveCitationRequest):
    """
    Save a citation to the database.
    Generates formatted citation if not provided.
    """
    # Generate formatted citation if not provided
    formatted = request.formatted
    if not formatted:
        formatted = CitationFormatter.format(request.metadata, request.style)

    # Save to database (no user_id required in dev mode)
    saved = await save_citation_to_db(
        metadata=request.metadata,
        style=request.style.value,
        formatted=formatted,
        project_id=request.project_id,
        tags=request.tags
    )

    return {
        "success": True,
        "citation": saved
    }


@router.get("/saved")
async def get_saved_citations(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    style: Optional[str] = Query(None, description="Filter by citation style"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get saved citations from the database.
    Supports filtering by project and style, with pagination.
    """
    citations = await get_citations_from_db(
        project_id=project_id,
        style=style,
        limit=limit,
        offset=offset
    )

    return {
        "citations": citations,
        "count": len(citations),
        "limit": limit,
        "offset": offset
    }


@router.get("/saved/{citation_id}")
async def get_citation(citation_id: str):
    """Get a single saved citation by ID"""
    citation = await get_citation_by_id(citation_id)
    return {"citation": citation}


@router.delete("/saved/{citation_id}")
async def delete_citation(citation_id: str):
    """Delete a saved citation"""
    success = await delete_citation_from_db(citation_id)
    return {"success": success}


@router.put("/saved/{citation_id}/style")
async def update_citation_style(
    citation_id: str,
    style: CitationStyle = Query(..., description="New citation style")
):
    """
    Update the style of a saved citation.
    Regenerates the formatted citation in the new style.
    """
    # Get existing citation
    citation = await get_citation_by_id(citation_id)

    # Recreate metadata object
    metadata = CitationMetadata(**citation["metadata"])

    # Generate new formatted citation
    formatted = CitationFormatter.format(metadata, style)

    # Update in database
    updated = await update_citation_in_db(citation_id, {
        "style": style.value,
        "formatted": formatted
    })

    return {"success": True, "citation": updated}


@router.post("/export")
async def export_citations(request: ExportRequest):
    """
    Export citations in various formats (BibTeX, RIS, plain text, etc.)
    """
    exports = []

    for citation_id in request.citation_ids:
        try:
            citation = await get_citation_by_id(citation_id)
            metadata = CitationMetadata(**citation["metadata"])

            exported = ExportGenerator.export(
                metadata,
                request.format,
                CitationStyle(citation.get("style", "apa"))
            )

            exports.append({
                "id": citation_id,
                "success": True,
                "exported": exported
            })
        except HTTPException as e:
            exports.append({
                "id": citation_id,
                "success": False,
                "error": e.detail
            })

    # Combine all exports into single output
    if request.format in [ExportFormat.BIBTEX, ExportFormat.RIS, ExportFormat.ENDNOTE]:
        combined = "\n\n".join([e["exported"] for e in exports if e.get("success")])
    else:
        combined = "\n".join([e["exported"] for e in exports if e.get("success")])

    return {
        "format": request.format.value,
        "exports": exports,
        "combined": combined,
        "count": len([e for e in exports if e.get("success")])
    }


@router.post("/export/direct")
async def export_citation_direct(
    metadata: CitationMetadata,
    format: ExportFormat = Query(ExportFormat.BIBTEX, description="Export format"),
    style: CitationStyle = Query(CitationStyle.APA, description="Citation style for plain text")
):
    """
    Export a citation directly without saving.
    Useful for one-off exports.
    """
    exported = ExportGenerator.export(metadata, format, style)

    return {
        "format": format.value,
        "exported": exported
    }


@router.post("/bibliography")
async def generate_bibliography(request: BibliographyRequest):
    """
    Generate a formatted bibliography from multiple citations.
    Supports sorting by author, year, or title.
    """
    citations_data = []

    for citation_id in request.citation_ids:
        try:
            citation = await get_citation_by_id(citation_id)
            metadata = CitationMetadata(**citation["metadata"])
            citations_data.append({
                "id": citation_id,
                "metadata": metadata,
                "formatted": CitationFormatter.format(metadata, request.style)
            })
        except HTTPException:
            continue

    # Sort citations
    if request.sort_by == "author":
        citations_data.sort(key=lambda x: (
            x["metadata"].get_authors()[0].family.lower()
            if x["metadata"].get_authors() else "zzz"
        ))
    elif request.sort_by == "year":
        citations_data.sort(key=lambda x: x["metadata"].year or "0000", reverse=True)
    elif request.sort_by == "title":
        citations_data.sort(key=lambda x: x["metadata"].title.lower())

    # Generate numbered bibliography
    bibliography_lines = []
    for i, item in enumerate(citations_data, 1):
        bibliography_lines.append(f"[{i}] {item['formatted']}")

    return {
        "style": request.style.value,
        "sort_by": request.sort_by,
        "citations": [
            {"id": c["id"], "formatted": c["formatted"]}
            for c in citations_data
        ],
        "bibliography": "\n\n".join(bibliography_lines),
        "count": len(citations_data)
    }


@router.post("/format-convert")
async def convert_citation_format(
    citation_id: str = Query(..., description="Citation ID to convert"),
    target_style: CitationStyle = Query(..., description="Target citation style")
):
    """
    Convert an existing citation to a different style.
    Returns the newly formatted citation without modifying the saved version.
    """
    citation = await get_citation_by_id(citation_id)
    metadata = CitationMetadata(**citation["metadata"])

    new_formatted = CitationFormatter.format(metadata, target_style)

    return {
        "original_style": citation.get("style"),
        "target_style": target_style.value,
        "original_formatted": citation.get("formatted"),
        "new_formatted": new_formatted
    }


@router.post("/parse-bibtex")
async def parse_bibtex(bibtex: str = Query(..., description="BibTeX string to parse")):
    """
    Parse a BibTeX entry and extract metadata.
    Useful for importing citations from BibTeX files.
    """
    # Simple BibTeX parser
    metadata = {}

    # Extract entry type and key
    entry_match = re.match(r'@(\w+)\s*\{\s*([^,]+),', bibtex)
    if entry_match:
        metadata["type"] = entry_match.group(1).lower()
        metadata["cite_key"] = entry_match.group(2)

    # Extract fields
    field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'
    for match in re.finditer(field_pattern, bibtex):
        field_name = match.group(1).lower()
        field_value = match.group(2)

        if field_name == "author":
            # Parse authors
            authors = []
            for author_str in field_value.split(" and "):
                author_str = author_str.strip()
                if "," in author_str:
                    parts = author_str.split(",", 1)
                    authors.append(Author(family=parts[0].strip(), given=parts[1].strip()))
                else:
                    parts = author_str.split()
                    if len(parts) >= 2:
                        authors.append(Author(given=" ".join(parts[:-1]), family=parts[-1]))
                    else:
                        authors.append(Author(literal=author_str))
            metadata["authors"] = [a.model_dump() for a in authors]
        elif field_name == "title":
            metadata["title"] = field_value
        elif field_name == "journal":
            metadata["journal"] = field_value
        elif field_name == "year":
            metadata["year"] = field_value
        elif field_name == "volume":
            metadata["volume"] = field_value
        elif field_name == "number":
            metadata["issue"] = field_value
        elif field_name == "pages":
            metadata["pages"] = field_value
        elif field_name == "doi":
            metadata["doi"] = field_value
        elif field_name == "publisher":
            metadata["publisher"] = field_value
        elif field_name == "url":
            metadata["url"] = field_value
        elif field_name == "abstract":
            metadata["abstract"] = field_value
        elif field_name == "keywords":
            metadata["keywords"] = [k.strip() for k in field_value.split(",")]

    return {
        "parsed": metadata,
        "valid": bool(metadata.get("title"))
    }
