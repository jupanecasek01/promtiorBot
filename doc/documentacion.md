
### **1. Proyecto**

#### **Arquitectura y Funcionalidades Principales**

1. **Clasificación de preguntas**: 
   - Al recibir una pregunta, el chatbot primero clasifica el tipo de consulta en tres categorías: "service" (relacionada con los servicios de la empresa), "founding" (relacionada con la fundación de la empresa) u "other" (para preguntas que no pertenecen a ninguna de las categorías anteriores).
   - Esta clasificación permite que el bot seleccione el flujo de respuesta adecuado, optimizando la precisión y relevancia de sus respuestas.

2. **Generación de respuestas basada en fuentes de datos**:
   - **Para preguntas sobre servicios**: El chatbot combina información obtenida tanto del sitio web de Promtior como de un PDF con información relevante de la empresa.
   - **Para preguntas sobre la fundación de la empresa**: El bot se enfoca exclusivamente en información extraída del PDF, ignorando la web. Esto es porque en la web no encontre informacion relevante sobre la fundación.
   - **Para preguntas irrelevantes (Other)**: El chatbot devuelve una respuesta predeterminada indicando que la consulta no es relevante o que la información no está disponible.

3. **Gestión de conversación**:
   - El chatbot mantiene un historial de la conversación mediante un identificador de conversación (`conversation_id`). Esto le permite contextualizar cada respuesta basada en las interacciones anteriores del usuario, proporcionando una experiencia de usuario más coherente.

está disponible.

4. **Tecnologías utilizadas**:
   - **LangChain**: Para el procesamiento del lenguaje natural y la integración de modelos de lenguaje.
   - **Groq con LLaMA3**: Usado como el modelo de lenguaje base para las interacciones.
   - **LangGraph**: Utilizado para gestionar el flujo de trabajo y la estructura del chatbot.
   - **LangSmith**: Para trazar y monitorear el flujo de trabajo, asegurando la trazabilidad de las interacciones.
   - **PyPDFLoader**: Para cargar y procesar el contenido de documentos PDF.
   - **RecursiveUrlLoader**: Para extraer información relevante de sitios web.
   - 
#### **Desafíos y soluciones**

Algunos desafíos fueron:
- **Integración de múltiples fuentes de datos**: Fue necesario garantizar que las respuestas se generaran de manera concisa, sin exponer explícitamente las fuentes de información.
- **Optimización de flujo en LangGraph**: Configurar el flujo de trabajo para que cada paso de procesamiento se ejecute de manera eficiente sin sobrecargar el modelo.


### **2. Instrucciones para probar el POST**

Para verificar el funcionamiento del chatbot, puedes enviar solicitudes POST usando herramientas como Postman o cualquier cliente HTTP.

#### **URL de prueba**

- **URL**: `https://prueba-tecnica-fpehd0fhcub2gjdf.canadaeast-01.azurewebsites.net/`
- **Método HTTP**: POST

#### **Cuerpo de la solicitud**

En el cuerpo de la solicitud debes enviar un JSON con los siguientes campos:

- `question`: La pregunta que deseas hacer al chatbot. Por ejemplo, `"What services does Promtior offer?"`.
- `conversation_id`: Un identificador único para la conversación. Puedes usar cualquier valor (números o texto) para identificar la conversación. Esto permite al bot recordar el contexto de la interacción.

#### **Ejemplo de JSON para el cuerpo de la solicitud**

```json
{
  "question": "What services does Promtior offer?",
  "conversation_id": "12345"
}
```

#### **Respuesta esperada**

El chatbot debería devolver una respuesta en formato JSON con la información solicitada. Dependiendo de la pregunta, el formato de la respuesta podría verse de la siguiente manera:

```json
{
  "response": "Promtior offers consulting services in digital transformation and business intelligence."
}
```

### **Consideraciones adicionales**

- **Manejo de errores**: En caso de que el chatbot no pueda procesar la pregunta, la API debería devolver un mensaje de error con el código de estado HTTP correspondiente.
- **Identificación del conversational flow**: El campo `conversation_id` es clave para mantener el contexto en una conversación. Usar un mismo `conversation_id` para preguntas relacionadas ayudará al chatbot a ofrecer respuestas más contextuales.

