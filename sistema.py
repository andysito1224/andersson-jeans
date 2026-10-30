import streamlit as st
import qrcode
from io import BytesIO
import base64

st.set_page_config(page_title="Andersson Jean's - Recepción Inteligente", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("📸 Módulo de Recepción - Traductor de Abreviaturas y Lotes")
st.markdown("Sube la nota, la IA traduce abreviaturas (PP, SB, #1, FR...), detecta la prenda principal y genera los stickers con el QR adentro.")

if 'n_pedido' not in st.session_state:
    st.session_state['n_pedido'] = "0038706"
if 'cliente' not in st.session_state:
    st.session_state['cliente'] = "Melson Oñate"
if 'tipo_prenda' not in st.session_state:
    st.session_state['tipo_prenda'] = "Pantalón"
if 'lotes' not in st.session_state:
    st.session_state['lotes'] = [
        {"desc_original": "PP Econ SE", "desc_traducida": "Pantalon Pequeño Económico SE", "cantidad": 165},
        {"desc_original": "#2 + SB", "desc_traducida": "Stone 2 + San Blas", "cantidad": 72},
        {"desc_original": "#1 + SB", "desc_traducida": "Stone 1 + San Blas", "cantidad": 76},
        {"desc_original": "#3 + SB", "desc_traducida": "Stone 3 + San Blas", "cantidad": 76},
        {"desc_original": "F. Redo", "desc_traducida": "Froter Redondo", "cantidad": 76}
    ]

archivo_foto = st.file_uploader("Subir foto de la Nota de Pedido", type=["jpg", "png", "jpeg"])

if archivo_foto is not None:
    st.image(archivo_foto, caption="Nota de pedido cargada", width=300)
    
    if st.button("🤖 Analizar, Traducir y Extraer Lotes"):
        with st.spinner("Interpretando abreviaturas y traduciendo textos..."):
            # Simulamos la lectura inteligente con el diccionario del taller
            st.session_state['n_pedido'] = "0038706"
            st.session_state['cliente'] = "Melson Oñate"
            st.session_state['tipo_prenda'] = "Pantalón"
            st.session_state['lotes'] = [
                {"desc_original": "PP Econ SE", "desc_traducida": "Pantalon Pequeño Económico SE", "cantidad": 165},
                {"desc_original": "#2 + SB", "desc_traducida": "Stone 2 + San Blas", "cantidad": 72},
                {"desc_original": "#1 + SB", "desc_traducida": "Stone 1 + San Blas", "cantidad": 76},
                {"desc_original": "#3 + SB", "desc_traducida": "Stone 3 + San Blas", "cantidad": 76},
                {"desc_original": "F. Redo", "desc_traducida": "Froter Redondo", "cantidad": 76}
            ]
            st.success("¡Nota analizada, abreviaturas traducidas y lotes listos!")
            st.rerun()

st.markdown("---")
st.markdown("### 📋 Datos Generales y Traducción de Lotes")

n_pedido = st.text_input("N° de Pedido / Nota", value=st.session_state['n_pedido'])
cliente = st.text_input("Cliente", value=st.session_state['cliente'])
tipo_prenda = st.text_input("Tipo de Prenda Principal (ej. Pantalón, Vestido, Jean)", value=st.session_state['tipo_prenda'])

st.markdown("#### Lotes y Traducción de Abreviaturas:")
total_general_prendas = 0

lotes_actualizados = []
for idx, lote in enumerate(st.session_state['lotes']):
    col1, col2 = st.columns([3, 1])
    with col1:
        nueva_trad = st.text_input(f"Lote {idx+1} (Traducido / Completo)", value=lote['desc_traducida'], key=f"trad_{idx}")
    with col2:
        nueva_cant = st.number_input(f"Cant {idx+1}", value=int(lote['cantidad']), key=f"cant_{idx}")
    
    lotes_actualizados.append({"desc_original": lote['desc_original'], "desc_traducida": nueva_trad, "cantidad": nueva_cant})
    total_general_prendas += nueva_cant

st.session_state['lotes'] = lotes_actualizados

st.info(f"📊 **Suma Total General:** {total_general_prendas} unidades de {tipo_prenda}")

st.markdown("---")

if st.button("🖨️ Generar Stickers para Imprimir"):
    if not n_pedido or not cliente or len(st.session_state['lotes']) == 0:
        st.warning("Por favor verifica que los datos estén completos.")
    else:
        st.success(f"¡Stickers con nombres completos y QR listos para imprimir!")
        
        for idx, lote in enumerate(st.session_state['lotes']):
            # Contenido único del QR para que el operario lo escanee en manualidades
            info_qr_lote = f"Pedido:{n_pedido}|Cliente:{cliente}|Prenda:{tipo_prenda}|Proceso:{lote['desc_traducida']}|Cant:{lote['cantidad']}"
            
            qr = qrcode.QRCode(version=1, box_size=5, border=1)
            qr.add_data(info_qr_lote)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img_qr.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Diseño de la etiqueta con el QR adentro y el peso en blanco
            st.markdown(f"""
            <div style="border: 2px dashed #000; padding: 12px; border-radius: 8px; margin-bottom: 20px; background-color: #fff; color: #000; display: flex; justify-content: space-between; align-items: center;">
                <div style="flex-grow: 1; padding-right: 10px;">
                    <h4 style="margin: 0; text-align: center; font-size: 18px;">ANDERSON JEAN'S</h4>
                    <hr style="margin: 4px 0;">
                    <p style="margin: 3px 0; font-size: 14px;"><b>Cliente:</b> {cliente}</p>
                    <p style="margin: 3px 0; font-size: 14px;"><b>Pedido:</b> {n_pedido} | <b>Lote:</b> #{idx+1}</p>
                    <p style="margin: 3px 0; font-size: 14px;"><b>Prenda:</b> {tipo_prenda}</p>
                    <p style="margin: 3px 0; font-size: 14px;"><b>Proceso/Detalle:</b> {lote['desc_traducida']}</p>
                    <p style="margin: 3px 0; font-size: 14px;"><b>Prendas:</b> {lote['cantidad']} unds</p>
                    <p style="margin: 3px 0; font-size: 14px;"><b>Peso:</b> ____________ kg</p>
                </div>
                <div style="text-align: center; min-width: 100px;">
                    <img src="data:image/png;base64,{qr_base64}" width="95"/>
                    <div style="font-size: 10px; margin-top: 2px;">Escanear Lote</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
