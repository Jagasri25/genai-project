# agents/agent.py
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.models.base import get_db
from backend.app.models.project import Project, Task
from backend.app.models.user import User

class QueryParameters(BaseModel):
    query: str
    user_id: int

class ChatbotAgent:
    def __init__(self):
        self.db = next(get_db())
        self.llm = OpenAI(temperature=0)
        self.tools = self.setup_tools()
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = self.setup_agent()

    def setup_tools(self) -> List[Tool]:
        return [
            Tool(
                name="ProjectQuery",
                func=self.query_projects,
                description="Useful for answering questions about projects, like 'What projects are active?' or 'Who is working on project X?'"
            ),
            Tool(
                name="TaskQuery",
                func=self.query_tasks,
                description="Useful for answering questions about tasks, like 'What tasks are assigned to user X?' or 'What is the status of task Y?'"
            ),
            Tool(
                name="UserQuery",
                func=self.query_users,
                description="Useful for answering questions about team members, like 'Who is Jagasri?' or 'What is Jagasri working on?'"
            ),
            Tool(
                name="DocumentQuery",
                func=self.query_documents,
                description="Useful for answering questions about project documents"
            )
        ]

    def setup_agent(self) -> AgentExecutor:
        prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
        suffix = """Begin!"

        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            self.tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"]
        )

        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=self.tools, verbose=True)
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )

    def query_projects(self, query: str) -> str:
        """Handle project-related queries"""
        # Example implementation - would be more sophisticated in production
        if "active" in query.lower():
            projects = self.db.query(Project).filter(Project.status == 'active').all()
            return "\n".join([f"{p.name} (Due: {p.end_date})" for p in projects])
        elif "my projects" in query.lower():
            projects = self.db.query(Project).join(ProjectMember).filter(
                ProjectMember.user_id == self.current_user_id
            ).all()
            return "\n".join([p.name for p in projects])
        else:
            return "I couldn't find information about projects matching your query."

    def query_tasks(self, query: str) -> str:
        """Handle task-related queries"""
        if "my tasks" in query.lower():
            tasks = self.db.query(Task).join(TaskAssignment).filter(
                TaskAssignment.user_id == self.current_user_id
            ).all()
            return "\n".join([f"{t.title} ({t.status})" for t in tasks])
        elif "deadline" in query.lower():
            tasks = self.db.query(Task).filter(
                Task.due_date.isnot(None)
            ).order_by(Task.due_date).limit(5).all()
            return "\n".join([f"{t.title} - Due: {t.due_date}" for t in tasks])
        else:
            return "I couldn't find task information matching your query."

    def query_users(self, query: str) -> str:
        """Handle user-related queries"""
        if "working on" in query.lower():
            name = query.split("working on")[0].strip()
            user = self.db.query(User).filter(
                User.full_name.ilike(f"%{name}%")
            ).first()
            if user:
                tasks = self.db.query(Task).join(TaskAssignment).filter(
                    TaskAssignment.user_id == user.id
                ).all()
                return f"{user.full_name} is working on:\n" + "\n".join([t.title for t in tasks])
            else:
                return f"I couldn't find a user named {name}"
        else:
            return "I couldn't understand your question about team members."

    def process_query(self, params: QueryParameters) -> Dict[str, Any]:
        self.current_user_id = params.user_id
        try:
            response = self.agent.run(input=params.query)
            return {"success": True, "response": response}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize the agent
agent = ChatbotAgent()