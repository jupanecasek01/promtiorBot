import os
from typing import Dict, List, TypedDict
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain_groq import ChatGroq
from langgraph.graph import END
from langgraph.graph import StateGraph
from langsmith import traceable
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

# Set up models to answer questions
GROQ_LLM_70 = ChatGroq(model="llama3-70b-8192")
GROQ_LLM_8 = ChatGroq(model="llama3-8b-8192")

conversation_with_summary_70b = ConversationChain(llm=GROQ_LLM_70)
conversation_with_summary_8b = ConversationChain(llm=GROQ_LLM_8)

def load_pdf_content(pdf_path):
    # Cargar el documento PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    # Cargar solo las páginas 3 y 4 (índices 2 y 3)
    pdf_text = "\n".join([doc.page_content for doc in documents[2:4]])
    return pdf_text

def custom_extractor(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()

# Instantiate the RecursiveUrlLoader
loader = RecursiveUrlLoader(url="https://www.promtior.ai/service", extractor=custom_extractor)

# Load the data from the website
docs = loader.load()

# Define the conversation state
class GraphState(TypedDict):
    initial_question: str
    question_category: str
    final_response: str
    num_steps: int
    conversation_history: List[Dict[str, str]]

# Node for question categorization
@traceable
def categorize_question(state):
    prompt_template = """\
    You are an agent responsible for categorizing questions about Promtior. Classify each question into one of the following categories:
        - service: if it is related to the services that Promtior offers.
        - founding: if it is related to the founding year of Promtior.
        - other: if the question is not related to these topics.

    Provide a single word with the category (service, founding, other).
    QUESTION CONTENT:\n {initial_question} \n
    """
    initial_question = state["initial_question"]
    state["num_steps"] += 1

    combined_prompt = prompt_template.format(initial_question=initial_question)
    response = conversation_with_summary_8b.predict(input=combined_prompt)
    if "service" in response.lower():
        state["question_category"] = "service"
    elif "founding" in response.lower():
        state["question_category"] = "founding"
    else:
        state["question_category"] = "other"

    return state

@traceable
def service_information_response(state):
    pdf_text = load_pdf_content("AI Engineer.pdf")
    web_text = docs

    prompt = PromptTemplate(
        template="""\
            You are an assistant for the Promtior website. Your task is to provide a clear and concise explanation of the services the company offers, based on the provided information. Do not mention where the information comes from (website or PDF), just focus on presenting the services clearly in English.

    QUESTION CONTENT (the user's question):\n{initial_question}\n

    MAIN INFORMATION (from the Promtior website):\n{web_text}\n

    ADDITIONAL CONTEXT (from the PDF document):\n{pdf_text}\n

    Please combine the relevant details from the website and the PDF to answer the question, focusing on the services offered by Promtior.
    """
    )

    input_text = prompt.template.format(
        initial_question=state["initial_question"], web_text=web_text, pdf_text=pdf_text
    )
    response = conversation_with_summary_70b.predict(input=input_text)
    state["final_response"] = response
    state["conversation_history"].append({"role": "assistant", "content": response})

    return state

# Node for founding-related responses
@traceable
def founding_information_response(state):
    pdf_text = load_pdf_content("AI Engineer.pdf")
    
    prompt = PromptTemplate(
    template="""\
    You are an assistant for the Promtior website. Respond only with relevant information in English, omitting references to where it was sourced.
    
    QUESTION CONTENT:\n{initial_question}\n   
    MAIN INFORMATION (from PDF):\n{pdf_text}
    """
    )

    input_text = prompt.template.format(
        initial_question=state["initial_question"], pdf_text=pdf_text
    )
    response = conversation_with_summary_70b.predict(input=input_text)
    state["final_response"] = response
    state["conversation_history"].append({"role": "assistant", "content": response})

    return state

# Node for general inquiries
@traceable
def other_inquiry_response(state):
    state["final_response"] = "I'm sorry, I don't have information on that."
    state["conversation_history"].append(
        {"role": "assistant", "content": state["final_response"]}
    )
    return state

# State printer
def state_printer(state):
    print(f"{state['final_response']}\n")
    return state

# Function to route responses
def route_to_respond(state):
    question_category = state['question_category']
    if question_category == "service":
        return "service_information_response"
    elif question_category == "founding":
        return "founding_information_response"
    else:
        return "other_inquiry_response"

# Set up the workflow
workflow = StateGraph(GraphState)

# Define nodes and transitions
workflow.add_node("categorize_question", categorize_question)
workflow.add_node("service_information_response", service_information_response)
workflow.add_node("founding_information_response", founding_information_response)

workflow.add_node("state_printer", state_printer)
workflow.add_node("other_inquiry_response", other_inquiry_response)

workflow.set_entry_point("categorize_question")

workflow.add_conditional_edges(
    "categorize_question",
    route_to_respond,
    {
        "service_information_response": "service_information_response",
        "founding_information_response": "founding_information_response",
        "other_inquiry_response": "other_inquiry_response",
    },
)

workflow.add_edge("service_information_response", "state_printer")
workflow.add_edge("founding_information_response", "state_printer")
workflow.add_edge("other_inquiry_response", "state_printer")
workflow.add_edge("state_printer", END)

app = workflow.compile()
states = []

def retrieve_state(conversation_id):
    global states
    for state in states:
        if state["conversation_id"] == conversation_id:
            return state
    return {
        "initial_question": "",
        "question_category": "",
        "final_response": "",
        "num_steps": 0,
        "conversation_history": [],
        "conversation_id": conversation_id,
    }

# Function to execute the chatbot (síncrona)
def execute_agent(question, conversation_id):
    global states  # Ensure state is recognized as global
    state = retrieve_state(conversation_id)
    state["initial_question"] = question
    states.append(state)
    output = app.invoke(state)
    return output
