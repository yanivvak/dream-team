import streamlit as st


import asyncio
import logging
from io import StringIO
import os
 
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy
from autogen_core.components.code_executor import CodeBlock
from autogen_ext.code_executor.docker_executor import DockerCommandLineCodeExecutor
from autogen_magentic_one.agents.coder import Coder, Executor
from autogen_magentic_one.agents.file_surfer import FileSurfer
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage, OrchestrationEvent

from autogen_magentic_one.messages import BroadcastMessage
from autogen_core.components.models import UserMessage


from autogen_magentic_one.utils import LogHandler
from dotenv import load_dotenv
load_dotenv()



 
async def confirm_code(code: CodeBlock) -> bool:
    response = await asyncio.to_thread(
        input,
        f"Executor is about to execute code (lang: {code.language}):\n{code.code}\n\nDo you want to proceed? (yes/no): ",
    )
    return response.lower() == "yes"
 
 
async def main() -> None:
    # Create the runtime.
    runtime = SingleThreadedAgentRuntime()
 
    # Create an appropriate client
    #client = create_completion_client_from_env()
    
 
    from autogen_ext.models import AzureOpenAIChatCompletionClient
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
 
    # Create the token provider
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
 
    client = AzureOpenAIChatCompletionClient(
        model="gpt-4o",
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        #azure_ad_token_provider=token_provider,
        model_capabilities={
            "vision":True,
            "function_calling":True,
            "json_output":True,
        }
    )
 
    async with DockerCommandLineCodeExecutor() as code_executor:
        # Register agents.
        await Coder.register(runtime, "Coder", lambda: Coder(model_client=client))
        coder = AgentProxy(AgentId("Coder", "default"), runtime)
 
        await Executor.register(
            runtime,
            "Executor",
            lambda: Executor("A agent for executing code", executor=code_executor, confirm_execution=confirm_code),
        )
        executor = AgentProxy(AgentId("Executor", "default"), runtime)
 
        # Register agents.
        await MultimodalWebSurfer.register(runtime, "WebSurfer", MultimodalWebSurfer)
        web_surfer = AgentProxy(AgentId("WebSurfer", "default"), runtime)
 
        await FileSurfer.register(runtime, "file_surfer", lambda: FileSurfer(model_client=client))
        file_surfer = AgentProxy(AgentId("file_surfer", "default"), runtime)
 
        await UserProxy.register(
            runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)
 
        await LedgerOrchestrator.register(
            runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=[web_surfer, user_proxy, coder, executor, file_surfer],
                model_client=client,
                max_rounds=30,
                max_time=25 * 60,
                return_final_answer=True,
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), runtime)
 
        runtime.start()
 
        actual_surfer = await runtime.try_get_underlying_agent_instance(web_surfer.id, type=MultimodalWebSurfer)
        await actual_surfer.init(
            model_client=client,
            downloads_folder=os.getcwd(),
            start_page="https://cve.mitre.org",#"https://github.com/microsoft/autogen",
            browser_channel="chromium",
            headless=True,
        )
 
        # await runtime.send_message(RequestReplyMessage(]), user_proxy.id) # USE this when you want interaction with the user
        await runtime.send_message(
            BroadcastMessage(
                content=UserMessage(
                    #   content="find a top article for Large Language Models in web and safe as 'article.pdf'", source="user"
                    content="generate three random words beging with 'A'", source="user"
                )
            ),
            recipient=orchestrator.id,
            sender=user_proxy.id,
        )
        
        await runtime.stop_when_idle()
 


# Initialize session state for instructions
if 'instructions' not in st.session_state:
    st.session_state['instructions'] = ""

# Input for instructions
instructions = st.text_input("Enter your instructions:")



if instructions:
    st.session_state['instructions'] = instructions
    st.write("Instructions:", st.session_state['instructions'])

    # run the workflow

    log_stream = StringIO()

    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler()
    log_handler.setStream(log_stream)
    logger.handlers = [log_handler]
    asyncio.run(main())

    # Display the log messages in Streamlit
    st.text_area("Log Output", log_stream.getvalue(), height=300)

    st.write("Done")
    
    
    # Container for displaying messages
    message_container = st.container()
    with message_container:
        st.write("Messages will be displayed here.")

        