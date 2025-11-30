# FIB API Agent Tool Analysis

**Date**: 2025-10-17  
**Purpose**: Evaluate FIB API endpoints for use as agent tools in a conversational AI application

## Executive Summary

After analyzing 6 public endpoints (and identifying 4 private endpoints), this document recommends **7 endpoints** as the most valuable agent tools for a conversational FIB assistant. These tools enable both general information queries and personalized student assistance.

## Evaluation Criteria

Each endpoint is evaluated on:
1. **Conversational Usefulness**: How naturally users would ask about this data
2. **Data Richness**: Depth and quality of information provided
3. **Query Patterns**: Common user questions this endpoint can answer
4. **Real-time Value**: Whether data changes frequently or is relatively static
5. **Agent Suitability**: How well it fits into a conversational flow

**Rating Scale**: ⭐ (Poor) to ⭐⭐⭐⭐⭐ (Excellent)

---

## Public Endpoints Analysis

### 1. Assignatures (Courses/Subjects) ⭐⭐⭐⭐⭐

**Endpoint**: `/v2/assignatures`  
**Total Records**: 364 courses  
**Pagination**: Yes (200 per page)

#### Strengths
- **Highly conversational**: Users naturally ask "Tell me about course X" or "What courses are available in AI?"
- **Rich data**: Includes credits, semester, study plans, prerequisites, course guides
- **Searchable**: Can filter by code, name, study plan, semester
- **Links to details**: Each course has a guide URL with detailed syllabus

#### Common User Queries
- "What is the CPP-MAI course about?"
- "How many credits is the IA course?"
- "Which courses are available in Q1?"
- "Show me all masters courses in AI"
- "What are the prerequisites for course X?"

#### Data Sample
```json
{
  "id": "CPP-MAI",
  "nom": "Constraint Processing and Programming",
  "credits": 4.5,
  "quadrimestres": ["Q1"],
  "plans": ["MEI", "MAI"],
  "guia_docent_url_publica": "https://..."
}
```

#### Agent Tool Design
```python
def search_courses(
    query: str = None,  # Search by name or code
    semester: str = None,  # Q1, Q2
    study_plan: str = None,  # GRAU, MAI, etc
    credits: float = None
) -> List[Course]:
    """Search FIB courses by various criteria"""
```

**Recommendation**: ✅ **ESSENTIAL - Must Include**

---

### 2. Examens (Exam Schedules) ⭐⭐⭐⭐⭐

**Endpoint**: `/v2/examens`  
**Total Records**: 1,867 exams  
**Pagination**: Yes (all returned)

#### Strengths
- **Time-sensitive**: Students urgently need exam information
- **Highly actionable**: Users can plan study schedules around exam dates
- **Detailed**: Includes date, time, location, course, type (final/partial)
- **Filterable**: By course, date range, semester, year

#### Common User Queries
- "When is my next exam?"
- "When is the IA exam?"
- "What exams do I have in January?"
- "Where is the AC2 final exam?"
- "Show me all exams for course X"

#### Data Sample
```json
{
  "assig": "AC2",
  "aules": "A5101",
  "inici": "2024-01-09T08:00:00",
  "fi": "2024-01-09T11:00:00",
  "tipus": "F",  // Final
  "curs": 2023,
  "quatr": 1
}
```

#### Agent Tool Design
```python
def get_exam_schedule(
    course_code: str = None,
    start_date: str = None,
    end_date: str = None,
    semester: int = None,
    exam_type: str = None  # F=Final, P=Partial
) -> List[Exam]:
    """Get exam schedules with filtering"""
```

**Recommendation**: ✅ **ESSENTIAL - Must Include**

---

### 3. Quadrimestres (Academic Terms) ⭐⭐⭐⭐

**Endpoint**: `/v2/quadrimestres`  
**Total Records**: 21 terms  
**Pagination**: Yes (all returned)

#### Strengths
- **Contextual**: Helps determine "current" semester for other queries
- **Linking**: Each term links to its classes, exams, and courses
- **Temporal navigation**: Essential for historical and future queries
- **Small dataset**: Easy to cache and reference

#### Common User Queries
- "What's the current semester?"
- "Show me Q1 2024 schedule"
- "When does Q2 start?"
- "What courses are offered this semester?"

#### Data Sample
```json
{
  "id": "2025Q1",
  "actual": "S",  // Is current
  "actual_horaris": "S",
  "classes": "https://api.fib.upc.edu/v2/quadrimestres/2025Q1/classes/",
  "examens": "https://api.fib.upc.edu/v2/quadrimestres/2025Q1/examens/"
}
```

#### Agent Tool Design
```python
def get_academic_terms(
    current_only: bool = False,
    year: int = None
) -> List[Term]:
    """Get academic term information"""
    
def get_current_term() -> Term:
    """Quick accessor for current semester"""
```

