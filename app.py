[20:23, 2/24/2026] Jonathan: import streamlit as st
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
[20:31, 2/24/2026] Jonathan: # --- DENTRO DEL BLOQUE: if st.button("GENERAR FICHA"): ---

    img = Image.open("plantilla_base.jpg").convert("RGB") # Usamos RGB para asegurar compatibilidad
    draw = ImageDraw.Draw(img)
    
    # Intentamos cargar una fuente mas grande o usamos una simulada
    # Si no tienes Arial.ttf, el texto sera pequeño, por eso usamos un rectangulo de fondo
    
    # 1. Dibujar rectangulos de fondo para que las medidas se vean
    # Ancho total
    draw.rectangle([400, 820, 600, 870], fill="white") 
    draw.text((420, 835), f"{ancho_total:.2f} mts", fill="black")
    
    # Paso Libre (en rojo)
    draw.rectangle([400, 710, 650, 760], fill="white")
    draw.text((420, 725), f"PASO LIBRE: {paso_libre:.2f} mts", fill="red")
    
    # Alto final
    draw.rectangle([810, 410, 950, 460], fill="white")
    draw.text((820, 420), f"{alto_final:.2f} mts", fill="black")

    # 2. Insertar Motor (Ajuste de posicion)
    nombre_asset = sistema.lower().replace(" ", "_") + ".png"
    try:
        motor_img = Image.open(f"assets/{nombre_asset}").convert("RGBA")
        motor_img.thumbnail((250, 250)) # Lo hacemos un poco mas grande
        
        if lado == "Izquierda":
            motor_img = motor_img.transpose(Image.FLIP_LEFT_RIGHT)
            # Pegamos el motor cerca del eje superior izquierdo
            img.paste(motor_img, (50, 50), motor_img)
        else:
            # Pegamos el motor cerca del eje superior derecho
            img.paste(motor_img, (700, 50), motor_img)
    except:
        st.warning(f"No se pudo superponer el motor: {nombre_asset}")

    # 3. MOSTRAR LA IMAGEN RESULTANTE (Este es el paso clave)
    st.image(img, caption="Resultado Final con Medidas", use_container_width=True)