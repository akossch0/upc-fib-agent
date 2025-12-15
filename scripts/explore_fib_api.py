"""Temporary script to explore FIB API and fetch sample data for evaluation dataset creation."""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.fib.upc.edu/v2"
CLIENT_ID = os.environ.get("FIB_CLIENT_ID")

ENDPOINTS = [
    {"name": "assignatures", "path": "assignatures", "description": "Course/subject catalog"},
    {"name": "quadrimestres", "path": "quadrimestres", "description": "Academic terms/semesters"},
    {"name": "examens", "path": "examens", "description": "Exam schedules"},
    {"name": "noticies", "path": "noticies", "description": "News and announcements"},
    {"name": "aules", "path": "aules", "description": "Classroom information"},
    {"name": "professors", "path": "professors", "description": "Professor directory"},
]


def fetch_endpoint(path: str, params: dict | None = None) -> dict | list:
    """Fetch data from FIB API endpoint."""
    headers = {
        "client_id": CLIENT_ID,
        "Accept": "application/json",
        "Accept-Language": "en",
    }
    url = f"{BASE_URL}/{path}"
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_all_paginated(path: str) -> list:
    """Fetch all pages of a paginated endpoint."""
    all_results = []
    page = 1
    while True:
        data = fetch_endpoint(path, {"page": page})
        if isinstance(data, dict) and "results" in data:
            all_results.extend(data["results"])
            if not data.get("next"):
                break
            page += 1
        else:
            return data if isinstance(data, list) else [data]
    return all_results


def main():
    if not CLIENT_ID:
        print("Error: FIB_CLIENT_ID not found in environment variables")
        return

    output_dir = Path(__file__).parent / "api_data"
    output_dir.mkdir(exist_ok=True)

    print(f"Using Client ID: {CLIENT_ID[:20]}...")
    print("=" * 70)

    for endpoint in ENDPOINTS:
        name = endpoint["name"]
        path = endpoint["path"]
        print(f"\nFetching {name}...")

        try:
            data = fetch_all_paginated(path)
            output_file = output_dir / f"{name}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  ✅ Saved {len(data)} records to {output_file}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n" + "=" * 70)
    print("Exploration complete!")
    print(f"Data saved to: {output_dir}")

    print("\n\nSample data summary:")
    print("-" * 70)

    courses_file = output_dir / "assignatures.json"
    if courses_file.exists():
        with open(courses_file) as f:
            courses = json.load(f)
        print(f"\nCourses ({len(courses)} total):")
        for course in courses[:5]:
            print(f"  - {course['id']}: {course['nom']} ({course['credits']} credits)")

    professors_file = output_dir / "professors.json"
    if professors_file.exists():
        with open(professors_file) as f:
            professors = json.load(f)
        print(f"\nProfessors ({len(professors)} total):")
        for prof in professors[:5]:
            print(f"  - {prof['nom']} {prof['cognoms']} ({prof['departament']})")

    examens_file = output_dir / "examens.json"
    if examens_file.exists():
        with open(examens_file) as f:
            examens = json.load(f)
        print(f"\nExams ({len(examens)} total):")
        for exam in examens[:5]:
            print(f"  - {exam['assig']}: {exam['inici']} in {exam['aules']}")


if __name__ == "__main__":
    main()
