st.title("Generador de Ficha Tecnica - Magallan")

# --- ENTRADA DE DATOS (SIDEBAR) ---
with st.sidebar:
    st.header("Parametros de Cortina")
    ancho_total = st.number_input("Ancho Fondo a Fondo (mts)", min_value=0.1, value=3.0, step=0.01)
    alto_guia = st.number_input("Alto de Guia (mts)", min_value=0.1, value=2.5, step=0.01)
    sumar_rollo = st.checkbox("Incluir rollo (+0.40m)", value=True)
    
    guias = {"60x50mm": 0.06, "80x60mm": 0.08, "100x60mm": 0.10, "150x60mm": 0.15}
    guia_sel = st.selectbox("Tipo de Guia", list(guias.keys()))
    
    sistema = st.selectbox("Sistema de Elevacion", [
        "Motor Paralelo", "Motor Tubular", "Motor Semiblindado", 
        "Motor Blindado", "Sistema a Resorte", "Sistema a Cadena"
    ])
    lado = st.radio("Lado del Motor/Mando", ["Izquierda", "Derecha"])

# --- CALCULOS ---
alto_final = alto_guia + 0.40 if sumar_rollo else alto_guia
paso_libre = ancho_total - (guias[guia_sel] * 2)

# --- GENERACION DE IMAGEN ---
if st.button("GENERAR FICHA"):
    try:
        # Carga de imagen base
        img = Image.open("plantilla_base.jpg").convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Intentamos usar fuente por defecto de PIL (mas compatible con Streamlit Cloud)
        # Dibujamos rectangulos blancos de fondo para que los textos resalten
        
        # 1. Medida: ANCHO TOTAL (Abajo centro)
        draw.rectangle([350, 830, 650, 880], fill="white", outline="black")
        draw.text((410, 845), f"ANCHO: {ancho_total:.2f} mts", fill="black")

        # 2. Medida: PASO LIBRE (Sobre flecha roja)
        draw.rectangle([350, 720, 650, 770], fill="white", outline="red")
        draw.text((380, 735), f"PASO LIBRE: {paso_libre:.2f} mts", fill="red")

        # 3. Medida: ALTO TOTAL (Derecha)
        draw.rectangle([830, 380, 980, 480], fill="white", outline="black")
        draw.text((840, 410), f"ALTO TOTAL:", fill="black")
        draw.text((840, 440), f"{alto_final:.2f} mts", fill="black")

        # 4. ESPACIO ROLLO (Si aplica)
        if sumar_rollo:
            draw.text((720, 110), "ROLLO: 0.40m", fill="blue")

        # 5. PEGAR MOTOR/SISTEMA
        archivo_motor = sistema.lower().replace(" ", "_") + ".png"
        try:
            motor_img = Image.open(f"assets/{archivo_motor}").convert("RGBA")
            motor_img.thumbnail((200, 200)) # Ajuste de tamaño
            
            if lado == "Izquierda":
                motor_img = motor_img.transpose(Image.FLIP_LEFT_RIGHT)
                # Coordenadas eje izquierdo
                img.paste(motor_img, (60, 30), motor_img)
            else:
                # Coordenadas eje derecho
                img.paste(motor_img, (720, 30), motor_img)
        except Exception as e_motor:
            st.warning(f"No se pudo cargar el motor '{archivo_motor}'. Verifique carpeta assets.")

        # --- MOSTRAR Y DESCARGAR ---
        st.image(img, use_container_width=True)
        
        # Convertir a PDF para descargar
        buf = io.BytesIO()
        img.save(buf, format="PDF")
        st.download_button("Descargar Ficha en PDF", buf.getvalue(), "Ficha_Magallan.pdf", "application/pdf")

    except FileNotFoundError:
        st.error("Error: Asegurate de que 'plantilla_base.jpg' este en la raiz de tu GitHub.")
    except Exception as e:
        st.error(f"Ocurrio un error inesperado: {e}")