**Recommendation**: ✅ **HIGHLY RECOMMENDED - Include**

---

### 4. Noticies (News & Announcements) ⭐⭐⭐⭐

**Endpoint**: `/v2/noticies`  
**Total Records**: 5 recent news items  
**Pagination**: Yes (all returned)

#### Strengths
- **Current events**: Students want to know "what's new at FIB"
- **Conversational starter**: Agent can proactively share news
- **Rich content**: Includes titles, descriptions, images, links
- **Time-stamped**: Can filter by recency

#### Common User Queries
- "What's new at FIB?"
- "Any recent announcements?"
- "Tell me about upcoming events"
- "When is Festibity Day?"

#### Data Sample
```json
{
  "titol": "The FIB inaugurates the 2025-2026 academic year",
  "link": "https://www.fib.upc.edu/en/news/...",
  "descripcio": "<div>Last Wednesday, 15th of October...",
  "data_publicacio": "2025-10-17T13:52:08"
}
```

#### Agent Tool Design
```python
def get_fib_news(
    limit: int = 5,
    since_date: str = None
) -> List[NewsItem]:
    """Get recent FIB news and announcements"""
```

**Recommendation**: ✅ **RECOMMENDED - Include for engagement**

---

### 5. Professors (Faculty Directory) ⭐⭐⭐⭐

**Endpoint**: `/v2/professors`  
**Total Records**: 520 professors  
**Pagination**: No (direct list)

#### Strengths
- **Contact information**: Students need to reach professors
- **Course mapping**: Links professors to their courses
- **Research profiles**: Links to FUTUR and APREN profiles
- **Searchable**: By name, department, course

#### Common User Queries
- "Who teaches IA?"
- "What's Professor X's email?"
- "Show me professors in the AC department"
- "Which professors teach in the AI masters?"
- "How do I contact my professor?"

#### Data Sample
```json
{
  "nom": "Sergi",
  "cognoms": "Abadal Cavallé",
  "obfuscated_email": "abadal(at)ac.upc.edu",
  "assignatures": ["FINE-MIRI"],
  "departament": "AC",
  "futur_url": "https://futur.upc.edu/1069516"
}
```

#### Agent Tool Design
```python
def search_professors(
    name: str = None,
    course_code: str = None,
    department: str = None
) -> List[Professor]:
    """Search FIB faculty directory"""
```

**Recommendation**: ✅ **RECOMMENDED - Include**

---

### 6. Aules (Classrooms) ⭐⭐

**Endpoint**: `/v2/aules`  
**Total Records**: 62 classrooms  
**Pagination**: Yes (all returned)

#### Strengths
- **Location queries**: "Where is my next class?"
- **Room reservations**: Links to reservation system
- **Simple data**: Easy to integrate

#### Weaknesses
- **Limited data**: Only room IDs and reservation links
- **Less conversational**: Users rarely ask about rooms directly
- **Better as metadata**: More useful as part of schedule/exam data

#### Common User Queries
- "Where is room A5101?"
- "Is room X available?"
- "Show me all classrooms"

#### Agent Tool Design
```python
def get_classroom_info(room_id: str) -> Classroom:
    """Get information about a specific classroom"""
```

**Recommendation**: ⚠️ **OPTIONAL - Low priority, better as supporting data**

---

## Private Endpoints Analysis

These require OAuth authentication but provide highly personalized data.

### 7. `/v2/jo` (User Profile) ⭐⭐⭐⭐⭐

#### Strengths
- **Personalization**: Core data for user-specific queries
- **Authentication**: Validates user identity
- **Context**: Provides student/professor status, degree program

#### Common User Queries
- "What's my student ID?"
- "Show me my profile"
- "What program am I enrolled in?"

**Recommendation**: ✅ **ESSENTIAL for private app**

---

### 8. `/v2/jo/assignatures` (My Courses) ⭐⭐⭐⭐⭐

#### Strengths
- **Highly personal**: User's actual enrolled courses
- **Actionable**: Drives many follow-up queries
- **Rich data**: Includes grades, course details, status

#### Common User Queries
- "What courses am I taking?"
- "What's my grade in course X?"
- "Am I passing all my courses?"
- "How many credits am I taking this semester?"

**Recommendation**: ✅ **ESSENTIAL for private app**

---

### 9. `/v2/jo/classes` (My Schedule) ⭐⭐⭐⭐⭐

#### Strengths
- **Daily utility**: Users check schedule constantly
- **Time-sensitive**: "When is my next class?"
- **Location data**: Where to go right now

#### Common User Queries
- "When is my next class?"
- "What classes do I have today?"
- "Show me my schedule for this week"
- "When does my IA class meet?"

