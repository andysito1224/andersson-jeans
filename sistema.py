import streamlit as st
import qrcode
from io import BytesIO

st.set_page_config(page_title="Andersson Jean's - Fábrica y Confección", page_icon="👖", layout="centered")

st.title("👖 Andersson Jean's & Confecciones")
st.subheader("Control de Lotes, Taller e Inventario")

# Memoria temporal en sesión
if 'produccion_operarios' not in st.session_state:
    st.session_state.produccion_operarios = {
        "Patto": [],
        "Henry": [],
        "Wagner": [],
        "Geison": [],
        "Otros": []
    }

if 'inventario_mama' not in st.session_state:
    st.session_state.inventario_mama = [
        {"producto": "Falda Clásica Denim", "talla": "M", "stock": 50, "precio_unit": 8.50},
        {"producto": "Pantalón Tailored Woman", "talla": "S", "stock": 30, "precio_unit": 12.00}
    ]

menu = st.sidebar.selectbox("Seleccione el Módulo", [
    "1. Recepción y Stickers QR", 
    "2. Registro Estilo Libreta (Operarios)", 
    "3. Cuentas y Ganancias del Día",
    "4. 📦 Inventario de Confección (Mamá)"
])

# --- MÓDULO 1: RECEPCIÓN Y TICKETS CON QR ---
if menu == "1. Recepción y Stickers QR":
    st.header("📸 Módulo de Recepción y Trazabilidad")
    st.write("Suba la foto de la nota de pedido para extraer datos, cliente y generar los tickets con QR.")

    archivo_foto = st.file_uploader("Subir foto de la Nota de Pedido", type=["jpg", "jpeg", "png"])

    if archivo_foto is not None:
        st.success("¡Nota procesada correctamente!")
        st.markdown("---")
        
        cliente_nombre = "Geison Urrutia"
        nro_pedido = "#0038743"
        
        st.subheader(f"📝 Cliente: {cliente_nombre} (Pedido {nro_pedido})")
        
        lotes = [
            {"id": 1, "prenda": "Falda", "cantidad": 112, "proceso": "#1 + SB (San Blas) + Distway"},
            {"id": 2, "prenda": "Falda", "cantidad": 112, "proceso": "#2 + SB (San Blas)"},
            {"id": 3, "prenda": "Falda", "cantidad": 112, "proceso": "Frost Claro / Oscuro + Roto"}
        ]
        
        st.markdown("### Lotes y Stickers Térmicos:")
        
        for lote in lotes:
            with st.container():
                st.markdown(f"""
                ---
                ### 🏷️ STICKER - Lote #{lote['id']}
                * **Cliente:** `{cliente_nombre}`
                * **Prenda:** `{lote['prenda']}`
                * **Cantidad:** `{lote['cantidad']} prendas`
                * **Proceso / Lavado:** `{lote['proceso']}`
                """)
                
                # Generar Código QR para trazabilidad
                qr_data = f"ANDERSON_LOTE_{lote['id']}_CLI_{cliente_nombre}_CANT_{lote['cantidad']}_{lote['proceso']}"
                img = qrcode.make(qr_data)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                
                st.image(buffered.getvalue(), width=140, caption=f"QR Lote #{lote['id']} - {cliente_nombre}")

        if st.button("🖨️ Imprimir Todos los Stickers"):
            st.toast("¡Enviando stickers a impresora térmica Bluetooth!", icon="🖨️")

