"""
Pydantic models for FIB API data types.

These models provide type-safe representations of the FIB API responses,
enabling better validation, IDE support, and serialization.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PaginatedResponse[T](BaseModel):
    """Generic paginated response wrapper for FIB API endpoints."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[T]


class CourseObligatorietat(BaseModel):
    """Course requirement/obligation type within a study plan."""

    codi_oblig: str = Field(description="Obligation code (OBL, OPT, etc.)")
    codi_especialitat: str = Field(default="", description="Specialization code")
    pla: str = Field(description="Study plan code")
    nom_especialitat: str = Field(default="", description="Specialization name")


class Course(BaseModel):
    """FIB course/subject (assignatura) information."""

    id: str = Field(description="Course code identifier")
    url: str = Field(description="API URL for course details")
    guia: str | None = Field(default=None, description="API URL for course guide")
    obligatorietats: list[CourseObligatorietat] = Field(default_factory=list)
    plans: list[str] = Field(default_factory=list, description="Study plans offering this course")
    lang: dict[str, list[str]] = Field(default_factory=dict, description="Languages by semester")
    quadrimestres: list[str] = Field(default_factory=list, description="Semesters when offered (Q1, Q2)")
    sigles: str = Field(description="Course acronym")
    codi_upc: str = Field(description="UPC course code")
    semestre: str = Field(description="Typical semester (S1-S8)")
    credits: float = Field(description="ECTS credits")
    vigent: str = Field(description="Active status (S/N)")
    guia_docent_externa: str = Field(default="")
    nom: str = Field(description="Course name")
    guia_docent_url_publica: str = Field(default="", description="Public syllabus URL")

    @property
    def is_active(self) -> bool:
        return self.vigent == "S"


class Exam(BaseModel):
    """FIB exam schedule entry."""

    id: int = Field(description="Exam entry ID")
    assig: str = Field(description="Course code")
    codi_upc: str = Field(description="UPC course code")
    aules: str = Field(description="Classroom(s) for the exam")
    inici: datetime = Field(description="Exam start datetime")
    fi: datetime = Field(description="Exam end datetime")
    quatr: int = Field(description="Semester number (1 or 2)")
    curs: int = Field(description="Academic year (e.g., 2023 for 2023-2024)")
    pla: str = Field(description="Study plan code")
    tipus: str = Field(description="Exam type (F=Final, P=Partial)")
    tipus_assignatura: str = Field(default="", description="Course type description")
    comentaris: str = Field(default="", description="Additional comments")
    eslaboratori: str = Field(default="", description="Lab indicator")

    @property
    def is_final(self) -> bool:
        return self.tipus == "F"

    @property
    def is_partial(self) -> bool:
        return self.tipus == "P"


class Professor(BaseModel):
    """FIB professor/faculty member."""

    id: int = Field(description="Professor ID")
    assignatures: list[str] = Field(default_factory=list, description="Courses taught")
    plans_estudi: list[str] = Field(default_factory=list, description="Study plans")
    especialitats: list[str] = Field(default_factory=list, description="Specializations")
    obfuscated_email: str = Field(description="Email with (at) instead of @")
    nom: str = Field(description="First name")
    cognoms: str = Field(description="Last name(s)")
    departament: str = Field(description="Department code")
    futur_url: str = Field(default="", description="FUTUR research profile URL")
    apren_url: str = Field(default="", description="APREN teaching profile URL")

    @property
    def full_name(self) -> str:
        return f"{self.nom} {self.cognoms}"

    @property
    def email(self) -> str:
        return self.obfuscated_email.replace("(at)", "@")


class Classroom(BaseModel):
    """FIB classroom/room."""

    id: str = Field(description="Room identifier")
    reserves: str = Field(description="API URL for room reservations")

    @property
    def building(self) -> str:
        if self.id and len(self.id) > 0 and self.id[0].isalpha():
            return self.id[0]
        return ""


class AcademicTerm(BaseModel):
    """FIB academic term/semester (quadrimestre)."""

    id: str = Field(description="Term identifier (e.g., 2025Q1)")
    url: str = Field(description="API URL for term details")
    actual: str = Field(description="Is current term (S/N)")
    actual_horaris: str = Field(description="Has current schedules (S/N)")
    classes: str = Field(description="API URL for classes")
    examens: str = Field(description="API URL for exams")
    assignatures: str = Field(description="API URL for courses")

    @property
    def is_current(self) -> bool:
        return self.actual == "S"

    @property
    def year(self) -> int:
        return int(self.id[:4])

    @property
    def semester(self) -> int:
        return int(self.id[-1])


