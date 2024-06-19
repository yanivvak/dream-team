import time
import streamlit as st
from autogen.agentchat import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager
from autogen.oai.openai_utils import config_list_from_json
import warnings

warnings.filterwarnings('ignore')

# Configuration for GPT-4
config_list_gpt4 = config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4o"],  # gpt4o or gpt4-0409
    },
)
gpt4_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "timeout": 120,
}

# User Proxy Agent
user_proxy = UserProxyAgent(
    name="Admin",
    is_termination_msg=lambda msg: "terminate" in msg.get("content").lower(),
    human_input_mode="ALWAYS",
    system_message="1. A human admin. 2. Interact with the team. 3. Plan execution needs to be approved by this Admin.",
    code_execution_config=False,
    description="""Call this Agent if:   
        You need guidance.
        The program is not working as expected.
        You need api key 
        The task is successfully completed.                 
        DO NOT CALL THIS AGENT IF:  
        You need to execute the code.""",
)

# Assistant Agent - Developer
developer = AssistantAgent(
    name="Developer",
    llm_config=gpt4_config,
    system_message="""You are an AI developer. You follow an approved plan, follow these guidelines: 
    1. You write python/shell code to solve tasks. 
    2. Wrap the code in a code block that specifies the script type.   
    3. The user can't modify your code. So do not suggest incomplete code which requires others to modify.   
    4. You should print the specific code you would like the executor to run.
    5. Don't include multiple code blocks in one response.   
    6. If you need to import libraries, use ```bash pip install module_name```, please send a code block that installs these libraries and then send the script with the full implementation code 
    7. Check the execution result returned by the executor,  If the result indicates there is an error, fix the error and output the code again  
    8. Do not show appreciation in your responses, say only what is necessary.    
    9. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    """,
    description="""Call this Agent if:   
        You need to write code.                  
        DO NOT CALL THIS AGENT IF:  
        You need to execute the code.""",
)
# Assistant Agent - Planner
planner = AssistantAgent(
    name="Planner",
    system_message="""You are an AI Planner,  follow these guidelines: 
    1. Your plan should include 5 steps, you should provide a detailed plan to solve the task.
    2. Post project review isn't needed. 
    3. Revise the plan based on feedback from admin and quality_assurance.   
    4. The plan should include the only the team members,  explain which step is performed by whom, for instance: the Developer should write code, the Executor should execute code, important do not include the admin in the tasks e.g ask the admin to research.  
    5. Do not show appreciation in your responses, say only what is necessary.  
    6. The final message should include an accurate answer to the user request
    """,
    llm_config=gpt4_config,
    description="""Call this Agent if:   
        You need to build a plan.                  
        DO NOT CALL THIS AGENT IF:  
        You need to execute the code.""",
)

# User Proxy Agent - Executor
executor = UserProxyAgent(
    name="Executor",
    system_message="1. You are the code executer. 2. Execute the code written by the developer and report the result.3. you should read the developer request and execute the required code",
    human_input_mode="NEVER",
    code_execution_config={
        "last_n_messages": 20,
        "work_dir": "dream",
        "use_docker": True,
    },
    description="""Call this Agent if:   
        You need to execute the code written by the developer.  
        You need to execute the last script.  
        You have an import issue.  
        DO NOT CALL THIS AGENT IF:  
        You need to modify code""",
)
quality_assurance = AssistantAgent(
    name="Quality_assurance",
    system_message="""You are an AI Quality Assurance. Follow these instructions:
      1. Double check the plan, 
      2. if there's a bug or error suggest a resolution
      3. If the task is not solved, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach.
      4. Return 'terminate' when the task successfully completed""",
    llm_config=gpt4_config,
)
allowed_transitions = {
    user_proxy: [planner, quality_assurance],
    planner: [user_proxy, developer, quality_assurance],
    developer: [executor, quality_assurance, user_proxy],
    executor: [developer, quality_assurance],
    quality_assurance: [planner, developer, executor, user_proxy],
}

system_message_manager = "You are the manager of a research group your role is to manage the team and make sure the project is completed successfully."

groupchat = GroupChat(
    agents=[user_proxy, developer, planner, executor, quality_assurance],
    allowed_or_disallowed_speaker_transitions=allowed_transitions,
    speaker_transitions_type="allowed",
    messages=[], max_round=30,
    send_introductions=True
)

manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config, system_message=system_message_manager)


# Streamlit UI

def stream_data(message):
    for word in message.split(" "):
        yield word + " "
        time.sleep(0.02)


def new_print_received_message(self, message, sender):
    # st.write(f"{sender.name}: {message.get('content')}")
    print(message)
    st.write(f"{sender.name}:")
    st.write_stream(stream_data(message))


GroupChatManager._print_received_message = new_print_received_message


def main():
    st.title("AI Dream Team")

    # Initialize session state for messages and first query flag
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'first_query' not in st.session_state:
        st.session_state.first_query = True

    task = st.text_input("Enter your task:", "What are the 5 leading GitHub repositories on llm for the legal domain?")

    if st.button("Run Task"):
        if st.session_state.first_query:
            chat_result = user_proxy.initiate_chat(manager, message=task, clear_history=True)
            st.session_state.first_query = False
        else:
            chat_result = user_proxy.initiate_chat(manager, message=task, clear_history=False)

        st.session_state.messages.append(chat_result)
        # st.write("Chat Summary:")
        # st.write(chat_result.summary)
        # st.write("Chat History:")
        # st.write(chat_result.chat_history)

    if st.button("Clear History"):
        st.session_state.messages = []
        st.session_state.first_query = True
        st.write("Chat history cleared.")


if __name__ == "__main__":
    main()