import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="Andersson Jean's - Control Operarios", page_icon="👖", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("Sistema de Escaneo Rápido de Lotes")

# BASE DE DATOS DE USUARIOS Y ROLES
ROLES_DB = {
    "1001": {"nombre": "Chofer / Logística", "rol": "Recepcion"},
    "1002": {"nombre": "Recepcionista", "rol": "Recepcion"},
    "1111": {"nombre": "Patto", "rol": "Operario"},
    "2222": {"nombre": "Henry", "rol": "Operario"},
    "3333": {"nombre": "Wagner", "rol": "Operario"},
    "4444": {"nombre": "Geison", "rol": "Operario"},
    "admin": {"nombre": "Administrador (Jefe)", "rol": "Admin"}
}

# Memoria global
if 'produccion_operarios' not in st.session_state:
    st.session_state.produccion_operarios = {
        "Patto": [], "Henry": [], "Wagner": [], "Geison": [], "Otros": []
    }

if 'lotes_oficiales' not in st.session_state:
    st.session_state.lotes_oficiales = {
        "1": {"id": 1, "cliente": "Geison Urrutia", "prenda": "3 Botones", "cantidad": 1350, "proceso": "Azul y Negro", "precio": 0.06},
        "2": {"id": 2, "cliente": "Geison Urrutia", "prenda": "Falda PP", "cantidad": 112, "proceso": "San Blas", "precio": 0.06}
    }

if 'inventario_confeccion' not in st.session_state:
    st.session_state.inventario_confeccion = [
        {"modelo": "Kasandra", "talla": "8", "stock": 48, "precio": 10.00},
    ]

if 'historial_salidas' not in st.session_state:
    st.session_state.historial_salidas = []

# --- LOGIN ---
if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None

if st.session_state.usuario_actual is None:
    st.markdown("### 🔐 Acceso al Sistema")
    ingreso_clave = st.text_input("Ingrese su Cédula o Clave personal", type="password")
    
    if st.button("🚀 Ingresar"):
        if ingreso_clave in ROLES_DB:
            st.session_state.usuario_actual = ROLES_DB[ingreso_clave]
            st.success(f"¡Bienvenido, {st.session_state.usuario_actual['nombre']}!")
            st.rerun()
        else:
            st.error("❌ Clave incorrecta.")
    st.stop()

nombre_user = st.session_state.usuario_actual['nombre']
rol_user = st.session_state.usuario_actual['rol']

st.sidebar.markdown(f"👤 **Usuario:** {nombre_user}")
st.sidebar.markdown(f"🏷️ **Perfil:** {rol_user}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.sidebar.markdown("---")

# ==========================================
# 1. RECEPCIÓN Y CHOFER (CREAR LOTES / QR)
# ==========================================
if rol_user == "Recepcion":
    st.header("📸 Ingreso de Paradas y Stickers QR")
    with st.form("form_rec"):
        foto = st.file_uploader("Foto de la Nota de Pedido", type=["jpg", "jpeg", "png"])
        cli = st.text_input("Cliente", value="Geison Urrutia")
        prend = st.text_input("Prenda / Modelo", value="3 Botones")
        cant = st.number_input("Cantidad de prendas", min_value=1, value=112)
        proc = st.text_input("Proceso / Lavado", value="San Blas")
        tarifa = st.number_input("Tarifa unitaria ($)", min_value=0.01, value=0.06)
        
        btn_crear = st.form_submit_button("💾 Guardar y Generar QR")
        if btn_crear:
            nuevo_id = str(len(st.session_state.lotes_oficiales) + 1)
            st.session_state.lotes_oficiales[nuevo_id] = {
                "id": nuevo_id, "cliente": cli, "prenda": prend, "cantidad": cant, "proceso": proc, "precio": tarifa
            }
            st.success(f"¡Lote #{nuevo_id} creado con éxito!")

    st.markdown("---")
    st.subheader("🏷️ Stickers Generados (Listos para imprimir)")
    for k, l in st.session_state.lotes_oficiales.items():
        st.markdown(f"* **Lote #{k}** | {l['cliente']} - {l['prenda']} ({l['cantidad']} un.) | Proceso: {l['proceso']}")
        qr_data = f"LOTE_{k}"
        img = qrcode.make(qr_data)
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), width=120, caption=f"QR Lote #{k}")

