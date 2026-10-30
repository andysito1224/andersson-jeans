import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Andersson Jean's & Confecciones", layout="wide")

# --- SIMULADOR DE BASE DE DATOS LOCAL EN SESSION_STATE ---
if 'db_pedidos' not in st.session_state:
    st.session_state['db_pedidos'] = {}  # Guarda pedidos por N° de pedido
if 'db_clientes' not in st.session_state:
    st.session_state['db_clientes'] = {
        "Confecciones Textiles S.A.": {"modelo_frecuente": "Jean Slim Fit Clásico", "proceso_frecuente": "Lavado Oscuro + Enlacrado"}
    }
if 'bitacora_manualidades' not in st.session_state:
    st.session_state['bitacora_manualidades'] = []

st.title("👖 Andersson Jean's & Confecciones")
st.markdown("Sistema Integral Automatizado con Inteligencia Artificial")

# Pestañas para separar la Recepción y el Módulo de Manualidades
pestana_recepcion, pestana_manualidades = st.tabs(["📸 1. Recepción y Generación QR", "📱 2. Módulo Manualidades (Escaneo QR)"])

# =========================================================================
# SECCIÓN 1: RECEPCIÓN Y GENERACIÓN DE QR CON IA
# =========================================================================
with pestana_recepcion:
    st.subheader("Recepción de Pedidos - Análisis por IA")
    st.markdown("1. Sube o toma la foto de la nota. 2. Presiona **Analizar con IA** para llenar todo solo. 3. Guarda y genera tu QR.")

    # Inicializar st.session_state para los campos si no existen
    for campo in ['n_pedido', 'cliente', 'modelo', 'cantidad', 'proceso', 'tarifa']:
        if campo not in st.session_state:
            st.session_state[campo] = ""

    if not st.session_state['cantidad']:
        st.session_state['cantidad'] = 100
    if not st.session_state['tarifa']:
        st.session_state['tarifa'] = 0.06

    archivo_foto = st.file_uploader("Tomar / Subir Foto de la Nota de Pedido", type=["jpg", "png", "jpeg"], key="foto_recepcion")

    if archivo_foto is not None:
        st.image(archivo_foto, caption="Nota de pedido cargada", width=300)
        
        # Botón de análisis con IA
        if st.button("🤖 Analizar con IA y Rellenar"):
            with st.spinner("Analizando nota de pedido..."):
                # Simulación de extracción automática por IA
                n_detectado = "0038743"
                cliente_detectado = "Confecciones Textiles S.A."
                
                # Consultamos la memoria de clientes
                pref_cliente = st.session_state['db_clientes'].get(cliente_detectado, {})
                
                st.session_state['n_pedido'] = n_detectado
                st.session_state['cliente'] = cliente_detectado
                st.session_state['modelo'] = pref_cliente.get("modelo_frecuente", "Jean Slim Fit Clásico")
                st.session_state['cantidad'] = 120
                st.session_state['proceso'] = pref_cliente.get("proceso_frecuente", "Lavado Oscuro + Enlacrado")
                st.session_state['tarifa'] = 0.06
                
                st.success("¡Datos extraídos con éxito! Verifique y edite si es necesario.")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Datos del Pedido (Editables por seguridad)")

    n_pedido = st.text_input("N° de Pedido / Nota", value=st.session_state['n_pedido'])
    cliente = st.text_input("Cliente", value=st.session_state['cliente'])
    modelo = st.text_input("Modelo / Prenda", value=st.session_state['modelo'])
    cantidad = st.number_input("Cantidad total de prendas", value=int(st.session_state['cantidad'] or 100))
    proceso = st.text_input("Proceso / Lavado / Color", value=st.session_state['proceso'])
    tarifa = st.number_input("Tarifa unitaria operario ($)", value=float(st.session_state['tarifa'] or 0.06), format="%.2f")

    # Sincronizamos cambios manuales
    st.session_state['n_pedido'] = n_pedido
    st.session_state['cliente'] = cliente
    st.session_state['modelo'] = modelo
    st.session_state['cantidad'] = cantidad
    st.session_state['proceso'] = proceso
    st.session_state['tarifa'] = tarifa

    st.markdown("---")

    if st.button("💾 Guardar y Generar Stickers QR"):
        if not n_pedido:
            st.error("Por favor ingrese o analice el número de pedido.")
        else:
            # Guardamos en la base de datos para que manualidades lo reconozca al escanear
            st.session_state['db_pedidos'][n_pedido] = {
                "cliente": cliente,
                "modelo": modelo,
                "cantidad": cantidad,
                "proceso": proceso,
                "tarifa": tarifa
            }
            
            # Guardamos preferencias en memoria de clientes
            st.session_state['db_clientes'][cliente] = {
                "modelo_frecuente": modelo,
                "proceso_frecuente": proceso
            }

            st.success("¡Guardado correctamente! Generando sticker QR...")
            
            info_qr = f"{n_pedido}" # Guardamos el número de pedido para lectura rápida con pistola
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(info_qr)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img_qr.save(buffered, format="PNG")
            
            st.image(buffered.getvalue(), caption=f"Sticker QR - Pedido {n_pedido}", width=250)
            st.download_button(
                label="📥 Descargar Sticker QR",
                data=buffered.getvalue(),
                file_name=f"QR_{n_pedido}.png",
                mime="image/png"
            )

