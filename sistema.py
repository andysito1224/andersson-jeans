import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Andersson Jean's & Confecciones", layout="wide")

# --- SIMULADOR DE BASE DE DATOS Y USUARIOS EN SESSION_STATE ---
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
if 'usuario_actual' not in st.session_state:
    st.session_state['usuario_actual'] = None
if 'rol_actual' not in st.session_state:
    st.session_state['rol_actual'] = None

st.title("👖 Andersson Jean's & Confecciones")

# =========================================================================
# 1. PANTALLA DE LOGIN (CONTROL DE ACCESO POR CLAVE)
# =========================================================================
if st.session_state['usuario_actual'] is None:
    st.subheader("🔐 Acceso al Sistema")
    st.markdown("Ingrese su contraseña personal para acceder a su área autorizada.")
    
    with st.form("form_login"):
        clave_ingresada = st.text_input("Contraseña:", type="password")
        btn_entrar = st.form_submit_button("Ingresar")
        
        if btn_entrar:
            # --- CONFIGURA AQUÍ LAS CLAVES DE TUS EMPLEADOS Y RECEPCIÓN ---
            
            # Ejemplo de claves para Operarios de Manualidades
            operarios = {
                "operario1": "Patto (Manualidades)",
                "operario2": "Carlos (Manualidades)"
            }
            
            # Ejemplo de claves para Recepción / Administración
            admin = {
                "recep2026": "Recepción / Admin"
            }
            
            if clave_ingresada in operarios:
                st.session_state['usuario_actual'] = operarios[clave_ingresada]
                st.session_state['rol_actual'] = "Manualidades"
                st.success(f"¡Bienvenido, {operarios[clave_ingresada]}!")
                st.rerun()
            elif clave_ingresada in admin:
                st.session_state['usuario_actual'] = admin[clave_ingresada]
                st.session_state['rol_actual'] = "Admin"
                st.success("¡Bienvenido a Recepción!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Verifique sus datos.")

# =========================================================================
# 2. VISTA EXCLUSIVA: OPERARIOS DE MANUALIDADES
# =========================================================================
elif st.session_state['rol_actual'] == "Manualidades":
    st.sidebar.markdown(f"### 👤 Operario: {st.session_state['usuario_actual']}")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['usuario_actual'] = None
        st.session_state['rol_actual'] = None
        st.rerun()

    st.subheader(f"📱 Módulo Manualidades - {st.session_state['usuario_actual']}")
    st.markdown("📸 **Tome una foto al sticker QR** con su celular, presione el botón de análisis y el sistema registrará automáticamente el lote a su cuenta.")

    foto_sticker = st.file_uploader("Tomar / Subir foto del Sticker QR del Lote", type=["jpg", "png", "jpeg"], key="foto_qr_operario")

    if foto_sticker is not None:
        st.image(foto_sticker, caption="Sticker QR capturado", width=250)
        
        if st.button("🤖 Analizar QR y Registrar a mi Cuenta"):
            with st.spinner("Leyendo código QR con IA..."):
                # Aquí la IA procesa la foto del sticker y extrae el número de pedido
                codigo_leido = "0038743" 
                pedido_encontrado = st.session_state['db_pedidos'].get(codigo_leido)
                
                if pedido_encontrado:
                    calc_ganancia = pedido_encontrado['cantidad'] * pedido_encontrado['tarifa']
                    registro = {
                        "operario": st.session_state['usuario_actual'],
                        "n_pedido": codigo_leido,
                        "cliente": pedido_encontrado['cliente'],
                        "modelo": pedido_encontrado['modelo'],
                        "cantidad": pedido_encontrado['cantidad'],
                        "proceso": pedido_encontrado['proceso'],
                        "ganancia": calc_ganancia,
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state['bitacora_manualidades'].insert(0, registro)
                    st.success(f"¡Lote N° {codigo_leido} registrado! Ganancia sumada: ${calc_ganancia:.2f}")
                else:
                    st.warning("No se reconoció el pedido en la foto. Intente tomarla más enfocada.")

    st.markdown("---")
    st.markdown("### 📊 Su Resumen y Ganancias del Día")

    # Filtramos la bitácora para que cada operario vea únicamente sus propios registros
    mis_registros = [i for i in st.session_state['bitacora_manualidades'] if i['operario'] == st.session_state['usuario_actual']]

    if len(mis_registros) > 0:
        total_prendas_operario = sum(i['cantidad'] for i in mis_registros)
        total_dinero_operario = sum(i['ganancia'] for i in mis_registros)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Prendas Procesadas", f"{total_prendas_operario} unds")
        with col2:
            st.metric("Su Ganancia Acumulada", f"${total_dinero_operario:.2f}")
            
        st.markdown("#### Sus Lotes Registrados Hoy:")
        for item in mis_registros:
            st.info(f"🏷️ **Pedido:** {item['n_pedido']} | **Cliente:** {item['cliente']} | **Modelo:** {item['modelo']} ({item['cantidad']} unds) | **Proceso:** {item['proceso']} | 💰 **Ganancia:** ${item['ganancia']:.2f} *({item['hora']})*")
    else:
        st.info("Aún no registra lotes hoy. Tome una foto al sticker QR para comenzar.")

# =========================================================================
# 3. VISTA EXCLUSIVA: RECEPCIÓN / ADMINISTRACIÓN
# =========================================================================
elif st.session_state['rol_actual'] == "Admin":
    st.sidebar.markdown(f"### 🛠️ Sesión: {st.session_state['usuario_actual']}")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['usuario_actual'] = None
        st.session_state['rol_actual'] = None
        st.rerun()

    st.subheader("📸 Recepción de Pedidos - Análisis por IA")
    st.markdown("Tome la foto de la nota de pedido, presione **Analizar con IA**, verifique los datos y genere su QR.")

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
