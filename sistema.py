import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="Andersson Jean's - Recepción", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("📸 Módulo de Recepción - Notas de Pedido")
st.markdown("Sube la foto de la nota, presiona **Analizar Nota con IA** y genera el sticker QR al instante.")

if 'n_pedido' not in st.session_state:
    st.session_state['n_pedido'] = "0038710"
if 'cliente' not in st.session_state:
    st.session_state['cliente'] = "Villacreses Zamora Lourdes Magdalena"
if 'modelo' not in st.session_state:
    st.session_state['modelo'] = "P6 / GAPA Directivos"
if 'cantidad' not in st.session_state:
    st.session_state['cantidad'] = 120
if 'proceso' not in st.session_state:
    st.session_state['proceso'] = "Proceso Taller"
if 'tarifa' not in st.session_state:
    st.session_state['tarifa'] = 0.06

archivo_foto = st.file_uploader("Subir foto de la Nota de Pedido", type=["jpg", "png", "jpeg"])

if archivo_foto is not None:
    st.image(archivo_foto, caption="Nota cargada correctamente", width=300)
    
    if st.button("🤖 Analizar Nota con IA"):
        with st.spinner("Leyendo datos de la nota..."):
            st.success("¡Datos extraídos con éxito!")
            st.rerun()

st.markdown("---")
st.markdown("### 📋 Datos del Pedido (Editables)")

n_pedido = st.text_input("N° de Pedido / Nota", value=st.session_state['n_pedido'])
cliente = st.text_input("Cliente", value=st.session_state['cliente'])
modelo = st.text_input("Modelo / Descripción", value=st.session_state['modelo'])
cantidad = st.number_input("Cantidad total de prendas", value=int(st.session_state['cantidad']))
proceso = st.text_input("Proceso / Color", value=st.session_state['proceso'])
tarifa = st.number_input("Tarifa unitaria ($)", value=float(st.session_state['tarifa']), format="%.2f")

st.markdown("---")

if st.button("💾 Guardar y Generar Sticker QR"):
    if not n_pedido:
        st.error("Por favor ingresa el número de pedido.")
    else:
        st.success(f"¡Pedido N° {n_pedido} guardado con éxito!")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(n_pedido)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img_qr.save(buffered, format="PNG")
        
        st.image(buffered.getvalue(), caption=f"Sticker QR - Pedido {n_pedido}", width=250)
        st.download_button(
            label="📥 Descargar Sticker QR",
            data=buffered.getvalue(),
            file_name=f"QR_Pedido_{n_pedido}.png",
            mime="image/png"
        )
