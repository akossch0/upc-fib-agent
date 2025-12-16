"""Generate slide visuals for the presentation deck."""

import argparse
import json
import os
from pathlib import Path

import google.auth
from google import genai
from google.genai import types
from PIL import Image
from tqdm import tqdm

MODEL_NAME = "gemini-2.5-flash-image"
IMAGE_ASPECT_RATIO = "3:4"
PLACEHOLDER_SIZE = (1152, 1536)
PROMPTS_FILE = Path(__file__).with_name("prompts.json")
OUTPUT_DIR = Path(__file__).with_name("assets")


def load_prompts() -> list[dict[str, str]]:
    with PROMPTS_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_image(part: types.Part, destination: Path) -> None:
    image = part.as_image()
    image.save(destination)


def placeholder_color(identifier: str) -> tuple[int, int, int]:
    seed = sum(ord(char) for char in identifier) % 255
    return (50 + seed % 150, 80 + (seed * 3) % 120, 110 + (seed * 5) % 100)


def create_placeholder(identifier: str) -> None:
    destination = OUTPUT_DIR / f"{identifier}.png"
    image = Image.new("RGB", PLACEHOLDER_SIZE, placeholder_color(identifier))
    image.save(destination)


def generate_image(client: genai.Client, identifier: str, prompt: str) -> None:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt],
        config=types.GenerateContentConfig(image_config=types.ImageConfig(aspect_ratio=IMAGE_ASPECT_RATIO)),
    )
    for part in response.parts:
        if part.inline_data is not None:
            save_image(part, OUTPUT_DIR / f"{identifier}.png")
            return
    print(f"[warn] No image payload in response for {identifier}; creating placeholder")
    create_placeholder(identifier)


def build_client() -> genai.Client:
    # Remove API-key variables so the SDK does not attempt API-key auth.
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("GOOGLE_API_KEY", None)

    credentials, detected_project = google.auth.default()
    project = os.environ.get("VERTEX_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT") or detected_project
    if not project:
        raise RuntimeError("Unable to determine Vertex AI project. Set VERTEX_PROJECT or GOOGLE_CLOUD_PROJECT.")
    location = os.environ.get("VERTEX_LOCATION") or os.environ.get("GOOGLE_CLOUD_REGION") or os.environ.get("CLOUD_ML_REGION") or "us-central1"
    return genai.Client(
        vertexai={"project": project, "location": location},
        credentials=credentials,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate slide visuals for the presentation.")
    parser.add_argument(
        "ids",
        nargs="*",
        help="Specific image IDs to generate (e.g., s08_prompts s12_lessons). If omitted, generates all.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = build_client()
    ensure_output_dir()

    prompts = load_prompts()
    if args.ids:
        filter_set = set(args.ids)
        prompts = [p for p in prompts if p["id"] in filter_set]
        if not prompts:
            print(f"[error] No matching IDs found. Available: {[p['id'] for p in load_prompts()]}")
            return

    for entry in tqdm(prompts):
        identifier = entry["id"]
        prompt = entry["prompt"]
        try:
            generate_image(client, identifier, prompt)
        except Exception as error:  # pragma: no cover
            print(f"[warn] {identifier}: {error}; creating placeholder image.")
            create_placeholder(identifier)


if __name__ == "__main__":
    main()