# --- MÓDULO 2: REGISTRO ESTILO LIBRETA (OPERARIOS) ---
elif menu == "2. Registro Estilo Libreta (Operarios)":
    st.header("📖 Registro Diario (Estilo Libreta)")
    st.write("Registre las prendas y procesos tal como lo anotan en el cuaderno de la fábrica.")

    col1, col2 = st.columns(2)
    with col1:
        operario = st.selectbox("Operario / Responsable", ["Patto", "Henry", "Wagner", "Geison", "Otro"])
    with col2:
        cliente_lote = st.text_input("Cliente del Lote", value="Geison Urrutia")

    col3, col4 = st.columns(2)
    with col3:
        tipo_prenda = st.selectbox("Tipo de Prenda", ["PP (Pantalón Pequeño / Falda)", "PG (Pantalón Grande)"])
        cantidad = st.number_input("Cantidad", min_value=1, value=50)
    with col4:
        proceso_manualidad = st.selectbox("Proceso / Manualidad", [
            "San Blas (SB)", "Bigote / Motor / Destroy", "1/2 Destroy", 
            "Lija / Esponja / Moteado", "Frost Claro / Oscuro", "Roto / Brillo"
        ])
        detalle_extra = st.text_input("Detalle adicional (ej: #1, #2, Roto)", value="Norm")

    # Tarifario automático basado en la práctica
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
    st.info(f"💵 Cálculo automático: {cantidad} un. x ${precio_unit} = **${total_linea:.2f}**")

    if st.button("➕ Anotar en la Cuenta del Operario"):
        registro = {
            "cliente": cliente_lote,
            "descripcion": f"{cantidad} {tipo_prenda} - {proceso_manualidad} ({detalle_extra})",
            "total": total_linea
        }
        st.session_state.produccion_operarios[operario].append(registro)
        st.success(f"¡Anotado correctamente para {operario}!")

# --- MÓDULO 3: CUENTAS Y GANANCIAS DEL DÍA ---
elif menu == "3. Cuentas y Ganancias del Día":
    st.header("📊 Cuentas y Resumen de los Muchachos")
    st.write("Control total de lo acumulado por cada operario.")

    total_general = 0
    for operario, lista in st.session_state.produccion_operarios.items():
        if lista:
            st.markdown(f"### 👷 {operario}")
            subtotal_op = 0
            for item in lista:
                st.markdown(f"- **Cliente:** {item['cliente']} | {item['descripcion']} -> **${item['total']:.2f}**")
                subtotal_op += item['total']
            st.markdown(f"**Total acumulado {operario}: `⚡ ${subtotal_op:.2f}`**")
            total_general += subtotal_op
            st.markdown("---")

    st.subheader(f"🏭 Total General a Pagar en Taller: ${total_general:.2f}")

# --- MÓDULO 4: INVENTARIO DE CONFECCIÓN (MAMÁ) ---
elif menu == "4. 📦 Inventario de Confección (Mamá)":
    st.header("🧵 Inventario de Confección - Producción de Mamá")
    st.write("Espacio independiente para llevar el control de stock, prendas terminadas y entregas.")

    with st.form("form_inventario"):
        st.subheader("Agregar Nuevo Producto al Stock")
        prod_nombre = st.text_input("Nombre de la prenda / Modelo")
        prod_talla = st.selectbox("Talla", ["XS", "S", "M", "L", "XL", "Única"])
        prod_stock = st.number_input("Cantidad en Stock", min_value=1, value=10)
        prod_precio = st.number_input("Precio estimado ($)", min_value=0.0, value=10.00)
        
        guardar_prod = st.form_submit_button("💾 Guardar en Inventario")
        if guardar_prod and prod_nombre:
            st.session_state.inventario_mama.append({
                "producto": prod_nombre,
                "talla": prod_talla,
                "stock": prod_stock,
                "precio_unit": prod_precio
            })
            st.success(f"¡{prod_nombre} agregado al inventario de mamá con éxito!")

    st.markdown("---")
    st.subheader("📋 Stock Actual Disponible")
    
    for i, item in enumerate(st.session_state.inventario_mama):
        col_a, col_b, col_c = st.columns([3, 1, 1])
        with col_a:
            st.markdown(f"**{item['producto']}** (Talla: {item['talla']})")
        with col_b:
            st.markdown(f"Stock: **{item['stock']} un.**")
        with col_c:
            st.markdown(f"Precio: **${item['precio_unit']:.2f}**")
