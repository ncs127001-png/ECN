import os
import json
import re
import hashlib
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import numpy as np
from pathlib import Path
from datetime import datetime

def sanitizar_nombre(nombre):
    """Limpia nombres de archivo para evitar caracteres problemáticos"""
    return re.sub(r'[\\/*?:"<>|]', "_", nombre)

def calcular_hash_imagen(datos_imagen):
    """Calcula un hash único para detectar imágenes duplicadas"""
    return hashlib.md5(datos_imagen).hexdigest()[:8]

def detectar_pdf_escaneado(ruta_pdf):
    """
    Detecta si un PDF es escaneado usando solo PyMuPDF (fitz).
    Devuelve: (es_escaneado, porcentaje_texto)
    """
    try:
        doc = fitz.open(ruta_pdf)
        total_paginas = len(doc)

        if total_paginas == 0:
            doc.close()
            return True, 0.0

        texto_total = 0
        for pagina in doc:
            texto = pagina.get_text("text")
            if texto:
                texto_total += len(texto)

        doc.close()

        chars_por_pagina = texto_total / total_paginas
        porcentaje_texto = min(100.0, (chars_por_pagina / 100.0) * 100.0)
        es_escaneado = chars_por_pagina < 50

        return es_escaneado, porcentaje_texto

    except Exception as e:
        print(f"⚠️ Error detectando tipo de PDF con fitz: {str(e)}")
        return True, 0.0

def aplicar_ocr_a_pagina(imagen_bytes):
    """
    Aplica OCR a una imagen usando Tesseract con configuración optimizada para documentos
    """
    try:
        img = Image.open(io.BytesIO(imagen_bytes))
        img = img.convert('L')
        img_array = np.array(img)
        umbral = np.mean(img_array) * 0.85
        img_array = (img_array > umbral) * 255
        img = Image.fromarray(img_array.astype('uint8'), 'L')
        config = r'--oem 3 --psm 6 -l spa+eng'
        texto = pytesseract.image_to_string(img, config=config)
        return texto.strip()
    except Exception as e:
        return f"[OCR FALLÓ: {str(e)}]"

def extraer_texto_pdf(ruta_pdf, carpeta_imagenes, contador_imagen_global, imagenes_procesadas):
    """
    Versión mejorada con:
    - Detección de PDFs escaneados + OCR automático (solo fitz)
    - Extracción de imágenes sin duplicados reales
    - Preservación de estructura de párrafos
    """
    texto = f"\n{'='*60}\n📄 DOCUMENTO: {os.path.basename(ruta_pdf)}\n{'='*60}\n\n"
    
    es_escaneado, porcentaje_texto = detectar_pdf_escaneado(ruta_pdf)
    if es_escaneado:
        texto += f"⚠️ PDF detectado como escaneado ({porcentaje_texto:.1f}% texto real)\n"
        texto += "🖼️ Aplicando OCR a las páginas...\n\n"
    
    try:
        doc = fitz.open(ruta_pdf)
        imagenes_encontradas = []
        
        for pagina_num, pagina in enumerate(doc, 1):
            texto_pagina = f"\n** PÁGINA {pagina_num} **\n\n"
            
            blocks = pagina.get_text("dict")["blocks"]
            parrafos = []
            ultimo_y = None
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        if line["spans"]:
                            y_pos = line["bbox"][1]
                            texto_linea = "".join(span["text"] for span in line["spans"])
                            
                            if ultimo_y is not None and (y_pos - ultimo_y) > 15:
                                parrafos.append("\n")
                            parrafos.append(texto_linea + "\n")
                            ultimo_y = y_pos
            
            texto_pagina += "".join(parrafos)
            
            if es_escaneado and not texto_pagina.strip().endswith(f"** PÁGINA {pagina_num} **"):
                try:
                    pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_bytes = pix.tobytes("jpeg", quality=85)
                    texto_ocr = aplicar_ocr_a_pagina(img_bytes)
                    
                    if texto_ocr and not texto_ocr.startswith("[OCR FALLÓ"):
                        texto_pagina += f"\n\n[OCR - PÁGINA {pagina_num}]\n{texto_ocr}\n"
                except Exception as e:
                    texto_pagina += f"\n[ERROR OCR: {str(e)}]\n"
            
            texto += texto_pagina
            
            imagenes = pagina.get_images(full=True)
            imagenes_procesadas_pagina = set()
            
            for img_index, img in enumerate(imagenes):
                try:
                    xref = img[0]
                    base_imagen = doc.extract_image(xref)
                    imagen_bytes = base_imagen["image"]
                    extension = base_imagen["ext"] or "png"
                    
                    hash_img = calcular_hash_imagen(imagen_bytes)
                    
                    if hash_img in imagenes_procesadas_pagina:
                        continue
                    if hash_img in imagenes_procesadas:
                        nombre_existente = imagenes_procesadas[hash_img]
                        texto += f"\n[IMAGEN REUTILIZADA (ya extraída): {nombre_existente}]\n"
                        continue
                    
                    contador_imagen_global += 1
                    nombre_seguro = sanitizar_nombre(os.path.basename(ruta_pdf))
                    nombre_archivo = f"{nombre_seguro}_p{pagina_num}_img{img_index+1}_{contador_imagen_global}.{extension}"
                    ruta_guardado = os.path.join(carpeta_imagenes, nombre_archivo)
                    
                    with open(ruta_guardado, "wb") as f:
                        f.write(imagen_bytes)
                    
                    imagenes_procesadas[hash_img] = nombre_archivo
                    imagenes_procesadas_pagina.add(hash_img)
                    imagenes_encontradas.append(nombre_archivo)
                    
                    texto += f"\n[IMAGEN EXTRAÍDA: {nombre_archivo}]\n"
                except Exception as e:
                    texto += f"\n⚠️ Error procesando imagen {img_index+1} en página {pagina_num}: {str(e)}\n"
        
        doc.close()
        return texto, imagenes_encontradas, contador_imagen_global
        
    except Exception as e:
        texto += f"\n⚠️ Error crítico procesando PDF: {str(e)}\n"
        return texto, [], contador_imagen_global

