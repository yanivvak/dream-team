"""This example demonstrates MagenticOne performing a task given by the user and returning a final answer."""
#    This example uses version 0.4.0.dev11 of the autogen packages
 
import asyncio
import logging
import os
from autogen_core import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core import AgentId, AgentProxy
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_core.code_executor import CodeBlock
from autogen_magentic_one.agents.coder import Coder, Executor
from autogen_magentic_one.agents.file_surfer import FileSurfer
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.utils import LogHandler
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

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
    
    # Create the token provider for Azure AD authentication.
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
 
    client = AzureOpenAIChatCompletionClient(
        model="gpt-4o",
        azure_deployment="gpt-4o",
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

        runtime.start()
 
        actual_surfer = await runtime.try_get_underlying_agent_instance(web_surfer.id, type=MultimodalWebSurfer)
        await actual_surfer.init(
            model_client=client,
            downloads_folder=os.getcwd(),
            start_page="https://bing.com",#"https://github.com/microsoft/autogen",
            browser_channel="chromium",
            headless=True,
        )
 
        await runtime.send_message(RequestReplyMessage(), user_proxy.id)
        await runtime.stop_when_idle()
 
 
if __name__ == "__main__":
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler()
    logger.handlers = [log_handler]
    asyncio.run(main())