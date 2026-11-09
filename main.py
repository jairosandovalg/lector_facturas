import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pandas as pd
import streamlit as st

# ==============================================================================
# 1. INSTALACIÓN AUTOMÁTICA DEL NAVEGADOR EN EL SERVIDOR (STREAMLIT CLOUD)
# ==============================================================================
@st.cache_resource(show_spinner="Preparando el entorno del navegador...")
def inicializar_entorno_playwright():
    """Descarga los binarios de Chromium si no existen en la máquina/servidor."""
    try:
        resultado = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Playwright Chromium instalado correctamente:", resultado.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar Playwright: {e.stderr}")
        st.warning("No se pudo autoinstalar Chromium vía subprocess. Si falla el lanzamiento, revisa packages.txt.")

# Ejecutar la verificación e instalación al cargar la aplicación
inicializar_entorno_playwright()

# Importar sync_playwright después de asegurar la instalación
from playwright.sync_api import sync_playwright

# ==============================================================================
# 2. CONFIGURACIÓN DE LA INTERFAZ STREAMLIT
# ==============================================================================
st.set_page_config(page_title="Extractor de Facturas a BI", layout="wide")

st.title("📊 Extractor de Facturas PDF a Tabla BI")
st.markdown(
    "Sube tus archivos PDF. Playwright interactuará en segundo plano con el navegador para "
    "procesarlos y consolidar los datos en una tabla lista para Power BI o Looker Studio."
)

archivos_subidos = st.file_uploader(
    "Selecciona o arrastra una o varias facturas PDF",
    type=["pdf"],
    accept_multiple_files=True
)

# ==============================================================================
# 3. LÓGICA DE EXTRACCIÓN CON PLAYWRIGHT
# ==============================================================================
def procesar_con_playwright(rutas_temporales):
    registros = []

    with sync_playwright() as p:
        # Modo headless=True obligatorio en Streamlit Cloud
        # args con --no-sandbox y --disable-gpu garantizan estabilidad en contenedores Linux
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"]
        )
        page = browser.new_page()

        # URL del portal o herramienta web donde subes los PDFs
        # page.goto("https://tu-plataforma-web.com/subir-factura")

        for ruta_pdf in rutas_temporales:
            nombre_archivo = Path(ruta_pdf).name

            # ------------------------------------------------------------------
            # Adapta estos selectores a tu flujo web real:
            # ------------------------------------------------------------------
            # 1. Cargar el PDF:
            # page.locator("input[type='file']").set_input_files(ruta_pdf)

            # 2. Si la web tiene un botón de procesamiento:
            # page.locator("button#btn-procesar").click()

            # 3. Esperar que se renderice la tabla:
            # page.wait_for_selector("table tbody tr", timeout=20000)

            # 4. Extraer celdas de la tabla generada:
            # filas = page.locator("table tbody tr").all()
            # for fila in filas:
            #     celdas = fila.locator("td").all_text_contents()
            #     if celdas:
            #         registros.append({
            #             "Archivo": nombre_archivo,
            #             "Columna_1": celdas[0].strip() if len(celdas) > 0 else "",
            #             "Columna_2": celdas[1].strip() if len(celdas) > 1 else "",
            #             "Columna_3": celdas[2].strip() if len(celdas) > 2 else "",
            #             "Columna_4": celdas[3].strip() if len(celdas) > 3 else "",
            #         })

            # Datos de muestra estructurados mientras configuras tus selectores web:
            registros.append({
                "Archivo": nombre_archivo,
                "Serie_Numero": "E001-16",
                "Fecha_Emision": "2017-10-10",
                "RUC_Cliente": "10468861611",
                "Cliente": "MOLINA ZAMBRANO KEVIN HARNOLD",
                "Descripcion": "SACOS DE ARROZ TONDERITO X 50 KILOS",
                "Cantidad": 10.0,
                "Valor_Unitario": 130.5085,
                "Total_Linea": 1305.09
            })

        browser.close()

    return pd.DataFrame(registros)

# ==============================================================================
# 4. ACCIÓN Y DESCARGA
# ==============================================================================
if archivos_subidos:
    st.info(f"{len(archivos_subidos)} archivo(s) listo(s) para procesar.")

    if st.button("🚀 Iniciar Extracción y Generar Tabla"):
        with st.spinner("Procesando con Playwright en segundo plano..."):
            rutas_temporales = []

            # Guardar archivos en un directorio temporal para que Playwright los pueda leer
            with tempfile.TemporaryDirectory() as carpeta_temp:
                for archivo in archivos_subidos:
                    ruta_temp = os.path.join(carpeta_temp, archivo.name)
                    with open(ruta_temp, "wb") as f:
                        f.write(archivo.getbuffer())
                    rutas_temporales.append(ruta_temp)

                try:
                    df_resultado = procesar_con_playwright(rutas_temporales)

                    if not df_resultado.empty:
                        st.success(f"Se extrajeron {len(df_resultado)} filas con éxito.")

                        # Mostrar métricas rápidas
                        col1, col2 = st.columns(2)
                        col1.metric("Archivos procesados", len(df_resultado["Archivo"].unique()))
                        if "Total_Linea" in df_resultado.columns:
                            col2.metric("Monto Total", f"S/ {df_resultado['Total_Linea'].sum():,.2f}")

                        # Vista previa de la tabla
                        st.dataframe(df_resultado, use_container_width=True)

                        # Botón para descargar el CSV listo para BI
                        csv_data = df_resultado.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
                        st.download_button(
                            label="📥 Descargar CSV para Power BI",
                            data=csv_data,
                            file_name="tabla_bi_facturas.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No se extrajeron registros de las tablas.")

                except Exception as error:
                    st.error(f"Ocurrió un error en la ejecución: {error}")
