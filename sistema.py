import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Andersson Jean's & Confecciones", page_icon="👖", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("Sistema Integral de Taller, Lavandería y Confección")

# BASE DE DATOS DE CLAVES Y ACCESOS
ACCESOS_DB = {
    # Lavandería (Chofer y Recepción)
    "luis": {"nombre": "Luis (Chofer)", "tipo": "Lavanderia_Recepcion"},
    "luz": {"nombre": "Luz (Recepción)", "tipo": "Lavanderia_Recepcion"},
    
    # Operarios de Manualidades
    "1111": {"nombre": "Patto (Manualidades)", "tipo": "Manualidades"},
    "2222": {"nombre": "Henry (Manualidades)", "tipo": "Manualidades"},
    "3333": {"nombre": "Wagner (Manualidades)", "tipo": "Manualidades"},
    "4444": {"nombre": "Geison (Manualidades)", "tipo": "Manualidades"},
    
    # Canales de Confección Lourd's (Mamá)
    "mayorista": {"nombre": "Canal Mayorista", "tipo": "Confeccion_Lourds"},
    "cuenca": {"nombre": "Canal Cuenca", "tipo": "Confeccion_Lourds"},
    "bodega": {"nombre": "Bodega General", "tipo": "Confeccion_Lourds"},
    
    # Administrador Total (Tú)
    "admin": {"nombre": "Administrador (Jefe)", "tipo": "Admin"}
}

# Memoria global en sesión
if 'produccion_manualidades' not in st.session_state:
    st.session_state.produccion_manualidades = {
        "Patto": [], "Henry": [], "Wagner": [], "Geison": []
    }

if 'lotes_lavanderia' not in st.session_state:
    st.session_state.lotes_lavanderia = {
        "1": {"id": 1, "cliente": "Geison Urrutia", "prenda": "3 Botones", "cantidad": 1350, "proceso": "Azul y Negro", "precio": 0.06}
    }

if 'cortes_lourds' not in st.session_state:
    st.session_state.cortes_lourds = [
        {"corte": "0000045", "modelo": "3 Botones / Extias", "tallas": "6 al 26", "cantidad": 1350, "stock": 1350}
    ]

if 'salidas_mercaderia' not in st.session_state:
    st.session_state.salidas_mercaderia = []

# --- CONTROL DE ACCESO (LOGIN) ---
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None:
    st.markdown("### 🔐 Acceso al Sistema")
    ingreso_clave = st.text_input("Ingrese su clave o cédula de acceso", type="password")
    
    if st.button("🚀 Ingresar"):
        clave_limpia = ingreso_clave.strip().lower()
        if clave_limpia in ACCESOS_DB:
            st.session_state.usuario_actual = ACCESOS_DB[clave_limpia]
            st.success(f"¡Bienvenido, {st.session_state.usuario_actual['nombre']}!")
            st.rerun()
        else:
            st.error("❌ Clave incorrecta. Verifique sus datos.")
    st.stop()

nombre_user = st.session_state.usuario_actual['nombre']
tipo_user = st.session_state.usuario_actual['tipo']

st.sidebar.markdown(f"👤 **Usuario:** {nombre_user}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.sidebar.markdown("---")

# =====================================================================
# 1. MÓDULO: ANDERSSON JEAN'S LAVANDERÍA (CHOFER 'luis' Y RECEPCIÓN 'luz')
# =====================================================================
if tipo_user == "Lavanderia_Recepcion":
    st.header("📸 Andersson Jean's - Recepción de Pedidos y QR")
    st.write("Tome la foto de la nota de pedido, ingrese los datos y genere los stickers QR para el taller.")

    with st.form("form_recepcion_lavanderia"):
        foto_nota = st.file_uploader("Tomar / Subir Foto de la Nota de Pedido", type=["jpg", "jpeg", "png"])
        cli = st.text_input("Cliente", value="Geison Urrutia")
        prend = st.text_input("Modelo / Prenda", value="Baggy / 3 Botones")
        cant = st.number_input("Cantidad total de prendas", min_value=1, value=112)
        proc = st.text_input("Proceso / Lavado / Color", value="San Blas / Azul")
        tarifa = st.number_input("Tarifa unitaria operario ($)", min_value=0.01, value=0.06)

        guardar_lote = st.form_submit_button("💾 Guardar Parada y Generar QR")
        if guardar_lote:
            nuevo_id = str(len(st.session_state.lotes_lavanderia) + 1)
            st.session_state.lotes_lavanderia[nuevo_id] = {
                "id": nuevo_id, "cliente": cli, "prenda": prend, "cantidad": cant, "proceso": proc, "precio": tarifa
            }
            st.success(f"¡Parada y Stickers del Lote #{nuevo_id} generados con éxito!")

    st.markdown("---")
    st.subheader("🏷️ Stickers QR Activos")
    for k, l in st.session_state.lotes_lavanderia.items():
        st.markdown(f"* **Lote #{k}** | {l['cliente']} - {l['prenda']} ({l['cantidad']} un.) | Proceso: {l['proceso']}")
        qr_data = f"LOTE_{k}"
        img = qrcode.make(qr_data)
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), width=120, caption=f"Sticker QR Lote #{k}")

