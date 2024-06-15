import streamlit as st    
from autogen.agentchat import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager  
from autogen.oai.openai_utils import config_list_from_json  
import warnings  

  
warnings.filterwarnings('ignore')  

# Configuration for GPT-4  
config_list_gpt4 = config_list_from_json(  
    "OAI_CONFIG_LIST.json",  
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

if 'input_keys' not in st.session_state:
    st.session_state.input_keys= []
if 'saved_agents' not in st.session_state:
    st.session_state.saved_agents = []
if 'info' not in st.session_state:
    st.session_state.info = None
if 'able_to_run' not in st.session_state:
    st.session_state.able_to_run = False
if 'running' not in st.session_state:
    st.session_state.running = False

# Initialize session state for messages and first query flag  
if 'messages' not in st.session_state:  
    st.session_state.messages = []  
if 'first_query' not in st.session_state:  
    st.session_state.first_query = True  

info_placeholder = st.empty()

if not st.session_state.info:
    info_placeholder.empty()
else:
    info_placeholder.info(st.session_state.info)

st.write(st.session_state.messages)

if (st.session_state.saved_agents):
    # st.write("Agents loaded...")
    agents = st.session_state.saved_agents
    st.session_state.able_to_run = True
else:
    st.warning("No agents loaded yet!")
    agents = []
    st.session_state.able_to_run = False

with st.expander("Defined agents", expanded=False):
    # st.write("Defined Agents:")
    for val in agents:
        st.json(val)

def get_entry_agent(agents):
    # return agents[st.selectbox("Entry Agent", agents.keys())]
    return agents["Admin"]

def config(allowed_transitions, max_round=30, speaker_transitions_type="allowed"):
    st.session_state.info = "Configuring agents..."

    agents = {}
    for agent in st.session_state.saved_agents:
        if agent["type"] == "UserProxyAgent":
            if agent["human_input_mode"] == "ALWAYS":
                _a = UserProxyAgent(
                    name=agent["name"],
                    system_message=agent["system_message"],
                    description=agent["description"],
                    human_input_mode=agent["human_input_mode"],
                    code_execution_config=False,
                    is_termination_msg=lambda msg: "terminate" in msg.get("content").lower(), # TODO: what is this?
                )
            elif agent["human_input_mode"] == "NEVER":
                _a = UserProxyAgent(
                    name=agent["name"],
                    system_message=agent["system_message"],
                    description=agent["description"],
                    human_input_mode=agent["human_input_mode"],
                    code_execution_config={  
                        "last_n_messages": 20,  
                        "work_dir": "dream",  
                        "use_docker": False,  
                    }
                )
        elif agent["type"] == "AssistantAgent":
            _a = AssistantAgent(
                name=agent["name"],
                system_message=agent["system_message"],
                description=agent["description"],
                llm_config=gpt4_config,
            )
        else:
            st.error(f"Unknown agent type: {agent['type']}")
            st.stop()
        
        

        agents[agent["name"]] = _a

    allowed_transitions = {
        agents["Admin"]: [ agents["Planner"],agents["Quality Assurance"]],
        agents["Planner"]: [ agents["Admin"], agents["Developer"], agents["Quality Assurance"]],
        agents["Developer"]: [agents["Executor"],agents["Quality Assurance"], agents["Admin"]],
        agents["Executor"]: [agents["Developer"],agents["Quality Assurance"]],
        agents["Quality Assurance"]: [agents["Planner"],agents["Developer"],agents["Executor"],agents["Admin"]],
    }

    # for key, val in allowed_transitions.items():
    #     st.write(f"{key.name}: {[v.name for v in val]}")

    entry_agent = get_entry_agent(agents)
    system_message_manager = "You are the manager of a research group your role is to manage the team and make sure the project is completed successfully."  

    groupchat = GroupChat(  
        # agents=[user_proxy, developer, planner, executor, quality_assurance],  
        agents=agents.values(),
        allowed_or_disallowed_speaker_transitions=allowed_transitions,  
        speaker_transitions_type=speaker_transitions_type,  
        messages=[], 
        max_round=max_round,  
        send_introductions=True  
    ) 
    manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config, system_message=system_message_manager)
    st.session_state.info = "Agents configured successfully!"
    
    return manager, entry_agent

def run(manager, user_proxy):
    st.session_state.info = "Running agents..."
    st.session_state.running = True
  
    task = st.text_input("Enter your task:", "What are the 5 leading GitHub repositories on llm for the legal domain?")  

    st.write(task)
    st.write("------------------")
    # st.write(user_proxy)
    
    if st.button("Run Task"):  
        st.info("Running task...")
        if st.session_state.first_query: 
            st.info("First query...")
            chat_result = user_proxy.initiate_chat(manager, message=task, clear_history=True)  
            st.session_state.first_query = False  
        else:  
            chat_result = user_proxy.initiate_chat(manager, message=task, clear_history=False)  
  
        st.session_state.messages.append(chat_result)  
        #st.write("Chat Summary:")  
        #st.write(chat_result.summary)
        st.write("Chat History:")  
        st.write(chat_result.chat_history)
  
    if st.button("Clear History"):  
        st.session_state.messages = []  
        st.session_state.first_query = True  
        st.write("Chat history cleared.")  
    
    return chat_result
    

if (st.session_state.able_to_run):

    if st.button("Run Agents", type="primary"):
        
        # TODO: add a check if agents are configured
        manager, entry_agent = config(allowed_transitions={})
        # task = "What are the 5 leading GitHub repositories on llm for the legal domain?"
        # chat_result = entry_agent.initiate_chat(manager, message=task, clear_history=True) 

        chat_result = run(manager=manager, user_proxy=entry_agent)
        st.write(chat_result)
        # st.rerun()




# agents_transitions = {}

# with st.expander("Setup allowed transitions", expanded=False):
#     st.write("Setup allowed transitions:")
#     for agent in st.session_state.saved_agents:
#         agents_transitions[agent["name"]] = st.multiselect(agent["name"], agents.keys(), agents.keys())

#     # st.write(agents_transitions)

#     allowed_transitions = {}
#     for key, val in agents_transitions.items():
#         allowed_transitions[agents[key]] = [agents[v] for v in val]

#     import json
#     # save agents_transitions into JSON file

#     st.download_button(
#         label="Download agents_transitions as JSON",
#         data=json.dumps(agents_transitions, indent=4),
#         file_name='agents_transitions.json',
#         mime='application/json'
#     )


#     # st.write("Updated allowed transitions:")
#     # for key, val in allowed_transitions.items():
#     #     st.write(f"{key.name}: {[v.name for v in val]}")
        
