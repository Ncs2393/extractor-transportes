import streamlit as st
import pandas as pd
import requests
import io

# Configuración estética de la app web
st.set_page_config(page_title="Extractor de Servicios Cloud", page_icon="🚖", layout="wide")

st.title("🚖 Extractor de Servicios (Conectado a Colab)")
st.markdown("Consolida tus capturas de pantalla usando el motor de tu Google Colab.")

# Entrada de la URL generada por Ngrok en tu Colab
url_colab = st.text_input(
    "Enlace público de Colab (Ngrok URL):", 
    placeholder="https://xxxx-xx-xx.ngrok-free.app"
)

# Selector de múltiples archivos
archivos_subidos = st.file_uploader(
    "Sube tus imágenes aquí", 
    type=["png", "jpg", "jpeg", "webp"], 
    accept_multiple_files=True
)

if archivos_subidos and url_colab:
    # Asegurar el formato correcto de la URL
    url_colab = url_colab.strip()
    if not url_colab.endswith("/"):
        url_colab += "/"
    
    endpoint = f"{url_colab}procesar-imagen/"
    datos_consolidados = []
    barra_progreso = st.progress(0)
    
    for idx, archivo in enumerate(archivos_subidos):
        try:
            # Empaquetar la imagen para la transmisión HTTP
            files = {"file": (archivo.name, archivo.getvalue(), archivo.type)}
            
            # CRUCIAL: Cabecera para saltar la pantalla de advertencia de Ngrok
            headers = {"ngrok-skip-browser-warning": "true"}
            
            response = requests.post(endpoint, files=files, headers=headers)
            
            if response.status_code == 200:
                datos_consolidados.append(response.json())
            else:
                st.error(f"Error {response.status_code} en Colab al procesar: {archivo.name}")
        except Exception as e:
            st.error(f"No se pudo conectar con Colab para {archivo.name}: {e}")
            
        barra_progreso.progress((idx + 1) / len(archivos_subidos))
        
    if datos_consolidados:
        df = pd.DataFrame(datos_consolidados)
        columnas_ordenadas = [
            "CONDUCTOR", "FECHA SERVICIO", "EMPRESA", "Empresa / Dirección inicio", 
            "EXP", "Destino", "VALOR", "Valor Final", "ESTADO SERVICIO", "ESTADO PAGO"
        ]
        df = df.reindex(columns=columnas_ordenadas)
        
        st.subheader("📊 Tabla de Resultados")
        st.dataframe(df, use_container_width=True)
        
        # Generar Excel en memoria para descarga inmediata
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Servicios')
        buffer.seek(0)
        
        st.download_button(
            label="📥 Descargar archivo Excel",
            data=buffer,
            file_name="Consolidado_Colab_Streamlit.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
