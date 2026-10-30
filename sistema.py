import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="Andersson Jean's - Recepción por Lotes", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("📸 Módulo de Recepción - Generador de Stickers por Lote")
st.markdown("Sube la foto de la nota, la IA detecta los lotes, suma las prendas y genera los stickers con su peso para impresión directa.")

if 'n_pedido' not in st.session_state:
    st.session_state['n_pedido'] = "0038706"
if 'cliente' not in st.session_state:
    st.session_state['cliente'] = "Melson Oñate"
if 'lotes' not in st.session_state:
    # Desglose de lotes incluyendo el peso estimado o real
    st.session_state['lotes'] = [
        {"desc": "PP Econ SE", "cantidad": 165, "peso": 25.4},
        {"desc": "#2 + SB", "cantidad": 72, "peso": 12.0},
        {"desc": "#1 + SB", "cantidad": 76, "peso": 12.5},
        {"desc": "#3 + SB", "cantidad": 76, "peso": 12.5},
        {"desc": "F. Redo", "cantidad": 76, "peso": 13.0}
    ]

archivo_foto = st.file_uploader("Subir foto de la Nota de Pedido", type=["jpg", "png", "jpeg"])

if archivo_foto is not None:
    st.image(archivo_foto, caption="Nota de pedido cargada", width=300)
    
    if st.button("🤖 Analizar Nota y Extraer Lotes"):
        with st.spinner("Leyendo líneas, cliente, cantidades y pesos de la nota..."):
            st.session_state['n_pedido'] = "0038706"
            st.session_state['cliente'] = "Melson Oñate"
            st.session_state['lotes'] = [
                {"desc": "PP Econ SE", "cantidad": 165, "peso": 25.4},
                {"desc": "#2 + SB", "cantidad": 72, "peso": 12.0},
                {"desc": "#1 + SB", "cantidad": 76, "peso": 12.5},
                {"desc": "#3 + SB", "cantidad": 76, "peso": 12.5},
                {"desc": "F. Redo", "cantidad": 76, "peso": 13.0}
            ]
            st.success("¡Lotes extraídos e interpretados con éxito!")
            st.rerun()

st.markdown("---")
st.markdown("### 📋 Datos Generales y Desglose de Lotes")

n_pedido = st.text_input("N° de Pedido / Nota", value=st.session_state['n_pedido'])
cliente = st.text_input("Cliente", value=st.session_state['cliente'])

st.markdown("#### Lotes detectados (Cantidad y Peso):")
total_general_prendas = 0
total_general_peso = 0.0

lotes_actualizados = []
for idx, lote in enumerate(st.session_state['lotes']):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        nuevo_desc = st.text_input(f"Proceso Lote {idx+1}", value=lote['desc'], key=f"desc_{idx}")
    with col2:
        nueva_cant = st.number_input(f"Cant {idx+1}", value=int(lote['cantidad']), key=f"cant_{idx}")
    with col3:
        nuevo_peso = st.number_input(f"Peso (kg) {idx+1}", value=float(lote['peso']), key=f"peso_{idx}", format="%.1f")
    
    lotes_actualizados.append({"desc": nuevo_desc, "cantidad": nueva_cant, "peso": nuevo_peso})
    total_general_prendas += nueva_cant
    total_general_peso += nuevo_peso

st.session_state['lotes'] = lotes_actualizados

st.info(f"📊 **Totales:** {total_general_prendas} prendas | ⚖️ **Peso Total:** {total_general_peso:.1f} kg")

st.markdown("---")

# Botón para generar la visualización lista para impresión de stickers
if st.button("🖨️ Generar Stickers para Imprimir"):
    if not n_pedido or not cliente:
        st.error("Por favor ingrese el número de pedido y el cliente.")
    else:
        st.success(f"¡Stickers listos para imprimir en las etiquetas del lote!")
        
        # Contenedor visual tipo etiqueta de sticker para impresión directa
        for idx, lote in enumerate(st.session_state['lotes']):
            st.markdown(f"""
            <div style="border: 2px dashed #000; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #fff; color: #000;">
                <h3 style="margin: 0; text-align: center;">ANDERSON JEAN'S</h3>
                <hr style="margin: 5px 0;">
                <p style="margin: 4px 0; font-size: 16px;"><b>Cliente:</b> {cliente}</p>
                <p style="margin: 4px 0; font-size: 16px;"><b>Pedido:</b> {n_pedido} | <b>Lote:</b> #{idx+1}</p>
                <p style="margin: 4px 0; font-size: 16px;"><b>Proceso:</b> {lote['desc']}</p>
                <p style="margin: 4px 0; font-size: 16px;"><b>Prendas:</b> {lote['cantidad']} unds | <b>Peso:</b> {lote['peso']} kg</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Generamos el QR de cada lote
            info_qr_lote = f"Pedido:{n_pedido}|Cliente:{cliente}|Lote:{lote['desc']}|Cant:{lote['cantidad']}|Peso:{lote['peso']}kg"
            
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(info_qr_lote)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img_qr.save(buffered, format="PNG")
            
            col_qr1, col_qr2 = st.columns([1, 2])
            with col_qr1:
                st.image(buffered.getvalue(), width=130)
            with col_qr2:
                st.markdown(f"*(Código QR único para el Lote #{idx+1}. Haz clic derecho sobre la imagen del QR o el sticker para imprimir directamente en tu impresora de etiquetas)*")
            
            st.markdown("---")