# =========================================================================
# SECCIÓN 2: MÓDULO MANUALIDADES (ESCANEO DE QR AUTOMÁTICO)
# =========================================================================
with pestana_manualidades:
    st.subheader("Módulo Manualidades - Registro por Escaneo QR")
    st.markdown("⚡ **Escanee el código QR del sticker** con su pistola o digite el número de pedido. Se registrará automáticamente a su cuenta y sumará su ganancia.")

    # Formulario optimizado para escaneo rápido
    with st.form(key="form_manualidades", clear_on_submit=True):
        codigo_escanear = st.text_input("Pase el láser del escáner aquí (N° de Pedido):", placeholder="Ej: 0038743")
        btn_registrar = st.form_submit_button("🚀 Registrar a mi Cuenta")

    if btn_registrar and codigo_escanear:
        # Buscamos si el pedido existe en el sistema
        pedido_encontrado = st.session_state['db_pedidos'].get(codigo_escanear)
        
        if pedido_encontrado:
            calc_ganancia = pedido_encontrado['cantidad'] * pedido_encontrado['tarifa']
            registro = {
                "n_pedido": codigo_escanear,
                "cliente": pedido_encontrado['cliente'],
                "modelo": pedido_encontrado['modelo'],
                "cantidad": pedido_encontrado['cantidad'],
                "proceso": pedido_encontrado['proceso'],
                "ganancia": calc_ganancia,
                "hora": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state['bitacora_manualidades'].insert(0, registro)
            st.success(f"¡Lote N° {codigo_escanear} agregado con éxito! Ganancia sumada: ${calc_ganancia:.2f}")
            st.rerun()
        else:
            # Opción de emergencia por si escanean un código que no pasó por recepción
            st.warning(f"El pedido '{codigo_escanear}' no está registrado en el sistema. Ingrese los datos rápidos:")
            cant_emergencia = st.number_input("Cantidad de prendas", value=100, key="emg_cant")
            tarifa_emergencia = st.number_input("Tarifa unitaria ($)", value=0.06, key="emg_tarifa", format="%.2f")
            
            if st.button("Guardar y sumar de emergencia"):
                calc_ganancia = cant_emergencia * tarifa_emergencia
                registro = {
                    "n_pedido": codigo_escanear,
                    "cliente": "Cliente General",
                    "modelo": "Prenda General",
                    "cantidad": cant_emergencia,
                    "proceso": "Estándar",
                    "ganancia": calc_ganancia,
                    "hora": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state['bitacora_manualidades'].insert(0, registro)
                st.success(f"¡Registrado! Ganancia sumada: ${calc_ganancia:.2f}")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Su Resumen y Cuenta del Día")

    if len(st.session_state['bitacora_manualidades']) > 0:
        total_prendas_operario = sum(i['cantidad'] for i in st.session_state['bitacora_manualidades'])
        total_dinero_operario = sum(i['ganancia'] for i in st.session_state['bitacora_manualidades'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Prendas Procesadas", f"{total_prendas_operario} unds")
        with col2:
            st.metric("Su Ganancia Acumulada", f"${total_dinero_operario:.2f}")
            
        st.markdown("#### Historial de Lotes Escaneados Hoy:")
        for item in st.session_state['bitacora_manualidades']:
            st.info(f"🏷️ **Pedido:** {item['n_pedido']} | **Cliente:** {item['cliente']} | **Modelo:** {item['modelo']} ({item['cantidad']} unds) | **Proceso:** {item['proceso']} | 💰 **Ganancia:** ${item['ganancia']:.2f} *({item['hora']})*")
    else:
        st.info("Aún no ha escaneado ningún lote hoy. Utilice el escáner para comenzar.")
       
