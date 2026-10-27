"""Standalone ADK app: native tools, Sessions, Memory Bank and telemetry."""
import os
from pathlib import Path
from agentplatform.frameworks import AdkApp
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from .tools import lookup_order
from .preference_memory import remember_preference

APP_NAME = 'support_agent_basics'

class OptionalMemory(PreloadMemoryTool):
    async def process_llm_request(self, *, tool_context, llm_request):
        if os.environ.get('GOOGLE_MEMORY_ENABLED','true').lower()=='true':
            # Native service uses the trusted invocation/session user context.
            await super().process_llm_request(tool_context=tool_context,llm_request=llm_request)

def build_agent():
    return Agent(name=APP_NAME,
        model=Gemini(model=os.environ.get('GOOGLE_AGENT_MODEL','gemini-3.5-flash'),
                     client_kwargs={'enterprise':True,'location':os.environ.get('GOOGLE_MODEL_LOCATION','us')}),
        description='Standalone support lesson with fictional packaged order data',
        instruction=Path(__file__).with_name('instructions.txt').read_text(),
        tools=[lookup_order,remember_preference,OptionalMemory()])

def build_app():
    # Managed Sessions/Memory Bank are selected by AdkApp after deployment.
    return AdkApp(agent=build_agent(),app_name=APP_NAME)
