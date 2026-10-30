
        import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Andersson Jean's & Confecciones", page_icon="👖", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("Sistema Integral de Taller, Lavandería y Confección")

# BASE DE DATOS DE CLAVES Y ACCESOS
ACCESOS_DB = {
    "luis": {"nombre": "Luis (Chofer)", "tipo": "Lavanderia_Recepcion"},
    "luz": {"nombre": "Luz (Recepción)", "tipo": "Lavanderia_Recepcion"},
    "1111": {"nombre": "Patto (Manualidades)", "tipo": "Manualidades"},
    "2222": {"nombre": "Henry (Manualidades)", "tipo": "Manualidades"},
    "3333": {"nombre": "Wagner (Manualidades)", "tipo": "Manualidades"},
    "4444": {"nombre": "Geison (Manualidades)", "tipo": "Manualidades"},
    "mayorista": {"nombre": "Canal Mayorista", "tipo": "Confeccion_Lourds"},
    "cuenca": {"nombre": "Canal Cuenca", "tipo": "Confeccion_Lourds"},
    "bodega": {"nombre": "Bodega General", "tipo": "Confeccion_Lourds"},
    "admin": {"nombre": "Administrador (Jefe)", "tipo": "Admin"}
}

# Memoria global en sesión
if 'produccion_manualidades' not in st.session_state:
    st.session_state.produccion_manualidades = {
        "Patto": [], "Henry": [], "Wagner": [], "Geison": []
    }

if 'lotes_lavanderia' not in st.session_state:
    st.session_state.lotes_lavanderia = {}

if 'cortes_lourds' not in st.session_state:
    st.session_state.cortes_lourds = []

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
    st.write("Tome la foto de la nota de pedido, ingrese los datos y genere los stickers QR.")

    with st.form("form_recepcion_lavanderia", clear_on_submit=True):
        foto_nota = st.file_uploader("Tomar / Subir Foto de la Nota de Pedido", type=["jpg", "jpeg", "png"])
        nro_pedido = st.text_input("N° de Pedido / Nota (ej: 0038743)")
        cli = st.text_input("Cliente")
        prend = st.text_input("Modelo / Prenda")
        cant = st.number_input("Cantidad total de prendas", min_value=1, value=100)
        proc = st.text_input("Proceso / Lavado / Color")
        tarifa = st.number_input("Tarifa unitaria operario ($)", min_value=0.01, value=0.06)

        guardar_lote = st.form_submit_button("💾 Guardar Parada y Generar QR")
        
        if guardar_lote:
            if not nro_pedido.strip():
                st.error("❌ Por favor ingrese el número de pedido o nota.")
            else:
                # Verificador de duplicados
                pedido_existe = False
                for l in st.session_state.lotes_lavanderia.values():
                    if l.get('nro_pedido') == nro_pedido.strip():
                        pedido_existe = True
                        break
                
                if pedido_existe:
                    st.error(f"❌ Esta orden de pedido (N° {nro_pedido}) ya fue ingresada. Ingrese la siguiente nota de pedido.")
                else:
                    nuevo_id = str(len(st.session_state.lotes_lavanderia) + 1)
                    st.session_state.lotes_lavanderia[nuevo_id] = {
                        "id": nuevo_id, "nro_pedido": nro_pedido.strip(), "cliente": cli, 
                        "prenda": prend, "cantidad": cant, "proceso": proc, "precio": tarifa
                    }
                    st.success(f"✅ ¡Parada N° {nro_pedido} guardada con éxito y stickers listos!")

    if st.session_state.lotes_lavanderia:
        st.markdown("---")
        st.subheader("🏷️ Stickers QR Activos")
        for k, l in st.session_state.lotes_lavanderia.items():
            st.markdown(f"* **Pedido N° {l.get('nro_pedido', k)}** | Cliente: {l['cliente']} | {l['prenda']} ({l['cantidad']} un.) | Proceso: {l['proceso']}")
            qr_data = f"LOTE_{l.get('nro_pedido', k)}"
            img = qrcode.make(qr_data)
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), width=120, caption=f"Sticker QR - Pedido {l.get('nro_pedido', k)}")

