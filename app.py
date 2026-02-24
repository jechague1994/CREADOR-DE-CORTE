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
    draw.rectang…
[20:36, 2/24/2026] Jonathan: import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración sin caracteres especiales para evitar errores de encoding
st.set_page_config(page_title="Magallan Cortinas", layout="wide")

st.title("Generador de Ficha Tecnica - Magallan")

# --- PARAMETROS ---
with st.sidebar:
    st.header("Entrada de Datos")
    ancho_total = st.number_input("Ancho Fondo a Fondo (mts)", value=3.0)
    alto_guia = st.number_input("Alto de Guia (mts)", value=2.5)
    sumar_rollo = st.checkbox("Sumar rollo (+0.40m)", value=True)
    
    opciones_guias = {"60x50mm": 0.06, "80x60mm": 0.08, "100x60mm": 0.10, "150x60mm": 0.15}
    guia_sel = st.selectbox("Tipo de Guia", list(opciones_guias.keys()))
    
    sistema = st.selectbox("Sistema de Elevacion", [
        "Motor Paralelo", "Motor Tubular", "Motor Semiblindado", 
        "Motor Blindado", "Sistema a Resorte", "Sistema a Cadena"
    ])
    lado = st.radio("Lado del Motor", ["Izquierda", "Derecha"])

# --- CALCULOS ---
alto_final = alto_guia + 0.40 if sumar_rollo else alto_guia
paso_libre = ancho_total - (opciones_guias[guia_sel] * 2)

# --- BOTON DE ACCION ---
if st.button("GENERAR FICHA"):
    try:
        # Cargamos la imagen de la CORTINA COMPLETA
        img = Image.open("plantilla_base.jpg").convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Intentamos usar una fuente legible, sino la de sistema
        try:
            font = ImageFont.load_default() # Para GitHub, esto es lo mas seguro
        except:
            font = ImageFont.load_default()

        # Dibujamos las medidas con rectangulos blancos de fondo para que se vean SI O SI
        # Ancho Total (Abajo)
        draw.rectangle([400, 830, 600, 880], fill="white")
        draw.text((410, 840), f"ANCHO: {ancho_total:.2f}m", fill="black")

        # Paso Libre (Centro)
        draw.rectangle([400, 720, 650, 770], fill="white")
        draw.text((410, 730), f"PASO LIBRE: {paso_libre:.2f}m", fill="red")

        # Alto (Derecha)
        draw.rectangle([850, 400, 980, 450], fill="white")
        draw.text((860, 410), f"ALTO: {alto_final:.2f}m", fill="black")

        # Insertar el dibujo del motor
        nombre_motor = sistema.lower().replace(" ", "_") + ".png"
        try:
            motor_ico = Image.open(f"assets/{nombre_motor}").convert("RGBA")
            motor_ico.thumbnail((250, 250)) # Lo hacemos grande para que se note
            
            if lado == "Izquierda":
                motor_ico = motor_ico.transpose(Image.FLIP_LEFT_RIGHT)
                img.paste(motor_ico, (50, 50), motor_ico)
            else:
                img.paste(motor_ico, (700, 50), motor_ico)
        except:
            st.warning(f"No se encontro la imagen: assets/{nombre_motor}")

        # Mostrar resultado
        st.image(img, use_container_width=True)
        
        # Opcion de PDF
        buf = io.BytesIO()
        img.save(buf, format="PDF")
        st.download_button("Descargar Ficha en PDF", buf.getvalue(), "Ficha_Magallan.pdf")

    except FileNotFoundError:
        st.error("Falta el archivo 'plantilla_base.jpg' en el repositorio.")