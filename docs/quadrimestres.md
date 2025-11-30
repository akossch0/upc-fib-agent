# Academic terms/semesters

**Endpoint**: `/v2/quadrimestres`

**Type**: Public (client_id only)

**Description**: Academic terms/semesters

## Response Structure

- **Pagination**: Yes
- **Count**: 21
- **Next**: None
- **Previous**: None
- **Results returned**: 21

### Sample Record (First Result)

```json
{
  "id": "2015Q1",
  "url": "https://api.fib.upc.edu/v2/quadrimestres/2015Q1/",
  "actual": "N",
  "actual_horaris": "N",
  "classes": "https://api.fib.upc.edu/v2/quadrimestres/2015Q1/classes/",
  "examens": "https://api.fib.upc.edu/v2/quadrimestres/2015Q1/examens/",
  "assignatures": "https://api.fib.upc.edu/v2/quadrimestres/2015Q1/assignatures/"
}
```

### Fields

- **id** (`str`): `2015Q1`
- **url** (`str`): `https://api.fib.upc.edu/v2/quadrimestres/2015Q1/`
- **actual** (`str`): `N`
- **actual_horaris** (`str`): `N`
- **classes** (`str`): `https://api.fib.upc.edu/v2/quadrimestres/2015Q1/classes/`
- **examens** (`str`): `https://api.fib.upc.edu/v2/quadrimestres/2015Q1/examens/`
- **assignatures** (`str`): `https://api.fib.upc.edu/v2/quadrimestres/2015Q1/assignatures/`

### Additional Sample Records

#### Record 2

```json
{
  "id": "2015Q2",
  "url": "https://api.fib.upc.edu/v2/quadrimestres/2015Q2/",
  "actual": "N",
  "actual_horaris": "N",
  "classes": "https://api.fib.upc.edu/v2/quadrimestres/2015Q2/classes/",
  "examens": "https://api.fib.upc.edu/v2/quadrimestres/2015Q2/examens/",
  "assignatures": "https://api.fib.upc.edu/v2/quadrimestres/2015Q2/assignatures/"
}
```

#### Record 3

```json
{
  "id": "2016Q2",
  "url": "https://api.fib.upc.edu/v2/quadrimestres/2016Q2/",
  "actual": "N",
  "actual_horaris": "N",
  "classes": "https://api.fib.upc.edu/v2/quadrimestres/2016Q2/classes/",
  "examens": "https://api.fib.upc.edu/v2/quadrimestres/2016Q2/examens/",
  "assignatures": "https://api.fib.upc.edu/v2/quadrimestres/2016Q2/assignatures/"
}
```

#### Record 4

```json
{
  "id": "2017Q1",
  "url": "https://api.fib.upc.edu/v2/quadrimestres/2017Q1/",
  "actual": "N",
  "actual_horaris": "N",
  "classes": "https://api.fib.upc.edu/v2/quadrimestres/2017Q1/classes/",
  "examens": "https://api.fib.upc.edu/v2/quadrimestres/2017Q1/examens/",
  "assignatures": "https://api.fib.upc.edu/v2/quadrimestres/2017Q1/assignatures/"
}
```

## Usage Example

```python
import requests

url = "https://api.fib.upc.edu/v2/quadrimestres"
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
