import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración de página
st.set_page_config(page_title="Magallan - Generador de Cortinas", layout="wide")

# Estilos personalizados
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("??? Sistema de Fichas Técnicas - Magallan")

# --- SIDEBAR: ENTRADA DE DATOS ---
with st.sidebar:
    st.header("?? Parámetros de la Cortina")
    
    ancho_total = st.number_input("Ancho Fondo a Fondo (mts)", min_value=0.5, step=0.01, value=3.0)
    alto_vano = st.number_input("Alto de Guía/Abertura (mts)", min_value=0.5, step=0.01, value=2.5)
    
    incluir_rollo = st.checkbox("Incluir espacio para rollo (+0.40m)", value=True)
    
    st.divider()
    
    opciones_guias = {"60x50mm": 60, "80x60mm": 80, "100x60mm": 100, "150x60mm": 150}
    guia_sel = st.selectbox("Tipo de Guía", list(opciones_guias.keys()))
    
    sistema = st.selectbox("Sistema de Elevación", [
        "Motor Paralelo", "Motor Tubular", "Motor Semiblindado", 
        "Motor Blindado", "Sistema a Resorte", "Sistema a Cadena"
    ])
    
    lado = st.radio("Ubicación del Mando/Motor", ["Izquierda", "Derecha"])
    
    tablilla = st.selectbox("Tipo de Tablilla", ["Ciega", "Microperforada", "Troquelada"])

# --- LÓGICA DE CÁLCULO ---
ancho_guia_m = opciones_guias[guia_sel] / 1000
paso_libre = ancho_total - (ancho_guia_m * 2)
alto_final = alto_vano + 0.40 if incluir_rollo else alto_vano

# --- PROCESAMIENTO DE IMAGEN ---
if st.button("?? GENERAR FICHA TÉCNICA"):
    try:
        # 1. Cargar imagen base
        img = Image.open("plantilla_base.jpg").convert("RGBA")
        canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 2. Intentar cargar fuentes (usamos default si falla)
        try:
            font_grande = ImageFont.truetype("Arial.ttf", 35)
            font_med = ImageFont.truetype("Arial.ttf", 25)
        except:
            font_grande = ImageFont.load_default()
            font_med = ImageFont.load_default()

        # 3. Dibujar Medidas (Coordenadas ajustadas a tu plantilla)
        # Ancho Fondo a Fondo (Abajo)
        draw.text((420, 835), f"{ancho_total:.2f} mts", fill="black", font=font_grande)
        
        # Paso Libre (Centro sobre flecha roja)
        draw.text((420, 725), f"PASO LIBRE: {paso_libre:.2f} mts", fill="#D32F2F", font=font_med)
        
        # Alto (Lateral derecho)
        draw.text((820, 420), f"{alto_final:.2f} mts", fill="black", font=font_grande)

        # Información de texto en esquina
        draw.text((50, 40), f"SISTEMA: {sistema.upper()}", fill="#004680", font=font_med)
        draw.text((50, 75), f"GUÍA: {guia_sel} | TABLILLA: {tablilla}", fill="#004680", font=font_med)

        # 4. Insertar el Motor/Sistema (Lógica de assets)
        nombre_asset = sistema.lower().replace(" ", "_") + ".png"
        try:
            motor_img = Image.open(f"assets/{nombre_asset}").convert("RGBA")
            # Redimensionar si es necesario (ejemplo a 150px de ancho)
            motor_img.thumbnail((180, 180))
            
            if lado == "Izquierda":
                motor_img = motor_img.transpose(Image.FLIP_LEFT_RIGHT)
                img.paste(motor_img, (80, 20), motor_img)
            else:
                img.paste(motor_img, (750, 20), motor_img)
        except:
            st.warning(f"No se pudo cargar la imagen del sistema: {nombre_asset}")

        # --- MOSTRAR RESULTADO ---
        col_img, col_info = st.columns([3, 1])
        
        with col_img:
            st.image(img, use_container_width=True)
        
        with col_info:
            st.success("? ¡Ficha generada!")
            st.metric("Ancho Total", f"{ancho_total} m")
            st.metric("Paso Libre", f"{paso_libre:.3f} m")
            st.metric("Altura Final", f"{alto_final} m")
            
            # Preparar PDF para descarga
            pdf_buf = io.BytesIO()
            img.convert("RGB").save(pdf_buf, format="PDF")
            
            st.download_button(
                label="?? Descargar PDF",
                data=pdf_buf.getvalue(),
                file_name=f"Ficha_Magallan_{ancho_total}x{alto_final}.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        st.info("Asegúrate de tener 'plantilla_base.jpg' en la raíz del proyecto.")