**Recommendation**: ✅ **ESSENTIAL for private app**

---

### 10. `/v2/jo/avisos` (My Notices) ⭐⭐⭐⭐

#### Strengths
- **Alerts**: Important personalized notifications
- **Proactive**: Agent can notify user of new messages
- **Course-specific**: Announcements from professors

#### Common User Queries
- "Do I have any new notices?"
- "Any announcements in my courses?"
- "What did my professor say about the exam?"

**Recommendation**: ✅ **HIGHLY RECOMMENDED for private app**

---

## Final Recommendations

### Core Agent Tools (Must Have)

#### For Public App
1. **search_courses** - Course catalog search
2. **get_exam_schedule** - Exam information
3. **get_academic_terms** - Semester context
4. **search_professors** - Faculty lookup
5. **get_fib_news** - News and announcements

#### For Private App (Add to above)
6. **get_my_profile** - User information
7. **get_my_courses** - Enrolled courses with grades
8. **get_my_schedule** - Personal class schedule  
9. **get_my_notices** - Personal notifications

### Implementation Priority

**Phase 1** (Immediate value)
- ✅ Courses search
- ✅ Exam schedules
- ✅ Academic terms (for context)

**Phase 2** (Enhanced functionality)
- ✅ Professor search
- ✅ News feed
- ✅ OAuth implementation

**Phase 3** (Private features)
- ✅ My profile
- ✅ My courses
- ✅ My schedule
- ✅ My notices

### Tool Architecture Recommendations

#### 1. Caching Strategy
- **Courses, Professors**: Cache for 24 hours (relatively static)
- **Exams**: Cache for 1 hour (important but stable)
- **News**: Cache for 15 minutes (semi-dynamic)
- **Academic Terms**: Cache for 7 days (very static)
- **User data**: No cache (must be fresh)

#### 2. Error Handling
```python
class FIBAPIError(Exception):
    """Base exception for FIB API errors"""
    
class AuthenticationError(FIBAPIError):
    """OAuth token expired or invalid"""
    
class RateLimitError(FIBAPIError):
    """API rate limit exceeded"""
```

#### 3. Response Formatting
```python
class AgentResponse:
    """Structured response for LLM consumption"""
    data: Dict[str, Any]
    summary: str  # Human-readable summary
    confidence: float  # How well query matched
    follow_ups: List[str]  # Suggested next questions
```

#### 4. Query Understanding
Map natural language to API calls:
- "When's my exam?" → get_exam_schedule(user_courses)
- "Tell me about IA" → search_courses(query="IA")
- "Who teaches this?" → search_professors(course="X")
- "What's new?" → get_fib_news(limit=3)

---

## Sample Agent Tool Implementation

```python
class FIBAgentTools:
    """Agent tools for FIB conversational assistant"""
    
    def __init__(self, client_id: str, oauth_client: Optional[FIBOAuthClient] = None):
        self.client_id = client_id
        self.oauth_client = oauth_client
        self.cache = {}
    
    @tool("Search FIB courses by name, code, or criteria")
    def search_courses(
        self,
        query: str = None,
        semester: str = None,
        credits: float = None
    ) -> str:
        """
        Search the FIB course catalog.
        
        Args:
            query: Course name or code to search for
            semester: Filter by semester (Q1, Q2)
            credits: Filter by credit value
            
        Returns:
            Formatted course information
        """
        # Implementation here
        pass
    
    @tool("Get exam schedules for courses")
    def get_exam_schedule(
        self,
        course_code: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> str:
        """Get upcoming exam schedules"""
        # Implementation here
        pass
    
    @tool("Get user's enrolled courses (requires authentication)")
    def get_my_courses(self) -> str:
        """Get the authenticated user's current courses"""
        if not self.oauth_client or not self.oauth_client.access_token:
            return "Authentication required. Please log in first."
        # Implementation here
        pass
```

---

## Metrics for Success

### Engagement Metrics
- % of queries successfully answered
- Average conversation length
- User satisfaction ratings
- Repeat usage rate

### Tool Usage Metrics
- Most frequently called tools
- Average response time per tool
- Cache hit rates
- Error rates by tool

### Quality Metrics
- Query understanding accuracy
- Response relevance scores
- Follow-up question quality
- Tool selection accuracy

---

## Conclusion

The FIB API provides excellent coverage for building a conversational assistant. The recommended 9 tools (5 public + 4 private) create a comprehensive agent capable of:

1. **Information Retrieval**: Courses, exams, professors, news
2. **Personal Assistant**: My schedule, grades, notices
3. **Navigation**: Current semester, classroom locations
4. **Discovery**: Browse courses, find professors, explore programs

The combination of public and private endpoints enables both general FIB information queries and personalized student assistance, making for a highly valuable conversational experience.

