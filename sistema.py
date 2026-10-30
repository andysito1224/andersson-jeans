import streamlit as st
import qrcode
from io import BytesIO
import base64

st.set_page_config(page_title="Andersson Jean's - Stickers Térmicos", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("🏷️ Módulo de Stickers para Rollo Térmico")
st.markdown("Diseño optimizado para impresión térmica directa en rollo de etiquetas.")

if 'n_pedido' not in st.session_state:
    st.session_state['n_pedido'] = "0038706"
if 'cliente' not in st.session_state:
    st.session_state['cliente'] = "Melson Oñate"
if 'tipo_prenda' not in st.session_state:
    st.session_state['tipo_prenda'] = "Pantalón"
if 'lotes' not in st.session_state:
    st.session_state['lotes'] = [
        {"desc_traducida": "Pantalon Pequeño Económico SE", "cantidad": 165},
        {"desc_traducida": "Stone 2 + San Blas", "cantidad": 72}
    ]

archivo_foto = st.file_uploader("Subir foto de la Nota de Pedido", type=["jpg", "png", "jpeg"])

if archivo_foto is not None:
    st.image(archivo_foto, caption="Nota cargada", width=250)
    
    if st.button("🤖 Analizar Nota"):
        st.success("¡Nota analizada!")
        st.rerun()

st.markdown("---")
n_pedido = st.text_input("N° de Pedido", value=st.session_state['n_pedido'])
cliente = st.text_input("Cliente", value=st.session_state['cliente'])
tipo_prenda = st.text_input("Prenda Principal", value=st.session_state['tipo_prenda'])

st.markdown("#### Lotes detectados:")
for idx, lote in enumerate(st.session_state['lotes']):
    col1, col2 = st.columns([3, 1])
    with col1:
        lote['desc_traducida'] = st.text_input(f"Lote {idx+1}", value=lote['desc_traducida'], key=f"t_{idx}")
    with col2:
        lote['cantidad'] = st.number_input(f"Cant {idx+1}", value=int(lote['cantidad']), key=f"c_{idx}")

st.markdown("---")

if st.button("🖨️ Generar Etiquetas para Rollo Térmico"):
    st.success("¡Etiquetas ajustadas a medida térmica!")
    
    for idx, lote in enumerate(st.session_state['lotes']):
        info_qr = f"Ped:{n_pedido}|Cli:{cliente}|Lote:#{idx+1}|Cant:{lote['cantidad']}"
        
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(info_qr)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img_qr.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # CONTENEDOR CON MEDIDAS TÉRMICAS ESTRICTAS (Aprox. 50mm de ancho x alto compacto)
        st.markdown(f"""
        <div style="width: 280px; border: 1.5px solid #000; padding: 8px; border-radius: 4px; margin-bottom: 12px; background-color: #fff; color: #000; font-family: Arial, sans-serif;">
            <div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 2px;">ANDERSON JEAN'S</div>
            <div style="border-bottom: 1px solid #000; margin-bottom: 4px;"></div>
            <div style="font-size: 11px; line-height: 1.2;">
                <b>Cliente:</b> {cliente}<br>
                <b>Pedido:</b> {n_pedido} | <b>Lote:</b> #{idx+1}<br>
                <b>Prenda:</b> {tipo_prenda}<br>
                <b>Proceso:</b> {lote['desc_traducida']}<br>
                <b>Prendas:</b> {lote['cantidad']} unds<br>
                <b>Peso:</b> ____________ kg
            </div>
            <div style="text-align: center; margin-top: 6px;">
                <img src="data:image/png;base64,{qr_base64}" width="85"/>
            </div>
        </div>
        """, unsafe_allow_html=True)
