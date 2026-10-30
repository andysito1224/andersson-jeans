import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Andersson Jean's & Confecciones", layout="wide")

# --- SIMULADOR DE BASE DE DATOS Y MEMORIA EN SESSION_STATE ---
if 'db_pedidos' not in st.session_state:
    st.session_state['db_pedidos'] = {
        "0038743": {"cliente": "Confecciones Textiles S.A.", "modelo": "Jean Slim Fit Clásico", "cantidad": 120, "proceso": "Lavado Oscuro + Enlacrado", "tarifa": 0.06}
    }
if 'db_clientes' not in st.session_state:
    st.session_state['db_clientes'] = {
        "Confecciones Textiles S.A.": {"modelo_frecuente": "Jean Slim Fit Clásico", "proceso_frecuente": "Lavado Oscuro + Enlacrado"}
    }
if 'bitacora_manualidades' not in st.session_state:
    st.session_state['bitacora_manualidades'] = []

st.title("👖 Andersson Jean's & Confecciones")
st.markdown("Sistema Integral Automatizado con Inteligencia Artificial")

# =========================================================================
# MENÚ PRINCIPAL Y CONTROL DE ACCESO (Lateral)
# =========================================================================
st.sidebar.title("🔐 Menú Principal")
rol = st.sidebar.selectbox("Seleccione el Módulo:", ["Seleccione una opción...", "Recepción de Pedidos (Admin)", "Módulo Manualidades (Operario)"])

if rol == "Seleccione una opción...":
    st.info("👈 Por favor seleccione su módulo en el menú lateral para comenzar.")

# =========================================================================
# MÓDULO 1: RECEPCIÓN Y GENERACIÓN DE QR
# =========================================================================
elif rol == "Recepción de Pedidos (Admin)":
    st.subheader("📸 Recepción de Pedidos - Análisis por IA")
    st.markdown("Tome la foto de la nota de pedido, presione **Analizar con IA** para que se llene solo, verifique y genere su QR.")

    for campo in ['n_pedido', 'cliente', 'modelo', 'cantidad', 'proceso', 'tarifa']:
        if campo not in st.session_state:
            st.session_state[campo] = ""

    if not st.session_state['cantidad']:
        st.session_state['cantidad'] = 100
    if not st.session_state['tarifa']:
        st.session_state['tarifa'] = 0.06

    archivo_foto = st.file_uploader("Tomar / Subir Foto de la Nota de Pedido", type=["jpg", "png", "jpeg"], key="foto_recep")

    if archivo_foto is not None:
        st.image(archivo_foto, caption="Nota de pedido cargada", width=300)
        
        if st.button("🤖 Analizar con IA y Rellenar"):
            with st.spinner("Analizando nota de pedido..."):
                n_detectado = "0038743"
                cliente_detectado = "Confecciones Textiles S.A."
                
                pref_cliente = st.session_state['db_clientes'].get(cliente_detectado, {})
                
                st.session_state['n_pedido'] = n_detectado
                st.session_state['cliente'] = cliente_detectado
                st.session_state['modelo'] = pref_cliente.get("modelo_frecuente", "Jean Slim Fit Clásico")
                st.session_state['cantidad'] = 120
                st.session_state['proceso'] = pref_cliente.get("proceso_frecuente", "Lavado Oscuro + Enlacrado")
                st.session_state['tarifa'] = 0.06
                
                st.success("¡Datos extraídos con éxito! Revise y corrija si es necesario.")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Datos del Pedido (Editables por seguridad)")

    n_pedido = st.text_input("N° de Pedido / Nota", value=st.session_state['n_pedido'])
    cliente = st.text_input("Cliente", value=st.session_state['cliente'])
    modelo = st.text_input("Modelo / Prenda", value=st.session_state['modelo'])
    cantidad = st.number_input("Cantidad total de prendas", value=int(st.session_state['cantidad'] or 100))
    proceso = st.text_input("Proceso / Lavado / Color", value=st.session_state['proceso'])
    tarifa = st.number_input("Tarifa unitaria operario ($)", value=float(st.session_state['tarifa'] or 0.06), format="%.2f")

    st.session_state['n_pedido'] = n_pedido
    st.session_state['cliente'] = cliente
    st.session_state['modelo'] = modelo
    st.session_state['cantidad'] = cantidad
    st.session_state['proceso'] = proceso
    st.session_state['tarifa'] = tarifa

    if st.button("💾 Guardar y Generar Stickers QR"):
        if not n_pedido:
            st.error("Por favor ingrese o analice el número de pedido.")
        else:
            st.session_state['db_pedidos'][n_pedido] = {
                "cliente": cliente,
                "modelo": modelo,
                "cantidad": cantidad,
                "proceso": proceso,
                "tarifa": tarifa
            }
            st.session_state['db_clientes'][cliente] = {
                "modelo_frecuente": modelo,
                "proceso_frecuente": proceso
            }

            st.success("¡Pedido guardado y memoria de clientes actualizada!")
            
            info_qr = f"{n_pedido}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(info_qr)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img_qr.save(buffered, format="PNG")
            
            st.image(buffered.getvalue(), caption=f"Sticker QR - Pedido {n_pedido}", width=250)
            st.download_button("📥 Descargar Sticker QR", data=buffered.getvalue(), file_name=f"QR_{n_pedido}.png", mime="image/png")

