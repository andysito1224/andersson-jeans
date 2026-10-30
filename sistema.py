import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="Andersson Jean's - Control y Confección", page_icon="👖", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("Control de Taller, Operarios e Inventario en Vivo (Mamá)")

# Base de datos de operarios
OPERARIOS_DB = {
    "1111": {"nombre": "Patto", "rol": "Operario"},
    "2222": {"nombre": "Henry", "rol": "Operario"},
    "3333": {"nombre": "Wagner", "rol": "Operario"},
    "4444": {"nombre": "Geison", "rol": "Operario"},
    "admin": {"nombre": "Administrador (Jefe)", "rol": "Admin"}
}

# Memoria global en sesión
if 'produccion_operarios' not in st.session_state:
    st.session_state.produccion_operarios = {
        "Patto": [], "Henry": [], "Wagner": [], "Geison": [], "Otros": []
    }

if 'lotes_oficiales' not in st.session_state:
    st.session_state.lotes_oficiales = [
        {"id": 45, "cliente": "Geison Urrutia", "prenda": "3 Botones / Extias", "cantidad": 1350, "proceso": "Azul y Negro", "precio": 0.06}
    ]

# INVENTARIO EN VIVO DE CONFECCIÓN (MAMÁ) - Basado en los tickets de corte
if 'inventario_confeccion' not in st.session_state:
    st.session_state.inventario_confeccion = [
        # Ejemplo inicial basado en tus notas de corte recientes
        {"modelo": "Kasandra", "talla": "8", "stock": 48, "precio": 10.00},
        {"modelo": "Kasandra", "talla": "10", "stock": 48, "precio": 10.00},
        {"modelo": "Kasandra", "talla": "12", "stock": 48, "precio": 10.00},
        {"modelo": "Kasandra", "talla": "14", "stock": 48, "precio": 10.00},
        {"modelo": "Modelo A", "talla": "8", "stock": 24, "precio": 10.00},
        {"modelo": "Modelo A", "talla": "10", "stock": 24, "precio": 10.00},
        {"modelo": "Modelo A", "talla": "12", "stock": 24, "precio": 10.00},
        {"modelo": "Modelo A", "talla": "14", "stock": 24, "precio": 10.00},
    ]

# Historial de salidas / ventas a los 4 destinos
if 'historial_salidas' not in st.session_state:
    st.session_state.historial_salidas = []

# --- CONTROL DE ACCESO (LOGIN) ---
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None:
    st.markdown("### 🔐 Acceso al Sistema")
    ingreso_clave = st.text_input("Ingrese su Cédula o Clave personal", type="password")
    
    if st.button("🚀 Ingresar"):
        if ingreso_clave in OPERARIOS_DB:
            st.session_state.usuario_actual = OPERARIOS_DB[ingreso_clave]
            st.success(f"¡Bienvenido, {st.session_state.usuario_actual['nombre']}!")
            st.rerun()
        else:
            st.error("❌ Clave incorrecta.")
    st.stop()

# Barra lateral
nombre_user = st.session_state.usuario_actual['nombre']
rol_user = st.session_state.usuario_actual['rol']

