import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# Definir rutas absolutas
BASE_DIR = Path(__file__).parent
DIR_SUBIDAS = BASE_DIR / "subidas"
DIR_DESCARGAS = BASE_DIR / "descargas"

# Asegurar que las carpetas existan
DIR_SUBIDAS.mkdir(parents=True, exist_ok=True)
DIR_DESCARGAS.mkdir(parents=True, exist_ok=True)

PDF_A_SUBIR = DIR_SUBIDAS / "factura_input.pdf"

def ejecutar_flujo():
    with sync_playwright() as p:
        # Lanzar el navegador
        browser = p.chromium.launch(headless=False)  # Cambia a True en producción
        
        # 1. Configuración clave: permitir descargas en el contexto
        context = browser.new_context(
            accept_downloads=True
        )
        
        page = context.new_page()

        # ------------------------------------------------------------------
        # CASO A: Insertar / Subir archivo PDF
        # ------------------------------------------------------------------
        # Reemplaza con la URL de tu aplicación
        # page.goto("https://tu-sistema.com/cargar-factura")

        # Localizador del input de tipo archivo
        # page.locator("input[type='file']").set_input_files(str(PDF_A_SUBIR))
        print(f"Ruta preparada para subir: {PDF_A_SUBIR}")

        # ------------------------------------------------------------------
        # CASO B: Descargar archivo PDF para uso posterior
        # ------------------------------------------------------------------
        # Reemplaza con la página donde se genera la descarga
        # page.goto("https://tu-sistema.com/reportes")

        # Escuchar el evento de descarga antes de hacer clic en el botón
        # with page.expect_download() as download_info:
        #     # Clic en el botón o enlace que inicia la descarga del PDF
        #     page.locator("button#btn-descargar-pdf").click()

        # download = download_info.value

        # Definir la ruta final donde quedará el archivo
        # ruta_final_pdf = DIR_DESCARGAS / download.suggested_filename
        # download.save_as(str(ruta_final_pdf))

        # print(f"Archivo PDF descargado exitosamente en: {ruta_final_pdf}")

        # Cerrar navegador
        context.close()
        browser.close()

if __name__ == "__main__":
    ejecutar_flujo()
