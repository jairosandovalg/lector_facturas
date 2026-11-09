import tempfile
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Extractor de Facturas", layout="wide")

st.title("Extractor de Facturas Web a BI")
st.markdown("Sube tus archivos PDF. Playwright interactuará con la web en segundo plano y te devolverá la tabla consolidada.")

# Subida interactiva de múltiples facturas
archivos_subidos = st.file_uploader(
    "Selecciona tus facturas PDF",
    type=["pdf"],
    accept_multiple_files=True
)

def procesar_con_playwright(rutas_temporales):
    registros = []
    
    # headless=True es INDISPENSABLE para Streamlit
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # URL de la web donde cargas los PDFs
        page.goto("https://tu-plataforma-web.com/subir-factura")

        for ruta_pdf in rutas_temporales:
            nombre_archivo = Path(ruta_pdf).name

            # 1. Cargar el PDF al input
            page.locator("input[type='file']").set_input_files(ruta_pdf)

            # 2. Si la web tiene botón de acción, descomenta:
            # page.locator("button#btn-procesar").click()

            # 3. Esperar que aparezca la tabla
            page.wait_for_selector("table tbody tr", timeout=20000)

            # 4. Extraer filas
            filas = page.locator("table tbody tr").all()
            for fila in filas:
                celdas = fila.locator("td").all_text_contents()
                if not celdas:
                    continue

                registros.append({
                    "Archivo": nombre_archivo,
                    "Columna_1": celdas[0].strip() if len(celdas) > 0 else "",
                    "Columna_2": celdas[1].strip() if len(celdas) > 1 else "",
                    "Columna_3": celdas[2].strip() if len(celdas) > 2 else "",
                    "Columna_4": celdas[3].strip() if len(celdas) > 3 else "",
                    "Columna_5": celdas[4].strip() if len(celdas) > 4 else "",
                })

        browser.close()
    
    return pd.DataFrame(registros)

# Botón de ejecución
if archivos_subidos:
    st.info(f"{len(archivos_subidos)} factura(s) cargada(s).")
    
    if st.button("Procesar Facturas y Extraer Tabla"):
        with st.spinner("Playwright está procesando los documentos..."):
            rutas_temporales = []
            
            # Guardar archivos subidos en una carpeta temporal para que Playwright los pueda leer
            with tempfile.TemporaryDirectory() as temp_dir:
                for archivo in archivos_subidos:
                    ruta_archivo = os.path.join(temp_dir, archivo.name)
                    with open(ruta_archivo, "wb") as f:
                        f.write(archivo.getbuffer())
                    rutas_temporales.append(ruta_archivo)

                # Ejecución de Playwright
                try:
                    df_resultado = procesar_con_playwright(rutas_temporales)
                    
                    if not df_resultado.empty:
                        st.success(f"Se extrajeron {len(df_resultado)} filas con éxito.")
                        
                        # Mostrar la tabla en el dashboard
                        st.dataframe(df_resultado, use_container_width=True)
                        
                        # Botón para descargar el CSV listo para Power BI
                        csv_data = df_resultado.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
                        st.download_button(
                            label="Descargar CSV para Power BI",
                            data=csv_data,
                            file_name="tabla_bi_facturas.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No se detectaron registros en las tablas de la página.")
                except Exception as e:
                    st.error(f"Ocurrió un error en la ejecución: {e}")