# =====================================================================
# 2. MÓDULO: MANUALIDADES (OPERARIOS: Patto, Henry, Wagner, Geison)
# =====================================================================
elif tipo_user == "Manualidades":
    st.header(f"📱 Módulo Manualidades - {nombre_user}")
    st.write("Escanee o digite el código del lote para sumarlo al instante a su bitácora diaria:")

    with st.form("form_escaneo_manualidades", clear_on_submit=True):
        cod_lote = st.text_input("⚡ Digitar / Escanear Número de Pedido o Lote")
        btn_reg = st.form_submit_button("🚀 Registrar en mi Bitácora")

        if btn_reg and cod_lote:
            code_clean = cod_lote.strip().replace("LOTE_", "")
            
            # Buscar por ID o por N° de pedido
            lote_encontrado = None
            for k, l in st.session_state.lotes_lavanderia.items():
                if k == code_clean or l.get('nro_pedido') == code_clean:
                    lote_encontrado = l
                    break

            if lote_encontrado:
                total_pago = lote_encontrado['cantidad'] * lote_encontrado['precio']
                nombre_real = nombre_user.split(" ")[0]
                
                st.session_state.produccion_manualidades[nombre_real].append({
                    "lote_id": lote_encontrado.get('nro_pedido', lote_encontrado['id']),
                    "cliente": lote_encontrado['cliente'],
                    "detalle": f"{lote_encontrado['cantidad']} un. - {lote_encontrado['prenda']} ({lote_encontrado['proceso']})",
                    "total": total_pago
                })
                st.success(f"✅ ¡Pedido #{lote_encontrado.get('nro_pedido')} registrado! Se sumaron ${total_pago:.2f} a su cuenta.")
            else:
                st.error("❌ Código de lote o pedido no encontrado.")

    st.markdown("---")
    st.subheader("📊 Su Bitácora y Ganancias del Día")
    nombre_real = nombre_user.split(" ")[0]
    mis_registros = st.session_state.produccion_manualidades.get(nombre_real, [])

    if not mis_registros:
        st.info("_Aún no registra lotes hoy._")
    else:
        acumulado = 0
        for i, item in enumerate(mis_registros, 1):
            st.markdown(f"**{i}. Pedido #{item['lote_id']}** | {item['cliente']} | {item['detalle']} -> **${item['total']:.2f}**")
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
        if not st.session_state.cortes_lourds:
            st.info("No hay cortes registrados todavía.")
        else:
            for c in st.session_state.cortes_lourds:
                st.markdown(f"🔹 **Corte N° {c['corte']}** | Modelo: `{c['modelo']}` | Tallas: {c['tallas']} | Stock Disponible: **{c['stock']} un.**")

    elif opcion_lourds == "➕ Registrar Nuevo Corte":
        with st.form("form_nuevo_corte_lourds", clear_on_submit=True):
            n_corte = st.text_input("Número de Talonario de Corte (ej: 0000055)")
            n_modelo = st.text_input("Modelo de Corte (ej: Kasandra / Wayted)")
            n_tallas = st.text_input("Rango de Tallas (ej: 6 al 16)")
            n_cant = st.number_input("Cantidad total de prendas cortadas", min_value=1, value=100)
            foto_corte_img = st.file_uploader("Subir foto de la hoja de corte", type=["jpg", "jpeg", "png"])

            sub_corte = st.form_submit_button("📥 Guardar Corte en Bodega")
            if sub_corte and n_corte:
                # Verificar duplicado de corte
                corte_existe = any(c['corte'] == n_corte.strip() for c in st.session_state.cortes_lourds)
                if corte_existe:
                    st.error(f"❌ Este talonario de corte (N° {n_corte}) ya fue registrado anteriormente.")
                else:
                    st.session_state.cortes_lourds.append({
                        "corte": n_corte.strip(), "modelo": n_modelo, "tallas": n_tallas, "cantidad": n_cant, "stock": n_cant
                    })
                    st.success(f"✅ ¡Corte N° {n_corte} registrado exitosamente y formulario limpio!")

    elif opcion_lourds == "🚚 Registrar Salida de Mercadería":
        with st.form("form_salida_lourds", clear_on_submit=True):
            destino_salida = st.text_input("Destino / Cliente que retira")
            foto_salida = st.file_uploader("Tomar / Subir foto de la Hoja de Salida de Mercadería", type=["jpg", "jpeg", "png"])
            cant_sale = st.number_input("Cantidad de prendas que salen", min_value=1, value=10)
            
            if not st.session_state.cortes_lourds:
                st.warning("No hay cortes disponibles en bodega para descontar.")
                opc_cortes = []
            else:
                opc_cortes = [f"Corte #{c['corte']} - {c['modelo']} (Stock: {c['stock']})" for c in st.session_state.cortes_lourds]
            
            sel_c = st.selectbox("Seleccionar Lote de Corte", opc_cortes) if opc_cortes else None
            btn_despacho = st.form_submit_button("📉 Descontar Salida de Bodega")
            
            if btn_despacho and sel_c:
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
                    st.markdown(f"- Pedido #{item['lote_id']} | {item['cliente']} | {item['detalle']} -> **${item['total']:.2f}**")
                st.markdown(f"**Subtotal {op}: ${sub:.2f}**")
                total_general_taller += sub
                st.markdown("---")
        st.subheader(f"🏭 Total General a Pagar en Taller: ${total_general_taller:.2f}")

    elif admin_tab == "2. Andersson Jean's - Lavandería":
        st.subheader("🏷️ Control de Lotes Generados en Lavandería")
        if not st.session_state.lotes_lavanderia:
            st.info("No hay lotes registrados.")
        else:
            for k, l in st.session_state.lotes_lavanderia.items():
                st.markdown(f"- **Pedido N° {l.get('nro_pedido', k)}** | Cliente: {l['cliente']} | {l['prenda']} ({l['cantidad']} un.) | Proceso: {l['proceso']}")

    elif admin_tab == "3. Confección Lourd's (Stock y Cortes)":
        st.subheader("🧵 Inventario Vivo de Confección Lourd's")
        if not st.session_state.cortes_lourds:
            st.info("No hay cortes registrados.")
        else:
            for c in st.session_state.cortes_lourds:
                st.markdown(f"🔹 **Corte N° {c['corte']}** | Modelo: `{c['modelo']}` | Stock actual: **{c['stock']} un.**")

    elif admin_tab == "4. Historial de Salidas de Mercadería":
        st.subheader("🚚 Registro de Salidas de Bodega")
        if not st.session_state.salidas_mercaderia:
            st.info("Aún no hay salidas registradas.")
        else:
            for s in st.session_state.salidas_mercaderia:
                st.markdown(f"▫️ Destino: **{s['destino']}** | Modelo: {s['modelo']} | Cantidad: **{s['cantidad']} un.**")
