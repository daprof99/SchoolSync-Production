import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage
import operator
from tools import *

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    next_step: str


llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


def router_node(state: AgentState):
    raw = state['messages'][-1].content
    msg = raw.split(" || ")[1] if " || " in raw else raw.strip()

    # Bursary/Finance Keywords (added MAKE for "make payment")
    if any(k in msg.upper() for k in
           ["PAY", "PAYMENT", "MAKE", "CHECK", "BILL", "CLOCKIN", "SUMMARY", "BROADCAST", "ADD STUDENT", "APPROVE", "HTTP", "REGISTER PARENT", "ALL CHILDREN", "FEES", "BALANCE", "OWING", "OWE", "DEBT", "MONEY"]):
        return {"next_step": "BURSARY"}
    
    # Results Keywords
    if any(k in msg.upper() for k in ["RESULT", "GRADE", "SCORE", "REPORT CARD"]):
        return {"next_step": "RESULTS"}
    
    # Messages Keywords
    if any(k in msg.upper() for k in ["MESSAGE", "TEACHER", "SHOW MESSAGES", "CONTACT"]):
        return {"next_step": "MESSAGES"}
    
    # Events Keywords
    if any(k in msg.upper() for k in ["EVENT", "CALENDAR", "PTA", "MEETING", "WHEN IS", "NEXT"]):
        return {"next_step": "EVENTS"}
    
    # Admissions Keywords
    if any(k in msg.upper() for k in ["ADMISSION", "REGISTER", "ENROLL", "NEW STUDENT"]):
        return {"next_step": "ADMISSIONS"}

    # AI Classifier for natural language
    sys = "Classify: ADMISSIONS, BURSARY, RESULTS, LIAISON, MESSAGES, EVENTS, GENERAL, OFF_TOPIC (Sports/Politics)."
    dec = llm.invoke(f"{sys}\nInput: {msg}").content.strip().upper()
    return {"next_step": "GENERAL" if "OFF_TOPIC" in dec else dec}


def get_next_node(state):
    step = state['next_step']
    if "BURSARY" in step: return "bursary_agent"
    if "ADMISSIONS" in step: return "admissions_agent"
    if "RESULTS" in step: return "results_agent"
    if "LIAISON" in step: return "liaison_agent"
    if "MESSAGES" in step: return "messages_agent"
    if "EVENTS" in step: return "events_agent"
    return "general_agent"


graph = StateGraph(AgentState)
graph.add_node("router", router_node)
graph.add_node("general_agent", check_general_tools)
graph.add_node("bursary_agent", check_bursary_tools_enhanced)  # Enhanced with multi-student
graph.add_node("admissions_agent", check_admissions_tools)
graph.add_node("results_agent", check_results_tools_enhanced)  # Enhanced with full features
graph.add_node("liaison_agent", check_liaison_tools)
graph.add_node("messages_agent", check_messages_tools)  # NEW: Parent-teacher messaging
graph.add_node("events_agent", check_events_tools)  # NEW: Calendar/Events
graph.set_entry_point("router")
graph.add_conditional_edges("router", get_next_node)
graph.add_edge("general_agent", END)
graph.add_edge("bursary_agent", END)
graph.add_edge("admissions_agent", END)
graph.add_edge("results_agent", END)
graph.add_edge("liaison_agent", END)
graph.add_edge("messages_agent", END)
graph.add_edge("events_agent", END)
app = graph.compile()