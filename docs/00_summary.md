# FIB API Public Endpoint Discovery Summary

**Date**: 2025-10-17 17:57:32

**Success Rate**: 6/6 (100.0%)

## Discovered Endpoints

| Endpoint | Description | Status | Records |
|----------|-------------|--------|----------|
| `assignatures` | Course/subject catalog | ✅ Success | 364 |
| `quadrimestres` | Academic terms/semesters | ✅ Success | 21 |
| `examens` | Exam schedules | ✅ Success | 1867 |
| `noticies` | News and announcements | ✅ Success | 5 |
| `aules` | Classroom information | ✅ Success | 62 |
| `professors` | Professor directory | ✅ Success | N/A |

## Detailed Documentation

See individual endpoint documentation files:

- [assignatures.md](./assignatures.md) - Course/subject catalog
- [quadrimestres.md](./quadrimestres.md) - Academic terms/semesters
- [examens.md](./examens.md) - Exam schedules
- [noticies.md](./noticies.md) - News and announcements
- [aules.md](./aules.md) - Classroom information
- [professors.md](./professors.md) - Professor directory

## Next Steps

To access private endpoints (user-specific data), you need to:

1. Complete OAuth 2.0 authentication flow
2. Run `python oauth_client.py` to authenticate
3. Run `python discover_endpoints.py` to discover private endpoints

Private endpoints include:
- `/v2/jo` - User profile
- `/v2/jo/assignatures` - User's courses
- `/v2/jo/classes` - User's schedule
- `/v2/jo/avisos` - User's notices
