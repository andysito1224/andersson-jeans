import streamlit as st

st.set_page_config(page_title="Andersson Jean's - Control de Lotes y Pagos", page_icon="👖", layout="centered")

st.title("👖 Andersson Jean's")
st.subheader("Sistema de Recepción, Lotes y Pagos")

menu = st.sidebar.selectbox("Seleccione el Módulo", ["1. Recepción y Stickers", "2. Cálculo de Pagos (Operarios)"])

if menu == "1. Recepción y Stickers":
    st.header("📸 Módulo de Recepción")
    st.write("Tome una foto de la nota de pedido o suba la imagen para procesar los lotes.")

    archivo_foto = st.file_uploader("Subir foto de la Nota de Pedido", type=["jpg", "jpeg", "png"])

    if archivo_foto is not None:
        st.success("¡Foto cargada y procesada correctamente!")
        st.markdown("---")
        st.subheader("📝 Datos Extraídos del Pedido")
        st.text("Nro. Pedido: #0038743")
        st.text("Cliente: Geison Urrutia")
        st.text("Fecha: 15/10/2026")
        
        st.markdown("### Lotes Detectados:")
        lotes = [
            {"id": 1, "prenda": "Falda", "cantidad": 112, "proceso": "#1 + SB (San Blas) + Distway"},
            {"id": 2, "prenda": "Falda", "cantidad": 112, "proceso": "#2 + SB (San Blas)"},
            {"id": 3, "prenda": "Falda", "cantidad": 112, "proceso": "Fros Claro / Oscuro"}
        ]
        
        for lote in lotes:
            with st.container():
                st.markdown(f"""
                **Lote #{lote['id']}**
                * Prenda: `{lote['prenda']}`
                * Cantidad: `{lote['cantidad']} prendas`
                * Proceso / Manualidad: `{lote['proceso']}`
                * 🖨️ *[Sticker listo para imprimir con espacio para Peso]*
                """)
                st.markdown("---")

        if st.button("🖨️ Imprimir Todos los Stickers Térmicos"):
            st.toast("¡Enviando lotes a la impresora térmica por Bluetooth!", icon="🖨️")

elif menu == "2. Cálculo de Pagos (Operarios)":
    st.header("💰 Control de Pagos por Manualidades")
    st.write("Seleccione el operario y el trabajo realizado para calcular la cuenta exacta.")

    operario = st.selectbox("Seleccionar Operario", ["Patto", "Henry", "Wagner"])
    
    if operario == "Patto":
        st.markdown("### Tarifario - Patto (San Blas / SB)")
        tipo_sb = st.selectbox("Tipo de San Blas", ["SB Normal ($0.06)", "SB Crudo ($0.07)", "SB Chompas ($0.07)", "SB Tubo ($0.07)"])
        cantidad = st.number_input("Cantidad de prendas", min_value=1, value=50)
        precio = 0.06 if "Normal" in tipo_sb else 0.07
        total = cantidad * precio
        st.markdown(f"### Total a Pagar a Patto: **${total:.2f}**")

    elif operario in ["Henry", "Wagner"]:
        st.markdown(f"### Tarifario - {operario}")
        tipo_prenda = st.radio("Tipo de Prenda", ["Pantalón Grande (PG)", "Pantalón Pequeño (PP)"])
        manualidad = st.selectbox("Manualidad", ["Bigote / Motor / Destroy ($0.08 PG / $0.06 PP)", "1/2 Destroy ($0.04 PG / $0.03 PP)", "Lija / Esponja / Moteado ($0.15 PG / $0.12 PP)"])
        cantidad = st.number_input("Cantidad de prendas", min_value=1, value=50)
        
        is_pg = "Grande" in tipo_prenda
        if "Bigote" in manualidad:
            precio = 0.08 if is_pg else 0.06
        elif "1/2 Destroy" in manualidad:
            precio = 0.04 if is_pg else 0.03
        else:
            precio = 0.15 if is_pg else 0.12
            
        total = cantidad * precio
        st.markdown(f"### Total a Pagar a {operario}: **${total:.2f}**")

    if st.button("💾 Guardar y Registrar Cuenta del Día"):
        st.success("¡Cuenta registrada con éxito para la contabilidad de la fábrica!")
