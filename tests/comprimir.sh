#!/bin/bash

# Recorre todos los archivos .mp4 del directorio actual
for file in *.mp4; do
    # Quita la extensión para obtener el nombre base
    name="${file%.mp4}"

    echo "⏳ Comprimiendo: $file"

    ffmpeg -i "$file" \
        -c:v libx264 -crf 28 \
        -c:a aac -b:a 128k \
        "COMP_${name}.mp4"

    echo "✔ Listo: COMP_${name}.mp4"
    echo
done

echo "✨ Proceso terminado ✨"

