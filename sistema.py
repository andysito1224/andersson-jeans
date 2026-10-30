import streamlit as st
import qrcode
from io import BytesIO
import base64

st.set_page_config(page_title="Andersson Jean's - Stickers Térmicos", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("🏷️ Módulo de Registro y Stickers Térmicos")
st.markdown("Selecciona el cliente, ingresa el pedido y los lotes para imprimir directo en tu rollo térmico.")

# Lista completa de clientes frecuentes de tus talonarios
CLIENTES_FRECUENTES = [
    "-- Selecciona un cliente --",
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

# Inicializar estados de la sesión
if 'n_pedido' not in st.session_state:
    st.session_state['n_pedido'] = ""
if 'cliente_sel' not in st.session_state:
    st.session_state['cliente_sel'] = CLIENTES_FRECUENTES[0]
if 'tipo_prenda' not in st.session_state:
    st.session_state['tipo_prenda'] = "Pantalón Grande (P.6)"
if 'lotes' not in st.session_state:
    st.session_state['lotes'] = [{"desc": "Stone 1 + San Blas", "cantidad": 100}]

# 1. Subir foto opcional (solo como referencia visual en pantalla)
archivo_foto = st.file_uploader("Subir foto de la Nota (Opcional para referencia)", type=["jpg", "png", "jpeg"])
if archivo_foto is not None:
    st.image(archivo_foto, caption="Nota de referencia cargada", width=220)

st.markdown("---")

# 2. Datos generales del pedido
n_pedido = st.text_input("N° de Pedido / Nota", value=st.session_state['n_pedido'])

cliente_dropdown = st.selectbox("Cliente Frecuente", options=CLIENTES_FRECUENTES)
if cliente_dropdown != CLIENTES_FRECUENTES[0]:
    cliente_final = cliente_dropdown
else:
    cliente_final = st.text_input("O escribe el nombre del cliente", value="")

tipo_prenda = st.text_input("Prenda Principal (ej. Pantalón Grande [P.6], Pantalón Pequeño [P.P.], Vestido P.)", value=st.session_state['tipo_prenda'])

st.markdown("---")
st.markdown("### 📋 Desglose de Lotes / Procesos")

# Botones para agregar o quitar lotes dinámicamente
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
        d = st.text_input(f"Proceso Lote #{idx+1}", value=lote['desc'], key=f"desc_{idx}")
    with col2:
        c = st.number_input(f"Cant #{idx+1}", value=int(lote['cantidad']), key=f"cant_{idx}")
    lotes_actualizados.append({"desc": d, "cantidad": c})

st.session_state['lotes'] = lotes_actualizados

st.markdown("---")

# 3. Generación e impresión de etiquetas térmicas
if st.button("🖨️ Generar Etiquetas para Rollo Térmico"):
    cliente_a_usar = cliente_final if cliente_final else cliente_dropdown
    
    if not n_pedido or cliente_a_usar == CLIENTES_FRECUENTES[0] or len(st.session_state['lotes']) == 0:
        st.error("Por favor ingresa el número de pedido, selecciona un cliente y asegúrate de tener al menos un lote.")
    else:
        st.success(f"¡Etiquetas listas para imprimir para el pedido N° {n_pedido}!")
        
        for idx, lote in enumerate(st.session_state['lotes']):
            info_qr = f"Ped:{n_pedido}|Cli:{cliente_a_usar}|Prenda:{tipo_prenda}|Lote:#{idx+1}|Proc:{lote['desc']}|Cant:{lote['cantidad']}"
            
            qr = qrcode.QRCode(version=1, box_size=4, border=1)
            qr.add_data(info_qr)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img_qr.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            st.markdown(f"""
            <div style="width: 280px; border: 1.5px solid #000; padding: 8px; border-radius: 4px; margin-bottom: 12px; background-color: #fff; color: #000; font-family: Arial, sans-serif;">
                <div style="text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 2px;">ANDERSON JEAN'S</div>
                <div style="border-bottom: 1px solid #000; margin-bottom: 4px;"></div>
                <div style="font-size: 11px; line-height: 1.2;">
                    <b>Cliente:</b> {cliente_a_usar}<br>
                    <b>Pedido:</b> {n_pedido} | <b>Lote:</b> #{idx+1}<br>
                    <b>Prenda:</b> {tipo_prenda}<br>
                    <b>Proceso:</b> {lote['desc']}<br>
                    <b>Prendas:</b> {lote['cantidad']} unds<br>
                    <b>Peso:</b> ____________ kg
                </div>
                <div style="text-align: center; margin-top: 6px;">
                    <img src="data:image/png;base64,{qr_base64}" width="85"/>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Limpieza automática (encerado de pantalla para el siguiente pedido)
        st.session_state['n_pedido'] = ""
        st.session_state['cliente_sel'] = CLIENTES_FRECUENTES[0]
        st.session_state['lotes'] = [{"desc": "", "cantidad": 50}]
        
        if st.button("🔄 Limpiar y listo para el siguiente pedido"):
            st.rerun()
