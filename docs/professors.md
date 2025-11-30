# Professor directory

**Endpoint**: `/v2/professors`

**Type**: Public (client_id only)

**Description**: Professor directory

## Response Structure

- **Format**: List (direct array response)
- **Total items**: 520

### Sample Record (First Item)

```json
{
  "id": 210312,
  "assignatures": [
    "FINE-MIRI"
  ],
  "plans_estudi": [
    "MIRI"
  ],
  "especialitats": [
    "MIRI-CNDS"
  ],
  "obfuscated_email": "abadal(at)ac.upc.edu",
  "nom": "Sergi",
  "cognoms": "Abadal Cavallé",
  "departament": "AC",
  "futur_url": "https://futur.upc.edu/1069516",
  "apren_url": "https://apren.upc.edu/ca/professorat/1069516"
}
```

### Fields

- **id** (`int`): `210312`
- **assignatures** (`list[str]`): ['FINE-MIRI']
- **plans_estudi** (`list[str]`): ['MIRI']
- **especialitats** (`list[str]`): ['MIRI-CNDS']
- **obfuscated_email** (`str`): `abadal(at)ac.upc.edu`
- **nom** (`str`): `Sergi`
- **cognoms** (`str`): `Abadal Cavallé`
- **departament** (`str`): `AC`
- **futur_url** (`str`): `https://futur.upc.edu/1069516`
- **apren_url** (`str`): `https://apren.upc.edu/ca/professorat/1069516`

### Additional Sample Records

#### Record 2

```json
{
  "id": 431,
  "assignatures": [
    "DBD",
    "BDA-GCED"
  ],
  "plans_estudi": [
    "GCED",
    "GRAU"
  ],
  "especialitats": [
    "ENGSOFT"
  ],
  "obfuscated_email": "alberto.abello(at)upc.edu",
  "nom": "Alberto",
  "cognoms": "Abello Gamazo",
  "departament": "ESSI",
  "futur_url": "https://futur.upc.edu/1003711",
  "apren_url": "https://apren.upc.edu/ca/professorat/1003711"
}
```

#### Record 3

```json
{
  "id": 212885,
  "assignatures": [
    "CG-BBI"
  ],
  "plans_estudi": [
    "BBI"
  ],
  "especialitats": [],
  "obfuscated_email": "jabril(at)ub.edu",
  "nom": "Josep Francesc",
  "cognoms": "Abril Ferrando",
  "departament": "UB",
  "futur_url": "",
  "apren_url": ""
}
```

#### Record 4

```json
{
  "id": 210381,
  "assignatures": [
    "MVA-MDS",
    "SMDE-MIRI",
    "AD-GCED"
  ],
  "plans_estudi": [
    "MDS",
    "MIRI",
    "GCED"
  ],
  "especialitats": [],
  "obfuscated_email": "nihan.acar.denizli(at)upc.edu",
  "nom": "Nihan",
  "cognoms": "Acar Denizli",
  "departament": "EIO",
  "futur_url": "https://futur.upc.edu/1255830",
  "apren_url": ""
}
```

## Usage Example

```python
import requests

url = "https://api.fib.upc.edu/v2/professors"
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
