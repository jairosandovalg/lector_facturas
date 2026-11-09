import glob
import os
from pathlib import Path
import pandas as pd
from playwright.sync_api import sync_playwright

CARPETA_PDFS = "facturas"        # Carpeta local con tus PDFs
CSV_SALIDA = "tabla_bi_desde_web.csv"

def procesar_facturas_en_web():
    archivos_pdf = glob.glob(os.path.join(CARPETA_PDFS, "*.pdf"))
    if not archivos_pdf:
        print(f"No se encontraron archivos PDF en la carpeta '{CARPETA_PDFS}'.")
        return

    registros_totales = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # False para ver cómo interactúa
        page = browser.new_page()

        # URL de la web/herramienta donde cargas las facturas
        page.goto("https://tu-plataforma-web.com/subir-factura")

        for ruta_pdf in archivos_pdf:
            ruta_absoluta = str(Path(ruta_pdf).resolve())
            nombre_archivo = os.path.basename(ruta_pdf)
            print(f"Cargando: {nombre_archivo}...")

            # 1. Cargar el archivo PDF en el input file
            # Ajusta el selector '#input-archivo' al id o clase real del input en tu web
            page.locator("input[type='file']").set_input_files(ruta_absoluta)

            # 2. Si la web tiene un botón de "Procesar" o "Subir", haz clic:
            # page.locator("button#btn-procesar").click()

            # 3. Esperar a que la tabla aparezca en pantalla
            # Ajusta el selector '.tabla-resultados' o 'table tbody tr' según la web
            page.wait_for_selector("table tbody tr", timeout=15000)

            # 4. Extraer filas de la tabla generada en la página
            filas = page.locator("table tbody tr").all()

            for fila in filas:
                celdas = fila.locator("td").all_text_contents()
                if not celdas:
                    continue

                # Ejemplo mapeando celdas típicas (ajustar según columnas de tu web)
                # [0: Cantidad, 1: Unidad, 2: Descripción, 3: P. Unitario, 4: Total]
                registros_totales.append({
                    "Archivo": nombre_archivo,
                    "Columna_1": celdas[0].strip() if len(celdas) > 0 else "",
                    "Columna_2": celdas[1].strip() if len(celdas) > 1 else "",
                    "Columna_3": celdas[2].strip() if len(celdas) > 2 else "",
                    "Columna_4": celdas[3].strip() if len(celdas) > 3 else "",
                    "Columna_5": celdas[4].strip() if len(celdas) > 4 else "",
                })

        browser.close()

    # 5. Guardar todo en una tabla para Power BI / Looker Studio
    if registros_totales:
        df = pd.DataFrame(registros_totales)
        df.to_csv(CSV_SALIDA, index=False, encoding="utf-8-sig")
        print(f"\nProceso finalizado. Se extrajeron {len(df)} registros en '{CSV_SALIDA}'.")
    else:
        print("No se extrajeron registros de las tablas web.")

if __name__ == "__main__":
    procesar_facturas_en_web()