class NewsItem(BaseModel):
    """FIB news/announcement item."""

    titol: str = Field(description="News title")
    link: str = Field(description="Full article URL")
    descripcio: str = Field(description="HTML description/summary")
    data_publicacio: datetime = Field(description="Publication datetime")

    @property
    def plain_description(self) -> str:
        import re

        clean = re.sub(r"<[^>]+>", "", self.descripcio)
        return clean.strip()


# Private endpoint models (require OAuth authentication)


class UserProfile(BaseModel):
    """User profile from /v2/jo endpoint."""

    username: str = Field(description="FIB username/identifier")
    nom: str = Field(description="First name")
    cognoms: str = Field(description="Last name(s)")
    email: str = Field(description="Email address")
    foto: str = Field(default="", description="Profile photo URL")
    tipus: str = Field(default="estudiant", description="User type (estudiant, professor, etc.)")
    plans_estudi: list[str] = Field(default_factory=list, description="Enrolled study plans")

    @property
    def full_name(self) -> str:
        return f"{self.nom} {self.cognoms}"

    @property
    def is_student(self) -> bool:
        return self.tipus.lower() == "estudiant"

    @property
    def is_professor(self) -> bool:
        return self.tipus.lower() == "professor"


class UserCourse(BaseModel):
    """User's enrolled course from /v2/jo/assignatures endpoint."""

    id: str = Field(description="Course code")
    url: str = Field(default="", description="API URL for course details")
    nom: str = Field(description="Course name")
    credits: float = Field(description="ECTS credits")
    quadrimestre: str = Field(default="", description="Semester (Q1, Q2)")
    grup: str = Field(default="", description="Assigned group")
    nota: float | None = Field(default=None, description="Grade if available")
    qualificacio: str = Field(default="", description="Qualification (A, B, C, etc.)")
    convocatoria: str = Field(default="", description="Exam session (ORD, EXT)")

    @property
    def is_passed(self) -> bool:
        if self.nota is not None:
            return self.nota >= 5.0
        return self.qualificacio.upper() in ("A", "B", "C", "D")


class UserClass(BaseModel):
    """User's scheduled class from /v2/jo/classes endpoint."""

    codi_assig: str = Field(description="Course code")
    nom_assig: str = Field(default="", description="Course name")
    grup: str = Field(description="Class group")
    dia_setmana: int = Field(description="Day of week (1=Monday, 7=Sunday)")
    inici: str = Field(description="Start time (HH:MM)")
    fi: str = Field(default="", description="End time (HH:MM)")
    dupinici: str = Field(default="", description="Duration start")
    tipus: str = Field(description="Class type (T=Theory, L=Lab, P=Problems)")
    aules: str = Field(description="Classroom(s)")

    @property
    def day_name(self) -> str:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if 1 <= self.dia_setmana <= 7:
            return days[self.dia_setmana - 1]
        return "Unknown"

    @property
    def class_type_name(self) -> str:
        type_map = {"T": "Theory", "L": "Lab", "P": "Problems", "S": "Seminar"}
        return type_map.get(self.tipus.upper(), self.tipus)


class Attachment(BaseModel):
    """File attachment from notice."""

    nom: str = Field(default="", description="Attachment filename")
    url: str = Field(default="", description="Download URL")
    tipus_mime: str = Field(default="", description="MIME type")
    mida: int = Field(default=0, description="File size in bytes")
    data_modificacio: datetime | None = Field(default=None, description="Last modification datetime")


class UserNotice(BaseModel):
    """User's notification from /v2/jo/avisos endpoint."""

    id: int = Field(description="Notice ID")
    titol: str = Field(description="Notice title")
    codi_assig: str = Field(description="Course code")
    text: str = Field(description="Notice content (may contain HTML)")
    data_insercio: datetime = Field(description="Publication datetime")
    data_modificacio: datetime | None = Field(default=None, description="Last modification datetime")
    adjunts: list[Attachment] = Field(default_factory=list, description="Attachments")

    @property
    def plain_text(self) -> str:
        import re

        clean = re.sub(r"<[^>]+>", "", self.text)
        return clean.strip()