# =====================================================================
# 2. MÓDULO: MANUALIDADES (OPERARIOS: Patto, Henry, Wagner, Geison)
# =====================================================================
elif tipo_user == "Manualidades":
    st.header(f"📱 Módulo Manualidades - {nombre_user}")
    st.write("Escanee o digite el código del lote para sumarlo al instante a su bitácora diaria:")

    foto_qr = st.camera_input("📷 Tomar foto al Sticker QR (Opcional)")

    with st.form("form_escaneo_manualidades", clear_on_submit=True):
        cod_lote = st.text_input("⚡ Digitar / Escanear Número de Lote (ej: 1, 2...)")
        btn_reg = st.form_submit_button("🚀 Registrar en mi Bitácora")

        if btn_reg and cod_lote:
            code_clean = cod_lote.strip().replace("LOTE_", "")
            if code_clean in st.session_state.lotes_lavanderia:
                lote = st.session_state.lotes_lavanderia[code_clean]
                total_pago = lote['cantidad'] * lote['precio']
                
                nombre_real = nombre_user.split(" ")[0]
                st.session_state.produccion_manualidades[nombre_real].append({
                    "lote_id": lote['id'],
                    "cliente": lote['cliente'],
                    "detalle": f"{lote['cantidad']} un. - {lote['prenda']} ({lote['proceso']})",
                    "total": total_pago
                })
                st.success(f"✅ ¡Lote #{lote['id']} registrado! Se sumaron ${total_pago:.2f} a su cuenta.")
            else:
                st.error("❌ Código de lote no encontrado.")

    st.markdown("---")
    st.subheader("📊 Su Bitácora y Ganancias del Día")
    nombre_real = nombre_user.split(" ")[0]
    mis_registros = st.session_state.produccion_manualidades.get(nombre_real, [])

    if not mis_registros:
        st.info("_Aún no registra lotes hoy._")
    else:
        acumulado = 0
        for i, item in enumerate(mis_registros, 1):
            st.markdown(f"**{i}. Lote #{item['lote_id']}** | {item['cliente']} | {item['detalle']} -> **${item['total']:.2f}**")
            acumulado += item['total']
        st.markdown(f"### ⚡ Total Acumulado Hoy: `💲 {acumulado:.2f}`")

