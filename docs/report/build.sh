#!/bin/bash
# LaTeX Report Build Script
# Requirements: TeX Live (or MiKTeX) with latexmk and biber

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BUILD_DIR="build"
MAIN_TEX="main.tex"

usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build    Build the PDF (default)"
    echo "  watch    Build and watch for changes (continuous preview)"
    echo "  clean    Remove build artifacts"
    echo "  help     Show this help message"
}

build() {
    echo "Building PDF..."
    mkdir -p "$BUILD_DIR"
    latexmk -pdf -interaction=nonstopmode -output-directory="$BUILD_DIR" "$MAIN_TEX"
    echo "Done! Output: $BUILD_DIR/main.pdf"
}

watch() {
    echo "Starting continuous build (press Ctrl+C to stop)..."
    mkdir -p "$BUILD_DIR"
    latexmk -pdf -pvc -interaction=nonstopmode -output-directory="$BUILD_DIR" "$MAIN_TEX"
}

clean() {
    echo "Cleaning build artifacts..."
    rm -rf "$BUILD_DIR"
    latexmk -C
    echo "Done!"
}

case "${1:-build}" in
    build)
        build
        ;;
    watch)
        watch
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo "Unknown command: $1"
        usage
        exit 1
        ;;
esac
