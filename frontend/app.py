import streamlit as st
import requests
import uuid

#configuracion de la pagina
st.set_page_config(
    page_title="Challenge Alura Agente - Mercado Central 24h",
    page_icon=":cart:",
    layout="centered",
)

# Estilo personalizado para botones laterales y chat
st.markdown("""
    <style>
    .stSidebar {
        background-color: #f8f9fa;
    }
    div.stButton > button {
        width: 100%;
        text-align: left;
        white-space: normal;
        height: auto;
        padding: 10px;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# URL del Webhook de n8n (Asegúrate de ajustar esta URL según tu entorno)
N8N_WEBHOOK_URL = "https://yerayanguiano.app.n8n.cloud/webhook/mercado-central-agent"

# 1. Gestión de ID de sesión y estados
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy el asistente virtual corporativo de Mercado Central 24h. ¿En qué te puedo ayudar hoy respecto a políticas, inventarios o procedimientos?"}
    ]

# Variable para capturar preguntas disparadas desde la barra lateral
prompt_to_send = None

# ---------------------------------------------------------
# BARRA LATERAL (SIDEBAR) - Preguntas Recomendadas
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=70)
    st.title("Mercado Central 24h")
    st.markdown("**Base de Conocimiento Centralizada**")
    st.divider()

    st.subheader("💡 Preguntas Recomendadas")
    st.caption("Haz clic en cualquier opción para consultar directamente al agente:")

    # Preguntas predefinidas organizadas por áreas/documentos
    preguntas_guiadas = [
        "¿Tienen disponibilidad de Leche y en qué pasillo se ubica?",
        "¿Cuál es el plazo máximo para devoluciones de productos no perecederos?",
        "¿Qué se menciona sobre el Código de Ética Corporativo?",
        "¿Cuáles son las políticas de compras para nuevos proveedores?",
        "¿Cómo opera el programa de fidelidad Cliente VIP Central?"
    ]

    for preg in preguntas_guiadas:
        if st.button(preg, key=preg):
            prompt_to_send = preg

    st.divider()
    st.caption("📌 **Nota:** Si la información no está en los documentos oficiales, el agente te lo indicará de forma segura.")

# ---------------------------------------------------------
# CUERPO PRINCIPAL (CHAT)
# ---------------------------------------------------------
st.title("Agente Virtual Corporativo")
st.caption("Chatbot RAG conectado en tiempo real con Qdrant y n8n.")

# Renderizar el historial de conversación en el centro
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar entrada del usuario por teclado si no seleccionó un botón lateral
user_input = st.chat_input("Escribe tu pregunta sobre documentos internos...")
if user_input:
    prompt_to_send = user_input

# ---------------------------------------------------------
# LÓGICA DE PROCESAMIENTO Y ENVÍO A N8N
# ---------------------------------------------------------
if prompt_to_send:
    # 1. Guardar y renderizar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt_to_send})
    with st.chat_message("user"):
        st.markdown(prompt_to_send)

    # 2. Consultar al agente en n8n
    with st.chat_message("assistant"):
        with st.spinner("Consultando la base de documentos..."):
            try:
                payload = {
                    "action": "sendMessage",
                    "chatInput": prompt_to_send,
                    "prompt": prompt_to_send,
                    "sessionId": st.session_state.session_id
                }

                # Enviar la petición HTTP POST a n8n
                response = requests.post(
                    N8N_WEBHOOK_URL, 
                    json=payload, 
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Captura la respuesta ya sea que venga como string, dict con 'output', 'text' o respuesta directa
                    if isinstance(data, dict):
                        bot_response = data.get("output") or data.get("text") or data.get("message") or str(data)
                    elif isinstance(data, list) and len(data) > 0:
                        bot_response = data[0].get("output") or data[0].get("text") or str(data[0])
                    else:
                        bot_response = str(data)
                else:
                    bot_response = f"⚠️ Error de comunicación con n8n (Código HTTP {response.status_code})."
            except Exception as e:
                bot_response = f"⚠️ No se pudo conectar con el servidor del agente: {str(e)}"

            # Renderizar y guardar la respuesta del agente
            st.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            # Recargar para limpiar el estado de envío instantáneamente
            st.rerun()