def procesar_txt(ruta_txt):
    nombre_archivo = os.path.basename(ruta_txt)
    texto = f"\n{'='*60}\n📄 TEXTO PLANO: {nombre_archivo}\n{'='*60}\n\n"
    try:
        with open(ruta_txt, 'r', encoding='utf-8') as f:
            contenido = f.read()
        texto += contenido + "\n"
    except Exception as e:
        texto += f"⚠️ Error leyendo archivo: {str(e)}\n"
    return texto

def procesar_json_conversacion(ruta_json):
    nombre_archivo = os.path.basename(ruta_json)
    texto = f"\n{'='*60}\n💬 CONVERSACIÓN: {nombre_archivo}\n{'='*60}\n\n"
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        if isinstance(datos, list) and all(isinstance(msg, dict) and 'role' in msg and 'content' in msg for msg in datos):
            for msg in datos:
                role = msg.get('role', '').upper()
                content = msg.get('content', '').strip()
                texto += f"{role}: {content}\n\n"
        elif 'messages' in datos and isinstance(datos['messages'], list):
            for msg in datos['messages']:
                sender = msg.get('sender', 'DESCONOCIDO')
                text = msg.get('text', '').strip()
                texto += f"{sender}: {text}\n\n"
        elif 'conversation' in datos and isinstance(datos['conversation'], list):
            for turno in datos['conversation']:
                speaker = turno.get('speaker', 'SPEAKER')
                text = turno.get('text', '').strip()
                texto += f"{speaker}: {text}\n\n"
        else:
            texto += "⚠️ Formato JSON no reconocido. Mostrando estructura:\n"
            texto += json.dumps(datos, indent=2, ensure_ascii=False)
    except Exception as e:
        texto += f"⚠️ Error procesando JSON: {str(e)}\n"
    return texto