# ==========================================
# 2. OPERARIOS (PANTALLA DE ESCANEO RÁPIDO)
# ==========================================
elif rol_user == "Operario":
    st.header(f"📱 Escaneo de Producción - {nombre_user}")
    st.write("Escanea o digita el número del lote para registrarlo de inmediato en tu bitácora:")

    # Opción con la cámara del celular para tomar foto al QR directamente si lo desean
    foto_qr = st.camera_input("📷 Tomar foto al Sticker QR (Opcional)")

    # Entrada rápida por texto / número de lote
    with st.form("form_escaneo_rapido", clear_on_submit=True):
        codigo_escaneado = st.text_input("⚡ Número de Lote (ej: 1, 2, 3...)")
        btn_registrar = st.form_submit_button("🚀 Registrar y Sumar a mi Bitácora")
        
        if btn_registrar and codigo_escaneado:
            code_clean = codigo_escaneado.strip().replace("LOTE_", "")
            
            if code_clean in st.session_state.lotes_oficiales:
                lote = st.session_state.lotes_oficiales[code_clean]
                total_lote = lote['cantidad'] * lote['precio']
                
                # Guardar en la bitácora del operario
                st.session_state.produccion_operarios[nombre_user].append({
                    "lote_id": lote['id'],
                    "cliente": lote['cliente'],
                    "detalle": f"{lote['cantidad']} un. - {lote['prenda']} ({lote['proceso']})",
                    "total": total_lote
                })
                st.success(f"✅ ¡Lote #{lote['id']} registrado! Se sumaron ${total_lote:.2f} a tu bitácora.")
            else:
                st.error("❌ Lote no encontrado. Verifique el código.")

    st.markdown("---")
    st.subheader("📊 Tu Bitácora y Ganancias de Hoy")
    mis_reg = st.session_state.produccion_operarios.get(nombre_user, [])
    
    if not mis_reg:
        st.info("_Aún no tienes lotes registrados hoy. Ingresa tu código arriba._")
    else:
        total_dia = 0
        for idx, item in enumerate(mis_reg, 1):
            st.markdown(f"**{idx}. Lote #{item['lote_id']}** | {item['cliente']} | {item['detalle']} -> **${item['total']:.2f}**")
            total_dia += item['total']
        st.markdown(f"### ⚡ Total Generado Hoy: `💲 {total_dia:.2f}`")

# ==========================================
# 3. ADMINISTRADOR
# ==========================================
elif rol_user == "Admin":
    menu_admin = st.sidebar.selectbox("Panel Admin", ["Cuentas del Taller", "Inventario Mamá", "Salidas (4 Destinos)"])
    
    if menu_admin == "Cuentas del Taller":
        st.header("📊 Cuentas Generales")
        tot = 0
        for op, lst in st.session_state.produccion_operarios.items():
            if lst:
                sub = sum(x['total'] for x in lst)
                st.markdown(f"**{op}:** ${sub:.2f}")
                tot += sub
        st.subheader(f"Total Fábrica: ${tot:.2f}")
    elif menu_admin == "Inventario Mamá":
        st.header("🧵 Inventario de Confección")
        for i in st.session_state.inventario_confeccion:
            st.markdown(f"- {i['modelo']} (Talla {i['talla']}): {i['stock']} un.")
    elif menu_admin == "Salidas (4 Destinos)":
        st.header("🚚 Despachos")
        st.write("Control de salidas a Mayorista, Cuenca, TikTok y Clientes Fijos.")
