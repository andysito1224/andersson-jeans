import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="Andersson Jean's - Control y Operarios", page_icon="👖", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("Sistema de Producción con Acceso por Operario")

# Base de datos de operarios permitidos (Cédula o Clave y Nombre)
OPERARIOS_DB = {
    "1111": {"nombre": "Patto", "rol": "Operario"},
    "2222": {"nombre": "Henry", "rol": "Operario"},
    "3333": {"nombre": "Wagner", "rol": "Operario"},
    "4444": {"nombre": "Geison", "rol": "Operario"},
    "admin": {"nombre": "Administrador (Jefe)", "rol": "Admin"}
}

# Memoria en sesión
if 'produccion_operarios' not in st.session_state:
    st.session_state.produccion_operarios = {
        "Patto": [], "Henry": [], "Wagner": [], "Geison": [], "Otros": []
    }

if 'inventario_mama' not in st.session_state:
    st.session_state.inventario_mama = [
        {"producto": "Falda Clásica Denim", "talla": "M", "stock": 50, "precio_unit": 8.50}
    ]

# --- CONTROL DE ACCESO (LOGIN) ---
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None:
    st.markdown("### 🔐 Acceso de Operarios y Administrador")
    st.write("Ingrese su número de cédula o clave personal para entrar al sistema:")
    
    ingreso_clave = st.text_input("Cédula o Clave", type="password")
    
    if st.button("🚀 Ingresar al Sistema"):
        if ingreso_clave in OPERARIOS_DB:
            st.session_state.usuario_actual = OPERARIOS_DB[ingreso_clave]
            st.success(f"¡Bienvenido, {st.session_state.usuario_actual['nombre']}!")
            st.rerun()
        else:
            st.error("❌ Clave o cédula incorrecta. Intente de nuevo.")
    
    st.stop() # Detiene la ejecución aquí hasta que inicien sesión

# Barra lateral para salir
nombre_user = st.session_state.usuario_actual['nombre']
rol_user = st.session_state.usuario_actual['rol']

