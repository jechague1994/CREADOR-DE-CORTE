import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Configuracion sin caracteres especiales
st.set_page_config(page_title="Magallan Fichas", layout="wide")
st.title("Generador de Ficha Tecnica - Magallan")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuracion")
    ancho = st.number_input("Ancho Total (mts)", value=3.0, step=0.01)
    alto_v = st.number_input("Alto de Guia (mts)", value=2.5, step=0.01)
    rollo = st.checkbox("Incluir rollo (+0.40m)", value=True)
    
    guias_dict = {"60x50mm": 0.06, "80x60mm": 0.08, "100x60mm": 0.10, "150x60mm": 0.15}
    tipo_guia = st.selectbox("Guia", list(guias_dict.keys()))
    
    sis = st.selectbox("Sistema de Elevacion", [
        "Motor Paralelo", "Motor Tubular", "Motor Semiblindado", 
        "Motor Blindado", "Sistema a Resorte", "Sistema a Cadena"
    ])
    
    tablilla = st.selectbox("Tablilla", ["Ciega", "Microperforada", "Troquelada"])

# --- CALCULOS ---
alto_f = alto_v + 0.40 if rollo else alto_v
paso_l = ancho - (guias_dict[tipo_guia] * 2)

# --- GENERACION ---
if st.button("GENERAR FICHA"):
    nom_img = sis.lower().replace(" ", "_") + ".png"
    ruta_img = f"assets/{nom_img}"
    
    try:
        # 1. Abrir la imagen del sistema elegido
        img = Image.open(ruta_img).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        # 2. Intentar pegar el LOGO en la esquina superior derecha
        try:
            logo = Image.open("assets/logo.png").convert("RGBA")
            logo.thumbnail((200, 100))
            img.paste(logo, (w - 220, 20), logo)
        except:
            # Si no hay logo, escribimos el nombre de la empresa
            draw.text((w - 220, 30), "MAGALLAN", fill="#004680")

        # 3. Dibujar Panel de Medidas Profesional (Abajo)
        # Creamos una base blanca solida para los datos
        rect_h = 180
        draw.rectangle([0, h - rect_h, w, h], fill="white")
        draw.line([0, h - rect_h, w, h - rect_h], fill="#004680", width=5)

        # 4. Escribir datos organizados en columnas (simulado)
        y_text = h - rect_h + 30
        draw.text((40, y_text), f"SISTEMA SELECCIONADO: {sis.upper()}", fill="#004680")
        draw.text((40, y_text + 40), f"ANCHO TOTAL: {ancho:.2f} mts", fill="black")
        draw.text((40, y_text + 80), f"ALTO TOTAL: {alto_f:.2f} mts", fill="black")
        
        draw.text((w // 2, y_text + 40), f"PASO LIBRE: {paso_l:.2f} mts", fill="red")
        draw.text((w // 2, y_text + 80), f"TIPO DE TABLILLA: {tablilla}", fill="black")

        # 5. Mostrar y Descargar
        st.image(img, use_container_width=True)
        
        pdf_io = io.BytesIO()
        img.save(pdf_io, format="PDF")
        st.download_button("📥 Descargar PDF para Cliente", pdf_io.getvalue(), f"Ficha_{ancho}x{alto_f}.pdf")

    except Exception as e:
        st.error(f"Error: No se pudo cargar la imagen del sistema {nom_img}. Revisa la carpeta assets.")