def main():
    print("="*70)
    print("✨ COMPRENDIO INTELIGENTE v2.3 - Optimizado con PyMuPDF puro")
    print("="*70)
    
    dependencias = {
        "PyMuPDF": "fitz",
        "pytesseract": "pytesseract",
        "Pillow": "PIL"
    }
    
    faltantes = []
    for nombre, modulo in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(nombre)
    
    if faltantes:
        print(f"\n❌ Faltan las siguientes dependencias: {', '.join(faltantes)}")
        print("💡 Instalar con: pip install " + " ".join(faltantes))
        print("   Para pytesseract también necesitas: sudo apt install tesseract-ocr")
        print("   Y para idiomas españoles: sudo apt install tesseract-ocr-spa")
        return
    
    raiz = Path(__file__).parent.absolute()
    
    carpeta_origen = input("\n📁 Ruta de la carpeta con documentos (dejar en blanco para usar carpeta actual): ").strip()
    if not carpeta_origen:
        carpeta_origen = raiz
    else:
        carpeta_origen = Path(carpeta_origen)
    
    if not carpeta_origen.exists():
        print(f"\n❌ Error: La carpeta {carpeta_origen} no existe.")
        return
    
    carpeta_imagenes = raiz / "images"
    carpeta_imagenes.mkdir(exist_ok=True)
    
    archivo_salida = raiz / f"compendio_inteligente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    pdfs = list(carpeta_origen.rglob("*.pdf"))
    txts = list(carpeta_origen.rglob("*.txt"))
    jsons = list(carpeta_origen.rglob("*.json"))
    
    print(f"\n📊 Encontrados:")
    print(f"  • PDFs: {len(pdfs)}")
    print(f"  • TXTs: {len(txts)}")
    print(f"  • JSONs: {len(jsons)}")
    
    if not (pdfs or txts or jsons):
        print("\n❌ No se encontraron documentos para procesar.")
        return
    
    compendio_texto = f"COMPRENDIO INTELIGENTE - Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    compendio_texto += "="*70 + "\n\n"
    
    contador_imagen = 0
    total_imagenes = 0
    imagenes_procesadas = {}
    pdfs_escaneados = 0
    pdfs_con_texto = 0
    
    for pdf in sorted(pdfs):
        print(f"📄 Procesando PDF: {pdf.name}")
        es_escaneado, _ = detectar_pdf_escaneado(str(pdf))
        if es_escaneado:
            pdfs_escaneados += 1
            print("   🖼️  PDF escaneado detectado - se aplicará OCR")
        else:
            pdfs_con_texto += 1
        
        texto_extraido, imagenes, contador_imagen = extraer_texto_pdf(
            str(pdf), str(carpeta_imagenes), contador_imagen, imagenes_procesadas
        )
        compendio_texto += texto_extraido
        total_imagenes += len(imagenes)
    
    for txt in sorted(txts):
        print(f"📝 Procesando TXT: {txt.name}")
        compendio_texto += procesar_txt(str(txt))
    
    for json_file in sorted(jsons):
        print(f"💬 Procesando JSON: {json_file.name}")
        compendio_texto += procesar_json_conversacion(str(json_file))
    
    compendio_texto += f"\n{'='*70}\n✅ RESUMEN FINAL\n{'='*70}\n"
    compendio_texto += f"• PDFs procesados: {len(pdfs)}\n"
    compendio_texto += f"  - Con texto real: {pdfs_con_texto}\n"
    compendio_texto += f"  - Escaneados (con OCR): {pdfs_escaneados}\n"
    compendio_texto += f"• Archivos TXT incluidos: {len(txts)}\n"
    compendio_texto += f"• Conversaciones JSON procesadas: {len(jsons)}\n"
    compendio_texto += f"• Imágenes extraídas (únicas): {total_imagenes}\n"
    compendio_texto += f"• Imágenes detectadas como duplicadas: {len(imagenes_procesadas) - total_imagenes}\n"
    compendio_texto += f"\n✨ Carpeta de imágenes: {carpeta_imagenes.absolute()}\n"
    compendio_texto += f"✨ Archivo compendio: {archivo_salida.absolute()}\n"
    
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(compendio_texto)
    
    print(f"\n{'='*70}")
    print(f"🎉 ¡PROCESO COMPLETADO!")
    print(f"📄 Compendio guardado en: {archivo_salida.name}")
    print(f"🖼️ Imágenes extraídas (únicas) en: {carpeta_imagenes.name} ({total_imagenes} imágenes)")
    print(f"📊 PDFs escaneados procesados con OCR: {pdfs_escaneados}")
    print(f"💡 ¡Duplicados detectados y omitidos automáticamente!")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error crítico: {str(e)}")
        raise