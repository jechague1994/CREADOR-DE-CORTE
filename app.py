import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Configuracion de pagina
st.set_page_config(page_title="Magallan - Generador", layout="wide")

st.title("Sistema de Fichas Tecnicas - Magallan")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Parametros")
    ancho_total = st.number_input("Ancho Fondo a Fondo (mts)", min_value=0.5, step=0.01, value=3.0)
    alto_vano = st.number_input("Alto de Guia (mts)", min_value=0.5, step=0.01, value=2.5)
    incluir_rollo = st.checkbox("Incluir rollo (+0.40m)", value=True)
    
    opciones_guias = {"60x50mm": 60, "80x60mm": 80, "100x60mm": 100, "150x60mm": 150}
    guia_sel = st.selectbox("Guia", list(opciones_guias.keys()))
    
    sistema = st.selectbox("Sistema", [
        "Motor Paralelo", "Motor Tubular", "Motor Semiblindado", 
        "Motor Blindado", "Sistema a Resorte", "Sistema a Cadena"
    ])
    lado = st.radio("Lado", ["Izquierda", "Derecha"])

# --- CALCULOS ---
ancho_guia_m = opciones_guias[guia_sel] / 1000
paso_libre = ancho_total - (ancho_guia_m * 2)
alto_final = alto_vano + 0.40 if incluir_rollo else alto_vano

# --- PROCESAMIENTO ---
if st.button("GENERAR FICHA"):
    try:
        img = Image.open("plantilla_base.jpg").convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        # Uso de fuente por defecto para evitar errores de archivo
        font = ImageFont.load_default()

        # Dibujar Medidas (ajustadas a tu imagen base)
        draw.text((420, 835), f"{ancho_total:.2f} mts", fill="black")
        draw.text((420, 725), f"PASO LIBRE: {paso_libre:.2f} mts", fill="red")
        draw.text((820, 420), f"{alto_final:.2f} mts", fill="black")

        # Insertar Motor desde carpeta assets
        # El nombre del archivo debe ser exacto al que subiste
        nombre_asset = sistema.lower().replace(" ", "_") + ".png"
        try:
            motor_img = Image.open(f"assets/{nombre_asset}").convert("RGBA")
            motor_img.thumbnail((200, 200))
            if lado == "Izquierda":
                motor_img = motor_img.transpose(Image.FLIP_LEFT_RIGHT)
                img.paste(motor_img, (50, 20), motor_img)
            else:
                img.paste(motor_img, (750, 20), motor_img)
        except:
            st.warning(f"No se encontro: assets/{nombre_asset}")

        st.image(img, use_container_width=True)
        
        # Descarga PDF
        pdf_buf = io.BytesIO()
        img.convert("RGB").save(pdf_buf, format="PDF")
        st.download_button("Descargar PDF", pdf_buf.getvalue(), "Ficha.pdf", "application/pdf")

    except Exception as e:
        st.error(f"Error: {e}")