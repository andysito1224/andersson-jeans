import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="Andersson Jean's - Control por Roles", page_icon="👖", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("Sistema Inteligente de Taller y Bodega")

# BASE DE DATOS DE USUARIOS Y ROLES ESPECÍFICOS
ROLES_DB = {
    # Chofer y Recepción (Ingreso de Lotes y QR)
    "1001": {"nombre": "Chofer / Logística", "rol": "Recepcion"},
    "1002": {"nombre": "Recepcionista", "rol": "Recepcion"},
    
    # Operarios de Manualidades
    "1111": {"nombre": "Patto", "rol": "Operario"},
    "2222": {"nombre": "Henry", "rol": "Operario"},
    "3333": {"nombre": "Wagner", "rol": "Operario"},
    "4444": {"nombre": "Geison", "rol": "Operario"},
    
    # Administradores (Tú y familia - Control total e inventario mamá)
    "admin": {"nombre": "Administrador (Jefe)", "rol": "Admin"}
}

# Memoria global en sesión
if 'produccion_operarios' not in st.session_state:
    st.session_state.produccion_operarios = {
        "Patto": [], "Henry": [], "Wagner": [], "Geison": [], "Otros": []
    }

if 'lotes_oficiales' not in st.session_state:
    st.session_state.lotes_oficiales = [
        {"id": 1, "cliente": "Geison Urrutia", "prenda": "3 Botones", "cantidad": 1350, "proceso": "Azul y Negro", "precio": 0.06}
    ]

if 'inventario_confeccion' not in st.session_state:
    st.session_state.inventario_confeccion = [
        {"modelo": "Kasandra", "talla": "8", "stock": 48, "precio": 10.00},
        {"modelo": "Modelo A", "talla": "10", "stock": 24, "precio": 10.00},
    ]

if 'historial_salidas' not in st.session_state:
    st.session_state.historial_salidas = []

# --- CONTROL DE ACCESO (LOGIN) ---
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None:
    st.markdown("### 🔐 Acceso Autorizado")
    ingreso_clave = st.text_input("Ingrese su Cédula o Clave personal", type="password")
    
    if st.button("🚀 Ingresar"):
        if ingreso_clave in ROLES_DB:
            st.session_state.usuario_actual = ROLES_DB[ingreso_clave]
            st.success(f"¡Bienvenido, {st.session_state.usuario_actual['nombre']}!")
            st.rerun()
        else:
            st.error("❌ Clave o cédula incorrecta.")
    st.stop()

# Barra lateral informativa y cierre de sesión
nombre_user = st.session_state.usuario_actual['nombre']
rol_user = st.session_state.usuario_actual['rol']

