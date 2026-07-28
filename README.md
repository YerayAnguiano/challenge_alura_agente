# Agente Virtual Corporativo RAG — Mercado Central 24h

Sistema de Inteligencia Artificial Conversacional basado en **RAG (Retrieval-Augmented Generation)** diseñado para responder consultas de los colaboradores del supermercado *Mercado Central 24h* sobre políticas internas, procedimientos, inventario y programa de clientes.

---

## 🔗 Aplicación en Vivo

Puedes probar la interfaz interactiva desplegada en la nube aquí:  
👉 **[Acceder a la Aplicación en Streamlit Community Cloud](https://mercadocentral24h.streamlit.app/)**

---

## 📄 Documentos de la Base de Conocimiento

El agente fue alimentado e indexado utilizando los siguientes documentos oficiales corporativos de un supermercado moderno de operación continua (24/7) que integra la experiencia de tienda física con servicios de delivery y app propia. Su enfoque principal es la eficiencia operativa en la gestión de stock y una fuerte política de atención al cliente, impulsada por su programa de fidelidad "Cliente VIP Central".

1. **`Politica_Atencion_Cliente_y_Devoluciones_Central24h.pdf`**: Tiempos de devolución, garantías, políticas sobre productos perecederos/no perecederos y procedimiento de atención.
  
2. **`inventario_de_supermercado_latam.xlsx`**: Listado de stock, marcas, categorías, precios y disponibilidad de productos por pasillos.
  
3. **`Reglamento_Interno_y_Horarios_Supermercado.docx`**: Turnos de trabajo, políticas de puntualidad, tolerancias, vestimenta y beneficios laborales.
  
  1. **`Manual_de_Politicas_de_Compras_y_Proveedores.pdf`**: Condiciones para alta de nuevos proveedores, tiempos de pago y criterios de selección.
    5. **`Preguntas_Frecuentes_Programa_Cliente_VIP_Central.txt`**: Reglas del programa de puntos, beneficios, expiración y niveles de membresía.

```
  ## 🛠️ Arquitectura y Flujos de Trabajo en n8n


  La solución utiliza **n8n** como motor principal de orquestación, dividiendo el procesamiento en dos workflows independientes para optimizar rendimiento y costos.

  ### 1. Ingesta, Procesamiento e Indexación Vectorial (Etapas 1 - 3)

  Este flujo procesa los documentos fuente, los convierte a texto estructurado, los divide en fragmentos (*chunks*) optimizados y genera sus vectores de características.

  ```text
  [Documentos PDF/Excel/DOCX/TXT]
            │
            ▼
     [Extracción y Limpieza]
            │
            ▼
     [Text Splitter (Chunks)]
            │
            ▼
   [OpenAI Embeddings (1536 dims)]
            │
            ▼
   [Qdrant Vector Database (Cosine)]
```

- **Orquestación en n8n:** Extrae el contenido sin procesar de cada formato de archivo, divide el texto en bloques lógicos conservando metadatos (`nombre_archivo`, `categoria`) e indexa los vectores en la base de datos vectorial.
- **Embeddings:** `OpenAI text-embedding-3-small` (1536 dimensiones) para garantizar máxima precisión semántica y compatibilidad matemática.
- **Vector Store:** **Qdrant Cloud** (Colección `mercado_central_kb`, Métrica de distancia: *Cosine*).

![](/home/yerry/Documents/Cursos%20&%20Talleres/Alura%20ONELatam/Challenge%20Alura%20Agente/img/workflow_ingesta.png)

---

### 2. Capa de Recuperación y Agente Conversacional RAG

Este flujo actúa como la API backend que recibe las consultas de los usuarios, busca el contexto relevante y formula una respuesta precisa.

```text
[Petición HTTP Webhook]
          │
          ▼
 [Window Buffer Memory]
          │
          ▼
    [AI Agent (LLM)] ──► [Vector Store Tool (Qdrant Search k=4)]
          │
          ▼
 [Respuesta con Cita de Fuentes]
```

- **Trigger:** Nodo **Webhook** (método `POST`) configurado para recibir payloads JSON con la pregunta del usuario (`chatInput`) y el identificador de sesión (`sessionId`).
- **Memoria:** **Window Buffer Memory** para mantener el contexto de la charla en mensajes consecutivos.
- **LLM / Modelo de Lenguaje:** `OpenAI gpt-4o-mini` con instrucciones de sistema (*System Prompt*) estrictas para prevenir alucinaciones, rechazar preguntas fuera de contexto y exigir citas directas de fuentes.
- **Tool RAG:** **Vector Store Tool** conectada a Qdrant en modo recuperación (*Retrieve Documents*), trayendo los $k=4$ fragmentos más relevantes por cada consulta.

![](/home/yerry/Documents/Cursos%20&%20Talleres/Alura%20ONELatam/Challenge%20Alura%20Agente/img/Workflow_RAG.png)

---

## Funcionamiento de la Aplicación (Frontend)

La interfaz fue desarrollada en **Python con Streamlit**, priorizando una experiencia de usuario (UX) limpia, ágil y visualmente atractiva.

### Características Principales:

- **Panel de Preguntas Recomendadas (Sidebar):** Permite a los colaboradores realizar consultas frecuentes con un solo clic sin necesidad de escribir la pregunta manualmente.
- **Historial Conversacional Continuo:** Mantiene la fluidez del diálogo vinculando la sesión activa con el nodo de memoria en n8n.
- **Control de Alucinaciones y Citas:** El asistente responde respaldado únicamente por los documentos oficiales y cita al final el archivo fuente y la categoría. Si la información no existe en los documentos, rechaza la respuesta de forma segura.

### Página principal

![](/home/yerry/Documents/Cursos%20&%20Talleres/Alura%20ONELatam/Challenge%20Alura%20Agente/img/interfaz_1.png)

### Pregunta sugerida

![](/home/yerry/Documents/Cursos%20&%20Talleres/Alura%20ONELatam/Challenge%20Alura%20Agente/img/interfaz_2.png)

---

## Tecnologías Utilizadas

- **Frontend:** Streamlit, Python 3.11, Requests.
- **Orquestador Backend:** n8n (Workflows & AI Agent).
- **Modelos de IA:** OpenAI (`gpt-4o-mini` y `text-embedding-3-small`).
- **Base de Datos Vectorial:** Qdrant Cloud.
- **Despliegue Cloud:** Streamlit Community Cloud.

---

## Instalación y Ejecución Local

Si deseas ejecutar el frontend de manera local en tu máquina:

1. **Clonar el repositorio:**
  
  ```bash
  git clone [https://github.com/tu-usuario/mercado-central-rag-agent.git](https://github.com/tu-usuario/mercado-central-rag-agent.git)
  cd mercado-central-rag-agent
  ```
  
  2. **Instalar dependencias:**

```bash
pip install -r requirements.txt    
```

3. **Configurar la variable de entorno para el Webhook (opcional):**
  
  ```bash
  export N8N_WEBHOOK_URL="http://localhost:5678/webhook/mercado-central-agent"
  ```
  
4. **Ejecutar Streamlit:**
  

```bash
streamlit run frontend/app.py
```
