# Classroom information

**Endpoint**: `/v2/aules`

**Type**: Public (client_id only)

**Description**: Classroom information

## Response Structure

- **Pagination**: Yes
- **Count**: 62
- **Next**: None
- **Previous**: None
- **Results returned**: 62

### Sample Record (First Result)

```json
{
  "id": "**",
  "reserves": "https://api.fib.upc.edu/v2/aules/**/reserves/"
}
```

### Fields

- **id** (`str`): `**`
- **reserves** (`str`): `https://api.fib.upc.edu/v2/aules/**/reserves/`

### Additional Sample Records

#### Record 2

```json
{
  "id": "A1S101",
  "reserves": "https://api.fib.upc.edu/v2/aules/A1S101/reserves/"
}
```

#### Record 3

```json
{
  "id": "A4002",
  "reserves": "https://api.fib.upc.edu/v2/aules/A4002/reserves/"
}
```

#### Record 4

```json
{
  "id": "A5001",
  "reserves": "https://api.fib.upc.edu/v2/aules/A5001/reserves/"
}
```

## Usage Example

```python
import requests

url = "https://api.fib.upc.edu/v2/aules"
headers = {
    "client_id": "YOUR_CLIENT_ID",
    "Accept": "application/json",
    "Accept-Language": "en"
}
response = requests.get(url, headers=headers)
data = response.json()
```


---
*Generated on 2025-10-17 17:57:32*