st.sidebar.markdown(f"👤 **Usuario:** {nombre_user}")
st.sidebar.markdown(f"🏷️ **Perfil:** {rol_user}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.sidebar.markdown("---")

# ==========================================
# 1. MENÚ PARA CHOFER Y RECEPCIÓN
# ==========================================
if rol_user == "Recepcion":
    st.header("📸 Módulo de Recepción y Paradas (Chofer / Recepción)")
    st.write("Tome la foto de la nota de pedido, ingrese los datos y genere los stickers con QR para el taller.")

    with st.form("form_recepcion_parada"):
        foto_nota = st.file_uploader("Tomar / Subir Foto de la Nota de Pedido", type=["jpg", "jpeg", "png"])
        cliente_p = st.text_input("Nombre del Cliente", value="Geison Urrutia")
        modelo_p = st.text_input("Modelo o Prenda", value="Baggy / 3 Botones")
        cantidad_p = st.number_input("Cantidad de prendas de esta parada", min_value=1, value=112)
        proceso_p = st.text_input("Proceso / Lavado / Color", value="Azul / Negro")
        tarifa_p = st.number_input("Tarifa unitaria operario ($)", min_value=0.01, value=0.06)

        guardar_parada = st.form_submit_button("💾 Guardar Parada y Generar QR (Nuevo)")
        
        if guardar_parada:
            nuevo_id = len(st.session_state.lotes_oficiales) + 1
            st.session_state.lotes_oficiales.append({
                "id": nuevo_id, "cliente": cliente_p, "prenda": modelo_p, 
                "cantidad": cantidad_p, "proceso": proceso_p, "precio": tarifa_p
            })
            st.success(f"¡Parada #{nuevo_id} guardada con éxito en el sistema! Lista para imprimir.")

    st.markdown("---")
    st.subheader("🏷️ Lotes y Stickers QR Listos para Imprimir")
    for l in st.session_state.lotes_oficiales:
        st.markdown(f"""
        * **Lote #{l['id']}** | Cliente: **{l['cliente']}** | Prenda: `{l['prenda']}` | Cantidad: **{l['cantidad']} un.** | Proceso: `{l['proceso']}`
        """)
        qr_data = f"LOTE_ID_{l['id']}_CANT_{l['cantidad']}"
        img = qrcode.make(qr_data)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        st.image(buffered.getvalue(), width=130, caption=f"QR Parada #{l['id']}")

# ==========================================
# 2. MENÚ PARA OPERARIOS (MANUALIDADES)
# ==========================================
elif rol_user == "Operario":
    st.header(f"📱 Panel de Producción - {nombre_user}")
    st.write("Escanee el código QR del siguiente lote o selecciónelo en la lista para sumarlo a su bitácora:")

    if not st.session_state.lotes_oficiales:
        st.info("No hay lotes activos asignados por recepción todavía.")
    else:
        # Menú desplegable continuo para elegir lotes actuales o nuevos
        opciones = [f"Lote #{l['id']} - {l['cliente']} ({l['prenda']} - {l['cantidad']} un.) - {l['proceso']}" for l in st.session_state.lotes_oficiales]
        lote_sel = st.selectbox("Seleccionar Lote Siguiente / Escaneado", opciones)
        
        id_lote = int(lote_sel.split("Lote #")[1].split(" -")[0])
        info = next(l for l in st.session_state.lotes_oficiales if l['id'] == id_lote)

        st.info(f"""
        📌 **Detalle del Lote Seleccionado:**
        * **Cliente:** {info['cliente']}
        * **Prenda:** {info['prenda']} ({info['cantidad']} un.)
        * **Proceso:** {info['proceso']}
        * **Total generado para ti:** **${(info['cantidad'] * info['precio']):.2f}**
        """)

        if st.button("🚀 Confirmar y Registrar en mi Bitácora"):
            st.session_state.produccion_operarios[nombre_user].append({
                "lote_id": info['id'],
                "cliente": info['cliente'],
                "detalle": f"{info['cantidad']} un. - {info['prenda']} ({info['proceso']})",
                "total": info['cantidad'] * info['precio']
            })
            st.success("¡Lote registrado con éxito! Ya puedes escanear o seleccionar el siguiente lote.")

    st.markdown("---")
    st.subheader("📊 Tu Bitácora y Ganancias de Hoy")
    mis_reg = st.session_state.produccion_operarios.get(nombre_user, [])
    if not mis_reg:
        st.write("_Aún no tienes registros hoy._")
    else:
        total_dia = 0
        for idx, item in enumerate(mis_reg, 1):
            st.markdown(f"**{idx}. Lote #{item['lote_id']}** | {item['cliente']} | {item['detalle']} -> **${item['total']:.2f}**")
            total_dia += item['total']
        st.markdown(f"### ⚡ Total Generado Hoy: `💲 {total_dia:.2f}`")

# ==========================================
# 3. MENÚ PARA ADMINISTRADOR (TÚ Y FAMILIA)
# ==========================================
elif rol_user == "Admin":
    menu_admin = st.sidebar.selectbox("Panel Administrativo", [
        "1. Cuentas Generales del Taller",
        "2. 📦 Inventario y Bodega (Mamá)",
        "3. 🚚 Registrar Salida (4 Destinos)"
    ])

    if menu_admin == "1. Cuentas Generales del Taller":
        st.header("📊 Resumen General de Operarios")
        total_fabrica = 0
        for op, lista in st.session_state.produccion_operarios.items():
            if lista:
                st.markdown(f"### 👷 Operario: {op}")
                sub_op = sum(x['total'] for x in lista)
                for item in lista:
                    st.markdown(f"- Lote #{item['lote_id']} ({item['cliente']}): {item['detalle']} -> **${item['total']:.2f}**")
                st.markdown(f"**Subtotal {op}: ${sub_op:.2f}**")
                total_fabrica += sub_op
                st.markdown("---")
        st.subheader(f"🏭 Total General a Pagar en Fábrica: ${total_fabrica:.2f}")

    elif menu_admin == "2. 📦 Inventario y Bodega (Mamá)":
        st.header("🧵 Inventario en Vivo - Confección de Mamá")
        st.write("Control directo de cortes, bodega y stock disponible para la venta.")

        with st.expander("➕ Registrar Nuevo Corte de Talonario"):
            with st.form("form_corte_mama"):
                m_modelo = st.text_input("Modelo / Nombre del Corte (ej: Kasandra, Wayted)")
                m_talla = st.selectbox("Talla", ["6", "8", "10", "12", "14", "16", "18", "20", "28", "30", "32", "34"])
                m_cant = st.number_input("Cantidad de prendas", min_value=1, value=48)
                m_precio = st.number_input("Precio base ($)", min_value=0.0, value=10.00)
                
                btn_corte = st.form_submit_button("📥 Agregar a Bodega de Mamá")
                if btn_corte and m_modelo:
                    st.session_state.inventario_confeccion.append({
                        "modelo": m_modelo, "talla": str(m_talla), "stock": m_cant, "precio": m_precio
                    })
                    st.success(f"¡Corte agregado correctamente a la bodega de mamá!")

        st.markdown("---")
        st.subheader("📋 Stock Actual en Bodega")
        for item in st.session_state.inventario_confeccion:
            st.markdown(f"🔹 **Modelo:** {item['modelo']} | **Talla:** {item['talla']} | Stock: **{item['stock']} un.** | Precio: **${item['precio']:.2f}**")

    elif menu_admin == "3. 🚚 Registrar Salida (4 Destinos)":
        st.header("🚚 Despacho y Descuento de Bodega")
        st.write("Descuenta stock automáticamente hacia los 4 canales de venta oficiales:")

        if not st.session_state.inventario_confeccion:
            st.warning("No hay inventario disponible.")
        else:
            with st.form("form_salidas_admin"):
                destinos = ["Mayorista", "Cuenca", "TikTok", "Clientes Fijos"]
                canal = st.selectbox("Canal de Destino", destinos)
                
                opciones_stock = [f"{i['modelo']} - Talla {i['talla']} (Disponibles: {i['stock']} un.)" for i in st.session_state.inventario_confeccion]
                prod_sel = st.selectbox("Seleccionar Prenda", opciones_stock)
                
                q_salida = st.number_input("Cantidad a despachar", min_value=1, value=10)
                
                ejecutar_salida = st.form_submit_button("📉 Descontar de Bodega")
                if ejecutar_salida:
                    idx = opciones_stock.index(prod_sel)
                    actual = st.session_state.inventario_confeccion[idx]
                    
                    if actual['stock'] >= q_salida:
                        st.session_state.inventario_confeccion[idx]['stock'] -= q_salida
                        st.session_state.historial_salidas.append({
                            "destino": canal, "modelo": actual['modelo'], "talla": actual['talla'], "cantidad": q_salida
                        })
                        st.success(f"¡Despacho registrado! Se descontaron {q_salida} unidades para **{canal}**. Stock restante: {st.session_state.inventario_confeccion[idx]['stock']} un.")
                    else:
                        st.error(f"❌ Stock insuficiente. Solo quedan {actual['stock']} unidades.")