# =====================================================================
# 3. MÓDULO: CONFECCIÓN LOURD'S (MAYORISTA, CUENCA, BODEGA)
# =====================================================================
elif tipo_user == "Confeccion_Lourds":
    st.header(f"🧵 Confección Lourd's - Canal: {nombre_user}")
    st.write("Registro de cortes de talonario y salidas de mercadería con soporte fotográfico.")

    opcion_lourds = st.selectbox("Seleccione Operación", ["📦 Ver Inventario de Cortes", "➕ Registrar Corte Nuevo", "🚚 Registrar Salida de Mercadería"])

    if opcion_lourds == "📦 Ver Inventario de Cortes":
        st.subheader("📋 Stock Actual en Bodega Lourd's")
        for c in st.session_state.cortes_lourds:
            st.markdown(f"🔹 **Corte N° {c['corte']}** | Modelo: `{c['modelo']}` | Tallas: {c['tallas']} | Stock Disponible: **{c['stock']} un.**")

    elif opcion_lourds == "➕ Registrar Nuevo Corte":
        with st.form("form_nuevo_corte_lourds"):
            n_corte = st.text_input("Número de Talonario de Corte (ej: 0000055)")
            n_modelo = st.text_input("Modelo de Corte (ej: Kasandra / Wayted)")
            n_tallas = st.text_input("Rango de Tallas (ej: 6 al 16)", value="6 al 16")
            n_cant = st.number_input("Cantidad total de prendas cortadas", min_value=1, value=100)
            foto_corte_img = st.file_uploader("Subir foto de la hoja de corte", type=["jpg", "jpeg", "png"])

            sub_corte = st.form_submit_button("📥 Guardar Corte en Bodega")
            if sub_corte and n_corte:
                st.session_state.cortes_lourds.append({
                    "corte": n_corte, "modelo": n_modelo, "tallas": n_tallas, "cantidad": n_cant, "stock": n_cant
                })
                st.success(f"¡Corte N° {n_corte} registrado exitosamente en la bodega de Lourd's!")

    elif opcion_lourds == "🚚 Registrar Salida de Mercadería":
        with st.form("form_salida_lourds"):
            destino_salida = st.text_input("Destino / Cliente que retira", value="Mayorista / Cuenca")
            foto_salida = st.file_uploader("Tomar / Subir foto de la Hoja de Salida de Mercadería", type=["jpg", "jpeg", "png"])
            cant_sale = st.number_input("Cantidad de prendas que salen", min_value=1, value=10)
            
            opc_cortes = [f"Corte #{c['corte']} - {c['modelo']} (Stock: {c['stock']})" for c in st.session_state.cortes_lourds]
            sel_c = st.selectbox("Seleccionar Lote de Corte", opc_cortes)

            btn_despacho = st.form_submit_button("📉 Descontar Salida de Bodega")
            if btn_despacho:
                idx = opc_cortes.index(sel_c)
                if st.session_state.cortes_lourds[idx]['stock'] >= cant_sale:
                    st.session_state.cortes_lourds[idx]['stock'] -= cant_sale
                    st.session_state.salidas_mercaderia.append({
                        "destino": destino_salida, "modelo": st.session_state.cortes_lourds[idx]['modelo'], "cantidad": cant_sale
                    })
                    st.success(f"¡Salida registrada! Se descontaron {cant_sale} unidades. Stock restante: {st.session_state.cortes_lourds[idx]['stock']} un.")
                else:
                    st.error("❌ Stock insuficiente en este corte.")

# =====================================================================
# 4. MÓDULO ADMINISTRADOR (TÚ COMO JEFE - CLAVE 'admin')
# =====================================================================
elif tipo_user == "Admin":
    st.header("👑 Panel de Administración General (Jefe)")
    
    admin_tab = st.sidebar.selectbox("Sección Admin", [
        "1. Reporte de Manualidades (Operarios)", 
        "2. Andersson Jean's - Lavandería", 
        "3. Confección Lourd's (Stock y Cortes)",
        "4. Historial de Salidas de Mercadería"
    ])

    if admin_tab == "1. Reporte de Manualidades (Operarios)":
        st.subheader("📊 Reporte de Producción de los Muchachos")
        total_general_taller = 0
        for op, lista in st.session_state.produccion_manualidades.items():
            if lista:
                st.markdown(f"### 👷 Operario: {op}")
                sub = sum(x['total'] for x in lista)
                for item in lista:
                    st.markdown(f"- Lote #{item['lote_id']} | {item['cliente']} | {item['detalle']} -> **${item['total']:.2f}**")
                st.markdown(f"**Subtotal {op}: ${sub:.2f}**")
                total_general_taller += sub
                st.markdown("---")
        st.subheader(f"🏭 Total General a Pagar en Taller: ${total_general_taller:.2f}")

    elif admin_tab == "2. Andersson Jean's - Lavandería":
        st.subheader("🏷️ Control de Lotes Generados en Lavandería")
        for k, l in st.session_state.lotes_lavanderia.items():
            st.markdown(f"- **Lote #{k}** | Cliente: {l['cliente']} | {l['prenda']} ({l['cantidad']} un.) | Proceso: {l['proceso']}")

    elif admin_tab == "3. Confección Lourd's (Stock y Cortes)":
        st.subheader("🧵 Inventario Vivo de Confección Lourd's")
        for c in st.session_state.cortes_lourds:
            st.markdown(f"🔹 **Corte N° {c['corte']}** | Modelo: `{c['modelo']}` | Stock actual: **{c['stock']} un.**")

    elif admin_tab == "4. Historial de Salidas de Mercadería":
        st.subheader("🚚 Registro de Salidas de Bodega")
        if not st.session_state.salidas_mercaderia:
            st.info("Aún no hay salidas registradas.")
        else:
            for s in st.session_state.salidas_mercaderia:
                st.markdown(f"▫️ Destino: **{s['destino']}** | Modelo: {s['modelo']} | Cantidad: **{s['cantidad']} un.**")
