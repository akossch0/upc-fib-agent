#!/usr/bin/env bash
set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${script_dir}"

output_pdf="slides.pdf"
tex_file="slides.tex"

if ! command -v pdflatex >/dev/null 2>&1; then
  echo "Error: pdflatex not found. Install TeX Live with beamer support." >&2
  exit 1
fi

echo "Building ${tex_file}..."
pdflatex -interaction=nonstopmode "${tex_file}" >/dev/null 2>&1 || true
pdflatex -interaction=nonstopmode "${tex_file}" >/dev/null 2>&1 || true

if [[ -f "${output_pdf}" ]]; then
  echo "Rendered ${output_pdf}"
else
  echo "Error: Failed to generate ${output_pdf}" >&2
  exit 1
fi

# Clean auxiliary files
rm -f *.aux *.log *.nav *.out *.snm *.toc

