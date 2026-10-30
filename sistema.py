import streamlit as st

st.subheader("📸 Andersson Jean's - Recepción de Pedidos y QR")
st.markdown("Tome la foto de la nota de pedido, analícela con IA y genere los stickers QR sin rellenar datos a mano.")

# 1. Subir o tomar la foto de la nota
archivo_foto = st.file_uploader("Tomar / Subir Foto de la Nota de Pedido", type=["jpg", "png", "jpeg"])

# Inicializar st.session_state para los campos si no existen
campos_clave = ['n_pedido', 'cliente', 'modelo', 'cantidad', 'proceso', 'tarifa']
for campo in campos_clave:
    if campo not in st.session_state:
        st.session_state[campo] = ""

# Valor por defecto para cantidad y tarifa si están vacíos
if not st.session_state['cantidad']:
    st.session_state['cantidad'] = 100
if not st.session_state['tarifa']:
    st.session_state['tarifa'] = 0.06

if archivo_foto is not None:
    st.image(archivo_foto, caption="Nota de pedido cargada", width=300)
    
    # 2. Botón para analizar la foto con IA
    if st.button("🤖 Analizar foto con IA"):
        with st.spinner("Leyendo datos de la nota con IA..."):
            
            # --- AQUÍ LLAMAS A TU MODELO DE VISIÓN (ej. Gemini Pro Vision / Flash) ---
            # Simulamos la extracción automática de los datos de la imagen:
            # (Aquí integrarías el llamado a la API de Gemini pasándole la imagen subida)
            datos_extraidos = {
                "n_pedido": "0038743",
                "cliente": "Confecciones Textiles S.A.",
                "modelo": "Jean Slim Fit Clásico",
                "cantidad": 120,
                "proceso": "Lavado Oscuro + Enlacrado",
                "tarifa": 0.06
            }
            
            # Guardamos los resultados en la sesión para que los inputs se actualicen solos
            st.session_state['n_pedido'] = datos_extraidos["n_pedido"]
            st.session_state['cliente'] = datos_extraidos["cliente"]
            st.session_state['modelo'] = datos_extraidos["modelo"]
            st.session_state['cantidad'] = datos_extraidos["cantidad"]
            st.session_state['proceso'] = datos_extraidos["proceso"]
            st.session_state['tarifa'] = datos_extraidos["tarifa"]
            
            st.success("¡Datos extraídos correctamente! Verifique y guarde.")
            st.rerun() # Recarga para pintar los campos con los valores nuevos

# 3. Campos del formulario autocompletados con st.session_state
n_pedido = st.text_input("N° de Pedido / Nota (ej: 0038743)", value=st.session_state['n_pedido'])
cliente = st.text_input("Cliente", value=st.session_state['cliente'])
modelo = st.text_input("Modelo / Prenda", value=st.session_state['modelo'])
cantidad = st.number_input("Cantidad total de prendas", value=int(st.session_state['cantidad']))
proceso = st.text_input("Proceso / Lavado / Color", value=st.session_state['proceso'])
tarifa = st.number_input("Tarifa unitaria operario ($)", value=float(st.session_state['tarifa']), format="%.2f")

# Actualizamos session_state si modificas algo a mano
st.session_state['n_pedido'] = n_pedido
st.session_state['cliente'] = cliente
st.session_state['modelo'] = modelo
st.session_state['cantidad'] = cantidad
st.session_state['proceso'] = proceso
st.session_state['tarifa'] = tarifa

# 4. Botón final para guardar y generar QR
if st.button("💾 Guardar Parada y Generar QR"):
    if not n_pedido:
        st.error("Por favor ingrese o analice el número de pedido o nota.")
    else:
        st.success("¡Parada guardada y QR generado correctamente!")
        # Aquí añades tu lógica para guardar en base de datos o generar el código QR
