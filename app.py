import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Configuracion de pagina
st.set_page_config(page_title="Generador Magallan", layout="wide")

st.title("Generador de Ficha Tecnica - Magallan")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("Datos de la Cortina")
    ancho = st.number_input("Ancho Fondo a Fondo (mts)", value=3.0, step=0.01)
    alto_v = st.number_input("Alto de Guia (mts)", value=2.5, step=0.01)
    rollo = st.checkbox("Incluir rollo (+0.40m)", value=True)
    
    guias_dict = {"60x50mm": 0.06, "80x60mm": 0.08, "100x60mm": 0.10, "150x60mm": 0.15}
    tipo_guia = st.selectbox("Guia", list(guias_dict.keys()))
    
    sis = st.selectbox("Sistema", ["Motor Paralelo", "Motor Tubular", "Motor Semiblindado", "Motor Blindado", "Sistema a Resorte", "Sistema a Cadena"])
    lado_m = st.radio("Lado del mando", ["Izquierda", "Derecha"])
    
    # Nueva opcion de tablilla
    tipo_tablilla = st.selectbox("Tipo de Tablilla", ["Ciega", "Microperforada", "Troquelada"])

# --- CALCULOS ---
alto_f = alto_v + 0.40 if rollo else alto_v
paso_l = ancho - (guias_dict[tipo_guia] * 2)

# --- PROCESO DE IMAGEN ---
if st.button("GENERAR FICHA"):
    try:
        # 1. Abrir la imagen base (La de las flechas)
        img = Image.open("plantilla_base.jpg").convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # 2. Dibujar medidas (Coordenadas ajustadas)
        # Ancho Total
        draw.rectangle([400, 830, 600, 880], fill="white")
        draw.text((410, 840), f"ANCHO: {ancho:.2f}m", fill="black")

        # Paso Libre
        draw.rectangle([400, 720, 650, 770], fill="white")
        draw.text((410, 730), f"PASO LIBRE: {paso_l:.2f}m", fill="red")

        # Alto
        draw.rectangle([850, 400, 980, 450], fill="white")
        draw.text((860, 410), f"ALTO: {alto_f:.2f}m", fill="black")

        # 3. Colocar Motor desde assets
        nom_m = sis.lower().replace(" ", "_") + ".png"
        try:
            m_img = Image.open(f"assets/{nom_m}").convert("RGBA")
            m_img.thumbnail((200, 200))
            if lado_m == "Izquierda":
                m_img = m_img.transpose(Image.FLIP_LEFT_RIGHT)
                img.paste(m_img, (50, 30), m_img)
            else:
                img.paste(m_img, (750, 30), m_img)
        except:
            st.warning(f"No se encontro: assets/{nom_m}")

        # 4. Colocar Muestra de Tablilla
        # Usamos la imagen que subiste de las duelas
        try:
            tab_img = Image.open("assets/duela_semi_plana.png").convert("RGB")
            # Definimos coordenadas de recorte para cada tipo (ajustables)
            cortes = {
                "Ciega": (10, 10, 300, 150),
                "Microperforada": (10, 160, 300, 310),
                "Troquelada": (10, 320, 300, 470)
            }
            muestra = tab_img.crop(cortes[tipo_tablilla])
            muestra.thumbnail((150, 150))
            # La pegamos en la esquina inferior izquierda como referencia
            img.paste(muestra, (50, 750))
            draw.text((50, 720), f"Tablilla: {tipo_tablilla}", fill="black")
        except:
            st.info("Nota: Para ver la tablilla, sube 'duela_semi_plana.png' a assets.")

        # 5. Mostrar y Descargar
        st.image(img, use_container_width=True)
        
        pdf_io = io.BytesIO()
        img.save(pdf_io, format="PDF")
        st.download_button("📥 Descargar Ficha PDF", pdf_io.getvalue(), f"Ficha_Magallan_{ancho}x{alto_f}.pdf")

    except Exception as e:
        st.error(f"Error critico: {e}. Verifique que 'plantilla_base.jpg' este en GitHub.")