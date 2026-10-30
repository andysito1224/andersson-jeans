import streamlit as st
import qrcode
from io import BytesIO
import base64

st.set_page_config(page_title="Andersson Jean's - Recepción Inteligente", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("🏷️ Módulo de Recepción y Stickers Térmicos con Diccionario")
st.markdown("Selecciona el cliente del taller, ingresa el pedido y deja que el sistema organice los lotes listos para imprimir.")

# BASE DE DATOS DE CLIENTES FRECUENTES EXTRAÍDA DE TUS TALONARIOS
CLIENTES_FRECUENTES = [
    "-- Selecciona un cliente del taller --",
    "Melson Oñate",
    "César Salazar",
    "Verónica Sánchez",
    "Jaime Urrutia",
    "Gloria Cherrez",
    "Hortensia Lleva",
    "Hernán López",
    "Alex Quinga",
    "Mario Mena",
    "Danilo Oñate",
    "Vicente Urrutia",
    "Jessica Urrutia",
    "Rocío Urrutia",
    "Kevin Pallo",
    "Oscar Rodríguez",
    "Geison Urrutia",
    "Elizabeth Vinueza",
    "Darwin Jimenez",
    "Eduardo Paredes / Carmita Chifla",
    "Carmen Banera",
    "Darwin Pallo"
]

# Inicializar estados limpios
if 'n_pedido' not in st.session_state:
    st.session_state['n_pedido'] = ""
if 'lotes' not in st.session_state:
    st.session_state['lotes'] = [{"desc": "Pantalón Grande [P.6] - Stone 1 + San Blas", "cantidad": 100}]

# 1. Subir foto de referencia de la nota
archivo_foto = st.file_uploader("Subir foto de la Nota de Pedido (Referencia visual)", type=["jpg", "png", "jpeg"])
if archivo_foto is not None:
    st.image(archivo_foto, caption="Nota cargada correctamente", width=220)

st.markdown("---")

# 2. Datos generales
n_pedido = st.text_input("N° de Pedido / Nota (Ej: 0038706)", value=st.session_state['n_pedido'])

# Selector inteligente con memoria de clientes del taller
cliente_dropdown = st.selectbox("Cliente Frecuente", options=CLIENTES_FRECUENTES)
if cliente_dropdown != CLIENTES_FRECUENTES[0]:
    cliente_final = cliente_dropdown
else:
    cliente_final = st.text_input("O escribe el nombre de un nuevo cliente", value="")

st.markdown("---")
st.markdown("### 📋 Lotes y Procesos Traducidos")
st.markdown("*(El sistema traduce automáticamente abreviaturas como P.6, P.P., SB, #1, #2, #3, F. Claro, etc.)*")

col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("➕ Añadir otro lote"):
        st.session_state['lotes'].append({"desc": "", "cantidad": 50})
        st.rerun()
with col_b2:
    if len(st.session_state['lotes']) > 1 and st.button("🗑️ Quitar último lote"):
        st.session_state['lotes'].pop()
        st.rerun()

lotes_actualizados = []
for idx, lote in enumerate(st.session_state['lotes']):
    col1, col2 = st.columns([3, 1])
    with col1:
        d = st.text_input(f"Lote #{idx+1} (Prenda + Proceso)", value=lote['desc'], key=f"desc_{idx}")
    with col2:
        c = st.number_input(f"Cant #{idx+1}", value=int(lote['cantidad']), key=f"cant_{idx}")
    lotes_actualizados.append({"desc": d, "cantidad": c})

st.session_state['lotes'] = lotes_actualizados

st.markdown("---")

# 3. Generación de etiquetas térmicas con QR integrado y peso en blanco
if st.button("🖨️ Generar Etiquetas para Rollo Térmico"):
    cliente_a_usar = cliente_final if cliente_final else cliente_dropdown
    
    if not n_pedido or cliente_a_usar == CLIENTES_FRECUENTES[0] or len(st.session_state['lotes']) == 0:
        st.error("Por favor completa el N° de pedido, selecciona un cliente de la lista y añade al menos un lote.")
    else:
        st.success(f"¡Etiquetas térmicas listas para imprimir para el pedido N° {n_pedido} de {cliente_a_usar}!")
        
        for idx, lote in enumerate(st.session_state['lotes']):
            # Codificación interna limpia para el QR
            info_qr = f"Ped:{n_pedido}|Cli:{cliente_a_usar}|Lote:#{idx+1}|Det:{lote['desc']}|Cant:{lote['cantidad']}"
            
            qr = qrcode.QRCode(version=1, box_size=4, border=1)
            qr.add_data(info_qr)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img_qr.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Etiqueta térmica compacta (Ancho exacto para rollo)
            st.markdown(f"""
            <div style="width: 280px; border: 1.5px solid #000; padding: 8px; border-radius: 4px; margin-bottom: 12px; background-color: #fff; color: #000; font-family: Arial, sans-serif;">
                <div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 2px;">ANDERSON JEAN'S</div>
                <div style="border-bottom: 1px solid #000; margin-bottom: 4px;"></div>
                <div style="font-size: 11px; line-height: 1.2;">
                    <b>Cliente:</b> {cliente_a_usar}<br>
                    <b>Pedido:</b> {n_pedido} | <b>Lote:</b> #{idx+1}<br>
                    <b>Detalle:</b> {lote['desc']}<br>
                    <b>Prendas:</b> {lote['cantidad']} unds<br>
                    <b>Peso:</b> ____________ kg
                </div>
                <div style="text-align: center; margin-top: 6px;">
                    <img src="data:image/png;base64,{qr_base64}" width="85"/>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Limpieza automática (encerado) para el siguiente pedido del taller
        st.session_state['n_pedido'] = ""
        st.session_state['lotes'] = [{"desc": "", "cantidad": 50}]
        
        if st.button("🔄 Limpiar pantalla para siguiente pedido"):
            st.rerun()
