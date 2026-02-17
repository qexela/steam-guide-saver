#!/bin/bash
# ============================================
# Steam Guide Saver — Cleanup
# Запуск: chmod +x scripts/clean.sh && ./scripts/clean.sh
# ============================================

# Переходим в корень проекта
cd "$(dirname "$0")/.."

echo "=== Steam Guide Saver — Cleanup ==="
echo "Working dir: $(pwd)"
echo ""

for dir in build __pycache__ dist; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo "  Deleted: $dir/"
    else
        echo "  Skip:    $dir/"
    fi
done

for file in *.spec downloader.log; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  Deleted: $file"
    else
        echo "  Skip:    $file"
    fi
done

echo ""
echo "=== Done! ==="