st.sidebar.markdown(f"👤 **Usuario:** {nombre_user}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.sidebar.markdown("---")

# Menú según rol
if rol_user == "Admin":
    menu = st.sidebar.selectbox("Módulos de Administrador", [
        "1. Crear Lotes y Stickers QR", 
        "2. Cuentas Generales del Taller",
        "3. 📦 Inventario y Bodega (Mamá)",
        "4. 🚚 Registrar Salida (Ventas / Destinos)"
    ])
else:
    menu = st.sidebar.selectbox("Módulos de Operario", [
        "📱 Escanear / Seleccionar Lote Asignado", 
        "📊 Mi Bitácora y Ganancias del Día"
    ])

# --- ADMIN: CREAR LOTES Y GENERAR QR ---
if menu == "1. Crear Lotes y Stickers QR":
    st.header("📸 Recepción y Asignación de Lotes Oficiales")
    with st.form("nuevo_lote_form"):
        cli = st.text_input("Nombre del Cliente", value="Geison Urrutia")
        pre = st.text_input("Modelo o Prenda", value="3 Botones / Baggy")
        can = st.number_input("Cantidad exacta", min_value=1, value=100)
        pro = st.text_input("Proceso / Lavado", value="Azul / Negro")
        pre_uni = st.number_input("Tarifa unitaria operario ($)", min_value=0.01, value=0.06)
        
        guardar_lote = st.form_submit_button("➕ Registrar Lote")
        if guardar_lote:
            nuevo_id = len(st.session_state.lotes_oficiales) + 1
            st.session_state.lotes_oficiales.append({
                "id": nuevo_id, "cliente": cli, "prenda": pre, "cantidad": can, "proceso": pro, "precio": pre_uni
            })
            st.success(f"¡Lote registrado con éxito!")

    st.markdown("### Lotes Activos")
    for l in st.session_state.lotes_oficiales:
        st.markdown(f"- **Lote #{l['id']}** | Cliente: {l['cliente']} | {l['prenda']} ({l['cantidad']} un.) - {l['proceso']}")

# --- OPERARIO: ESCANEAR / SELECCIONAR LOTE ---
elif menu == "📱 Escanear / Seleccionar Lote Asignado":
    st.header(f"📱 Producción - {nombre_user}")
    if not st.session_state.lotes_oficiales:
        st.warning("No hay lotes activos asignados.")
    else:
        opciones = [f"Lote #{l['id']} - {l['cliente']} ({l['prenda']} - {l['cantidad']} un.)" for l in st.session_state.lotes_oficiales]
        elegido = st.selectbox("Seleccione el Lote", opciones)
        id_sel = int(elegido.split("Lote #")[1].split(" -")[0])
        lote_info = next(l for l in st.session_state.lotes_oficiales if l['id'] == id_sel)

        st.info(f"Cantidad fija: **{lote_info['cantidad']} prendas** | Valor: **${lote_info['cantidad']*lote_info['precio']:.2f}**")

        if st.button("🚀 Confirmar y Sumar a mi Bitácora"):
            st.session_state.produccion_operarios[nombre_user].append({
                "lote_id": lote_info['id'], "cliente": lote_info['cliente'],
                "detalle": f"{lote_info['cantidad']} un. - {lote_info['prenda']}",
                "total": lote_info['cantidad'] * lote_info['precio']
            })
            st.success("¡Registrado en tu bitácora con éxito!")

elif menu == "📊 Mis Bitácora y Ganancias del Día":
    st.header(f"📊 Bitácora de {nombre_user}")
    mis_reg = st.session_state.produccion_operarios.get(nombre_user, [])
    total_m = sum(x['total'] for x in mis_reg)
    for r in mis_reg:
        st.markdown(f"- Lote #{r['lote_id']} | {r['detalle']} -> **${r['total']:.2f}**")
    st.markdown(f"### ⚡ Total Ganado Hoy: `💲 {total_m:.2f}`")

elif menu == "2. Cuentas Generales del Taller":
    st.header("📊 Cuentas Totales de la Fábrica")
    total_f = 0
    for op, lista in st.session_state.produccion_operarios.items():
        if lista:
            sub = sum(x['total'] for x in lista)
            st.markdown(f"**{op}:** ${sub:.2f}")
            total_f += sub
    st.subheader(f"🏭 Total General Fábrica: ${total_f:.2f}")

# --- ADMIN: INVENTARIO Y BODEGA (MAMÁ) ---
elif menu == "3. 📦 Inventario y Bodega (Mamá)":
    st.header("🧵 Inventario en Vivo - Confección de Mamá")
    st.write("Control de prendas terminadas listas para ofrecer y vender.")

    # Agregar nuevo corte recibido
    with st.expander("➕ Registrar Nuevo Corte en Bodega"):
        with st.form("form_nuevo_corte"):
            c_modelo = st.text_input("Modelo (ej: Kasandra, Wayted, Baggy)")
            c_talla = st.selectbox("Talla", ["6", "8", "10", "12", "14", "16", "18", "20", "28", "30", "32", "34"])
            c_cant = st.number_input("Cantidad de prendas cortadas", min_value=1, value=48)
            c_precio = st.number_input("Precio estimado ($)", min_value=0.0, value=10.00)
            
            sub_corte = st.form_submit_button("📥 Agregar a Bodega")
            if sub_corte and c_modelo:
                st.session_state.inventario_confeccion.append({
                    "modelo": c_modelo, "talla": str(c_talla), "stock": c_cant, "precio": c_precio
                })
                st.success(f"¡Se agregaron {c_cant} unidades del modelo {c_modelo} talla {c_talla} a la bodega!")

    st.markdown("---")
    st.subheader("📋 Stock Actual Disponible en Bodega")
    for idx, item in enumerate(st.session_state.inventario_confeccion):
        st.markdown(f"🔹 **Modelo:** {item['modelo']} | **Talla:** {item['talla']} | Stock Disponible: **{item['stock']} un.** | Precio: **${item['precio']:.2f}**")

    if st.session_state.historial_salidas:
        st.markdown("---")
        st.subheader("🚚 Últimas Salidas / Descuentos Registrados")
        for s in st.session_state.historial_salidas[-5:]:
            st.markdown(f"▫️ Destino: **{s['destino']}** | {s['cantidad']} un. de {s['modelo']} (Talla {s['talla']})")

# --- ADMIN: REGISTRAR SALIDAS A LOS 4 DESTINOS ---
elif menu == "4. 🚚 Registrar Salida (Ventas / Destinos)":
    st.header("🚚 Despacho y Descuento de Inventario")
    st.write("Selecciona el modelo y la cantidad que sale hacia los diferentes canales de venta:")

    if not st.session_state.inventario_confeccion:
        st.warning("No hay productos en el inventario.")
    else:
        with st.form("form_salida"):
            destinos_disponibles = ["Mayorista", "Cuenca", "TikTok", "Clientes Fijos"]
            destino_elegido = st.selectbox("Canal de Destino", destinos_disponibles)
            
            # Opciones de inventario
            opciones_inv = [f"{i['modelo']} - Talla {i['talla']} (Stock: {i['stock']} un.)" for i in st.session_state.inventario_confeccion]
            prod_elegido_str = st.selectbox("Seleccionar Prenda", opciones_inv)
            
            cant_salida = st.number_input("Cantidad a descontar", min_value=1, value=10)
            
            btn_descontar = st.form_submit_button("📉 Despachar y Descontar de Bodega")
            if btn_descontar:
                # Buscar índice del producto seleccionado
                idx_encontrado = opciones_inv.index(prod_elegido_str)
                prod_actual = st.session_state.inventario_confeccion[idx_encontrado]
                
                if prod_actual['stock'] >= cant_salida:
                    # Descontar stock
                    st.session_state.inventario_confeccion[idx_encontrado]['stock'] -= cant_salida
                    # Registrar en historial
                    st.session_state.historial_salidas.append({
                        "destino": destino_elegido,
                        "modelo": prod_actual['modelo'],
                        "talla": prod_actual['talla'],
                        "cantidad": cant_salida
                    })
                    st.success(f"¡Despacho registrado con éxito! Se descontaron {cant_salida} unidades para **{destino_elegido}**. Stock actual restante: {st.session_state.inventario_confeccion[idx_encontrado]['stock']} un.")
                else:
                    st.error(f"❌ Error: No hay suficiente stock. Solo quedan {prod_actual['stock']} unidades disponibles.")
        st.markdown(f"- **{item['producto']}** (Talla: {item['talla']}) | Stock: **{item['stock']} un.** | Precio: **${item['precio_unit']:.2f}**")