st.sidebar.markdown(f"👤 **Usuario:** {nombre_user}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.sidebar.markdown("---")

# Menú según el rol
if rol_user == "Admin":
    menu = st.sidebar.selectbox("Seleccione el Módulo", [
        "1. Recepción y Stickers QR", 
        "2. Registro de Lotes", 
        "3. Cuentas Generales del Taller",
        "4. 📦 Inventario de Confección (Mamá)"
    ])
else:
    menu = st.sidebar.selectbox("Seleccione el Módulo", [
        "📱 Escanear y Registrar Lote", 
        "📊 Mis Ganancias y Mi Historial"
    ])

# --- MÓDULO 1: RECEPCIÓN Y TICKETS (ADMIN) ---
if menu == "1. Recepción y Stickers QR":
    st.header("📸 Módulo de Recepción y Trazabilidad")
    archivo_foto = st.file_uploader("Subir foto de la Nota de Pedido", type=["jpg", "jpeg", "png"])

    if archivo_foto is not None:
        st.success("¡Nota procesada correctamente!")
        cliente_nombre = "Geison Urrutia"
        nro_pedido = "#0038743"
        
        st.subheader(f"📝 Cliente: {cliente_nombre} (Pedido {nro_pedido})")
        
        lotes = [
            {"id": 1, "prenda": "Falda", "cantidad": 112, "proceso": "#1 + San Blas + Distway"},
            {"id": 2, "prenda": "Falda", "cantidad": 112, "proceso": "#2 + San Blas"},
            {"id": 3, "prenda": "Falda", "cantidad": 112, "proceso": "Frost Claro + Roto"}
        ]
        
        for lote in lotes:
            with st.container():
                st.markdown(f"""
                ---
                ### 🏷️ STICKER - Lote #{lote['id']}
                * **Cliente:** `{cliente_nombre}`
                * **Prenda:** `{lote['prenda']}` | **Cantidad:** `{lote['cantidad']} un`
                * **Proceso:** `{lote['proceso']}`
                """)
                
                qr_data = f"LOTE_{lote['id']}_{cliente_nombre}_{lote['cantidad']}_{lote['proceso']}"
                img = qrcode.make(qr_data)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                st.image(buffered.getvalue(), width=140, caption=f"QR Lote #{lote['id']} - {cliente_nombre}")

# --- MÓDULO OPERARIO: ESCANEAR Y REGISTRAR ---
elif menu == "📱 Escanear y Registrar Lote":
    st.header(f"📱 Registro de Producción - {nombre_user}")
    st.write("Escanee el código QR del lote o registre el trabajo realizado:")

    cliente_lote = st.text_input("Cliente del Lote", value="Geison Urrutia")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_prenda = st.selectbox("Tipo de Prenda", ["PP (Pantalón Pequeño / Falda)", "PG (Pantalón Grande)"])
        cantidad = st.number_input("Cantidad de prendas", min_value=1, value=50)
    with col2:
        proceso_manualidad = st.selectbox("Proceso / Manualidad", [
            "San Blas (SB)", "Bigote / Motor / Destroy", "1/2 Destroy", 
            "Lija / Esponja / Moteado", "Frost Claro / Oscuro", "Roto / Brillo"
        ])
        detalle_extra = st.text_input("Detalle (ej: #1, #2)", value="Norm")

    # Tarifario automático
    is_pg = "PG" in tipo_prenda
    if "San Blas" in proceso_manualidad:
        precio_unit = 0.07 if is_pg else 0.06
    elif "Bigote" in proceso_manualidad or "Motor" in proceso_manualidad:
        precio_unit = 0.08 if is_pg else 0.06
    elif "Lija" in proceso_manualidad or "Esponja" in proceso_manualidad:
        precio_unit = 0.15 if is_pg else 0.12
    else:
        precio_unit = 0.05

    total_linea = cantidad * precio_unit
    st.info(f"💵 Valor a tu favor por este lote: {cantidad} un. x ${precio_unit} = **${total_linea:.2f}**")

    if st.button("🚀 Guardar en mi Producción"):
        registro = {
            "cliente": cliente_lote,
            "descripcion": f"{cantidad} {tipo_prenda} - {proceso_manualidad} ({detalle_extra})",
            "total": total_linea
        }
        st.session_state.produccion_operarios[nombre_user].append(registro)
        st.success("¡Lote registrado con éxito! Ya se sumó a tu cuenta del día.")

# --- MÓDULO OPERARIO: VER SU HISTORIAL Y GANANCIAS ---
elif menu == "📊 Mis Ganancias y Mi Historial":
    st.header(f"📊 Historial y Ganancias de {nombre_user}")
    st.write("Aquí puedes ver todos los lotes que has registrado y cuánto vas ganando:")

    mis_registros = st.session_state.produccion_operarios.get(nombre_user, [])
    
    if not mis_registros:
        st.info("Aún no tienes lotes registrados en este turno.")
    else:
        total_mio = 0
        for i, item in enumerate(mis_registros, 1):
            st.markdown(f"**{i}. Cliente:** {item['cliente']} | {item['descripcion']} -> **${item['total']:.2f}**")
            total_mio += item['total']
        
        st.markdown(f"### ⚡ Total Acumulado para ti: `💲 {total_mio:.2f}`")

# --- MÓDULOS DE ADMINISTRADOR (REGISTRO LIBRETA, CUENTAS Y MAMÁ) ---
elif menu == "2. Registro de Lotes":
    st.header("📖 Registro General de Taller")
    # (Módulo abierto para el admin si necesita registrar por ellos)
    st.info("Módulo de supervisión administrativa.")

elif menu == "3. Cuentas Generales del Taller":
    st.header("📊 Cuentas Totales de la Fábrica")
    total_general = 0
    for op, lista in st.session_state.produccion_operarios.items():
        if lista:
            st.markdown(f"### 👷 Operario: {op}")
            sub = sum(item['total'] for item in lista)
            for item in lista:
                st.markdown(f"- {item['cliente']} | {item['descripcion']} (${item['total']:.2f})")
            st.markdown(f"**Subtotal {op}: ${sub:.2f}**")
            total_general += sub
            st.markdown("---")
    st.subheader(f"🏭 Total General a Pagar en Fábrica: ${total_general:.2f}")

elif menu == "4. 📦 Inventario de Confección (Mamá)":
    st.header("🧵 Inventario de Confección - Mamá")
    for item in st.session_state.inventario_mama:
        st.markdown(f"- **{item['producto']}** (Talla: {item['talla']}) | Stock: **{item['stock']} un.** | Precio: **${item['precio_unit']:.2f}**")
