# Exam schedules

**Endpoint**: `/v2/examens`

**Type**: Public (client_id only)

**Description**: Exam schedules

## Response Structure

- **Pagination**: Yes
- **Count**: 1867
- **Next**: None
- **Previous**: None
- **Results returned**: 1867

### Sample Record (First Result)

```json
{
  "id": 29845,
  "assig": "AC2",
  "codi_upc": "270060",
  "aules": "A5101",
  "inici": "2024-01-09T08:00:00",
  "fi": "2024-01-09T11:00:00",
  "quatr": 1,
  "curs": 2023,
  "pla": "GRAU",
  "tipus": "F",
  "tipus_assignatura": "OBL_ESP ENGCOM GRAU",
  "comentaris": "",
  "eslaboratori": ""
}
```

### Fields

- **id** (`int`): `29845`
- **assig** (`str`): `AC2`
- **codi_upc** (`str`): `270060`
- **aules** (`str`): `A5101`
- **inici** (`str`): `2024-01-09T08:00:00`
- **fi** (`str`): `2024-01-09T11:00:00`
- **quatr** (`int`): `1`
- **curs** (`int`): `2023`
- **pla** (`str`): `GRAU`
- **tipus** (`str`): `F`
- **tipus_assignatura** (`str`): `OBL_ESP ENGCOM GRAU`
- **comentaris** (`str`): ``
- **eslaboratori** (`str`): ``

### Additional Sample Records

#### Record 2

```json
{
  "id": 29844,
  "assig": "IA",
  "codi_upc": "270023",
  "aules": "A5E02",
  "inici": "2024-01-09T08:00:00",
  "fi": "2024-01-09T10:00:00",
  "quatr": 1,
  "curs": 2023,
  "pla": "GRAU",
  "tipus": "P",
  "tipus_assignatura": "OBL_ESP COM GRAU",
  "comentaris": "2n torn (Lliurament de projectes",
  "eslaboratori": ""
}
```

#### Record 3

```json
{
  "id": 29846,
  "assig": "ASW",
  "codi_upc": "270081",
  "aules": "A5E01",
  "inici": "2024-01-09T08:00:00",
  "fi": "2024-01-09T11:00:00",
  "quatr": 1,
  "curs": 2023,
  "pla": "GRAU",
  "tipus": "F",
  "tipus_assignatura": "OBL_ESP ENGSOFT GRAU",
  "comentaris": "",
  "eslaboratori": ""
}
```

#### Record 4

```json
{
  "id": 29956,
  "assig": "IML-MAI",
  "codi_upc": "270703",
  "aules": "UB Classroom",
  "inici": "2024-01-09T10:00:00",
  "fi": "2024-01-09T12:00:00",
  "quatr": 1,
  "curs": 2023,
  "pla": "MAI",
  "tipus": "F",
  "tipus_assignatura": "OBL MAI",
  "comentaris": "",
  "eslaboratori": ""
}
```

## Usage Example

```python
import requests

url = "https://api.fib.upc.edu/v2/examens"
headers = {
    "client_id": "YOUR_CLIENT_ID",
    "Accept": "application/json",
    "Accept-Language": "en"
}
response = requests.get(url, headers=headers)
data = response.json()
```


---
*Generated on 2025-10-17 17:57:31*