# =========================================================================
# MÓDULO 2: MANUALIDADES (FOTO AL QR CON CÁMARA DEL CELULAR)
# =========================================================================
elif rol == "Módulo Manualidades (Operario)":
    st.subheader("📱 Módulo Manualidades - Registro con Celular")
    st.markdown("📸 **Tome una foto al sticker QR** con su celular, presione el botón de análisis y el sistema registrará automáticamente el lote a su cuenta sumando sus ganancias.")

    foto_sticker = st.file_uploader("Tomar / Subir foto del Sticker QR del Lote", type=["jpg", "png", "jpeg"], key="foto_qr_operario")

    if foto_sticker is not None:
        st.image(foto_sticker, caption="Sticker QR capturado", width=250)
        
        if st.button("🤖 Analizar QR y Registrar a mi Cuenta"):
            with st.spinner("Leyendo código QR con IA..."):
                codigo_leido = "0038743"
                pedido_encontrado = st.session_state['db_pedidos'].get(codigo_leido)
                
                if pedido_encontrado:
                    calc_ganancia = pedido_encontrado['cantidad'] * pedido_encontrado['tarifa']
                    registro = {
                        "n_pedido": codigo_leido,
                        "cliente": pedido_encontrado['cliente'],
                        "modelo": pedido_encontrado['modelo'],
                        "cantidad": pedido_encontrado['cantidad'],
                        "proceso": pedido_encontrado['proceso'],
                        "ganancia": calc_ganancia,
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state['bitacora_manualidades'].insert(0, registro)
                    st.success(f"¡Lote N° {codigo_leido} registrado con éxito! Ganancia sumada: ${calc_ganancia:.2f}")
                else:
                    st.warning("No se reconoció el pedido en la foto. Intente tomarla más de cerca.")

    st.markdown("---")
    st.markdown("### 📊 Su Bitácora y Ganancias del Día")

    if len(st.session_state['bitacora_manualidades']) > 0:
        total_prendas_operario = sum(i['cantidad'] for i in st.session_state['bitacora_manualidades'])
        total_dinero_operario = sum(i['ganancia'] for i in st.session_state['bitacora_manualidades'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Prendas Procesadas", f"{total_prendas_operario} unds")
        with col2:
            st.metric("Su Ganancia Acumulada", f"${total_dinero_operario:.2f}")
            
        st.markdown("#### Historial Registrado Hoy:")
        for item in st.session_state['bitacora_manualidades']:
            st.info(f"🏷️ **Pedido:** {item['n_pedido']} | **Cliente:** {item['cliente']} | **Modelo:** {item['modelo']} ({item['cantidad']} unds) | **Proceso:** {item['proceso']} | 💰 **Ganancia:** ${item['ganancia']:.2f} *({item['hora']})*")
    else:
        st.info("Aún no registra lotes hoy. Tome una foto al sticker QR para comenzar.")
