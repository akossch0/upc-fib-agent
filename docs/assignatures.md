# Course/subject catalog

**Endpoint**: `/v2/assignatures`

**Type**: Public (client_id only)

**Description**: Course/subject catalog

## Response Structure

- **Pagination**: Yes
- **Count**: 364
- **Next**: https://api.fib.upc.edu/v2/assignatures/?page=2
- **Previous**: None
- **Results returned**: 200

### Sample Record (First Result)

```json
{
  "id": "CPP-MAI",
  "url": "https://api.fib.upc.edu/v2/assignatures/CPP-MAI/",
  "guia": "https://api.fib.upc.edu/v2/assignatures/CPP-MAI/guia/",
  "obligatorietats": [
    {
      "codi_oblig": "OPT",
      "codi_especialitat": "MAI-MRPS",
      "pla": "MAI",
      "nom_especialitat": "Modelling, Reasoning and Problem Solving"
    }
  ],
  "plans": [
    "MEI",
    "MAI"
  ],
  "lang": {
    "Q1": [],
    "Q2": []
  },
  "quadrimestres": [
    "Q1"
  ],
  "sigles": "CPP-MAI",
  "codi_upc": "270725",
  "semestre": "S3",
  "credits": 4.5,
  "vigent": "S",
  "guia_docent_externa": "",
  "nom": "Constraint Processing and Programming",
  "guia_docent_url_publica": "https://www.fib.upc.edu/en/studies/masters/master-artificial-intelligence/curriculum/syllabus/CPP-MAI"
}
```

### Fields

- **id** (`str`): `CPP-MAI`
- **url** (`str`): `https://api.fib.upc.edu/v2/assignatures/CPP-MAI/`
- **guia** (`str`): `https://api.fib.upc.edu/v2/assignatures/CPP-MAI/guia/`
- **obligatorietats** (`list[object]`): Array of objects
- **plans** (`list[str]`): ['MEI', 'MAI']
- **lang** (`dict`): Nested object
  - **lang.Q1** (`list`): Empty array
  - **lang.Q2** (`list`): Empty array
- **quadrimestres** (`list[str]`): ['Q1']
- **sigles** (`str`): `CPP-MAI`
- **codi_upc** (`str`): `270725`
- **semestre** (`str`): `S3`
- **credits** (`float`): `4.5`
- **vigent** (`str`): `S`
- **guia_docent_externa** (`str`): ``
- **nom** (`str`): `Constraint Processing and Programming`
- **guia_docent_url_publica** (`str`): `https://www.fib.upc.edu/en/studies/masters/master-artificial-intelligence/curriculum/syllabus/CPP-MAI`

### Additional Sample Records

#### Record 2

```json
{
  "id": "APC",
  "url": "https://api.fib.upc.edu/v2/assignatures/APC/",
  "guia": "https://api.fib.upc.edu/v2/assignatures/APC/guia/",
  "obligatorietats": [
    {
      "codi_oblig": "OPT",
      "codi_especialitat": "",
      "pla": "GRAU",
      "nom_especialitat": ""
    }
  ],
  "plans": [
    "GRAU",
    "GCED"
  ],
  "lang": {
    "Q1": [],
    "Q2": []
  },
  "quadrimestres": [],
  "sigles": "APC",
  "codi_upc": "270160",
  "semestre": "S5",
  "credits": 6.0,
  "vigent": "S",
  "guia_docent_externa": "",
  "nom": "PC Architecture",
  "guia_docent_url_publica": "https://www.fib.upc.edu/en/studies/bachelors-degrees/bachelor-degree-informatics-engineering/curriculum/syllabus/APC"
}
```

#### Record 3

```json
{
  "id": "ASDP",
  "url": "https://api.fib.upc.edu/v2/assignatures/ASDP/",
  "guia": "https://api.fib.upc.edu/v2/assignatures/ASDP/guia/",
  "obligatorietats": [
    {
      "codi_oblig": "OPT",
      "codi_especialitat": "",
      "pla": "GIA",
      "nom_especialitat": ""
    },
    {
      "codi_oblig": "OPT",
      "codi_especialitat": "",
      "pla": "GRAU",
      "nom_especialitat": ""
    }
  ],
  "plans": [
    "GRAU",
    "GCED",
    "GIA"
  ],
  "lang": {
    "Q1": [
      "English"
    ],
    "Q2": [
      "English"
    ]
  },
  "quadrimestres": [
    "Q1",
    "Q2"
  ],
  "sigles": "ASDP",
  "codi_upc": "270190",
  "semestre": "S5",
  "credits": 6.0,
  "vigent": "S",
  "guia_docent_externa": "",
  "nom": "Academic Skills for Developing a Project",
  "guia_docent_url_publica": "https://www.fib.upc.edu/en/studies/bachelors-degrees/bachelor-degree-informatics-engineering/curriculum/syllabus/ASDP"
}
```

#### Record 4

```json
{
  "id": "AP3-BBI",
  "url": "https://api.fib.upc.edu/v2/assignatures/AP3-BBI/",
  "guia": "https://api.fib.upc.edu/v2/assignatures/AP3-BBI/guia/",
  "obligatorietats": [
    {
      "codi_oblig": "OBL",
      "codi_especialitat": "",
      "pla": "BBI",
      "nom_especialitat": ""
    }
  ],
  "plans": [
    "BBI"
  ],
  "lang": {
    "Q1": [],
    "Q2": []
  },
  "quadrimestres": [
    "Q1"
  ],
  "sigles": "AP3-BBI",
  "codi_upc": "2703114",
  "semestre": "S3",
  "credits": 6.0,
  "vigent": "S",
  "guia_docent_externa": "",
  "nom": "Applied Programming III",
  "guia_docent_url_publica": "https://www.fib.upc.edu/en/studies/bachelors-degrees/bachelor-degree-bioinformatics/curriculum/syllabus/AP3-BBI"
}
```

## Usage Example

```python
import requests

url = "https://api.fib.upc.edu/v2/assignatures"
headers = {
    "client_id": "YOUR_CLIENT_ID",
    "Accept": "application/json",
    "Accept-Language": "en"
}
response = requests.get(url, headers=headers)
data = response.json()
```


---
*Generated on 2025-10-17 17:57:30*
