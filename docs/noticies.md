# News and announcements

**Endpoint**: `/v2/noticies`

**Type**: Public (client_id only)

**Description**: News and announcements

## Response Structure

- **Pagination**: Yes
- **Count**: 5
- **Next**: None
- **Previous**: None
- **Results returned**: 5

### Sample Record (First Result)

```json
{
  "titol": "The FIB inaugurates the 2025-2026 academic year",
  "link": "https://www.fib.upc.edu/en/news/fib-inaugurates-2025-2026-academic-year",
  "descripcio": "<div class=\"field field-name-body field-type-text-with-summary field-label-hidden\"><div class=\"field-items\"><div class=\"field-item even\">Last Wednesday, 15th of October 15, the Vèrtex building at UPC was the setting for the official inauguration ceremony of the 2025-2026 academic year at the FIB.</div></div></div><div class=\"field field-name-field-imatge field-type-image field-label-hidden\"><div class=\"field-items\"><div class=\"field-item even\"><img alt=\"\" height=\"225\" src=\"https://www.fib.upc.edu/sites/fib/files/styles/imatge_pantalles/public/aa_inauguracio_curs_25-26_inici.jpg?itok=pMXzlYBx\" width=\"400\" /></div></div></div>",
  "data_publicacio": "2025-10-17T13:52:08"
}
```

### Fields

- **titol** (`str`): `The FIB inaugurates the 2025-2026 academic year`
- **link** (`str`): `https://www.fib.upc.edu/en/news/fib-inaugurates-2025-2026-academic-year`
- **descripcio** (`str`): `<div class="field field-name-body field-type-text-with-summary field-label-hidden"><div class="field-items"><div class="field-item even">Last Wednesda...`
- **data_publicacio** (`str`): `2025-10-17T13:52:08`

### Additional Sample Records

#### Record 2

```json
{
  "titol": "Festibity Day 2025",
  "link": "https://www.fib.upc.edu/en/news/festibity-day-2025",
  "descripcio": "<div class=\"field field-name-body field-type-text-with-summary field-label-hidden\"><div class=\"field-items\"><div class=\"field-item even\"><p>Get ready for Festibity Day 2025: connect with companies and boost your professional future</p></div></div></div><div class=\"field field-name-field-imatge field-type-image field-label-hidden\"><div class=\"field-items\"><div class=\"field-item even\"><img alt=\"\" height=\"163\" src=\"https://www.fib.upc.edu/sites/fib/files/styles/imatge_pantalles/public/banner_festibity_day_butlleti.jpg?itok=3craQjmO\" width=\"400\" /></div></div></div>",
  "data_publicacio": "2025-10-10T09:24:21"
}
```

#### Record 3

```json
{
  "titol": "Pre-enrolment to official FIB Master’s is now open 2025-2026",
  "link": "https://www.fib.upc.edu/en/news/pre-enrolment-official-fib-masters-now-open-2025-2026",
  "descripcio": "<div class=\"field field-name-body field-type-text-with-summary field-label-hidden\"><div class=\"field-items\"><div class=\"field-item even\">Pre-enrolment to official Master’s organized by Barcelona School of Informatics is now open. The courses will start in February for the Spring semester of 2025-2026.</div></div></div><div class=\"field field-name-field-imatge field-type-image field-label-hidden\"><div class=\"field-items\"><div class=\"field-item even\"><img alt=\"\" height=\"200\" src=\"https://www.fib.upc.edu/sites/fib/files/styles/imatge_pantalles/public/images/fib/mastersoficialswebportada.png?itok=Bflp49QE\" width=\"400\" /></div></div></div>",
  "data_publicacio": "2025-10-06T10:59:28"
}
```

#### Record 4

```json
{
  "titol": "BSC Earth Sciences - Open Day, 2025",
  "link": "https://www.fib.upc.edu/en/news/bsc-earth-sciences-open-day-2025",
  "descripcio": "<div class=\"field field-name-body field-type-text-with-summary field-label-hidden\"><div class=\"field-items\"><div class=\"field-item even\">Explore the future of Earth Sciences alongside women and gender-diverse researchers in a morning of talks, networking, and cutting-edge technology at the BSC.</div></div></div><div class=\"field field-name-field-imatge field-type-image field-label-hidden\"><div class=\"field-items\"><div class=\"field-item even\"><img alt=\"\" height=\"225\" src=\"https://www.fib.upc.edu/sites/fib/files/styles/imatge_pantalles/public/discover_the_reaserch_done_by_women_and_dissident_identities_in_atmospheric_composition_climate_variability_health_resilience_computational_earth_sciences_and_climate_services_learn_about_car_1_1.png?itok=cceAFGz9\" width=\"400\" /></div></div></div>",
  "data_publicacio": "2025-10-03T11:01:59"
}
```

## Usage Example

```python
import requests

url = "https://api.fib.upc.edu/v2/noticies"
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
