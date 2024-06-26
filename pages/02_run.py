import streamlit as st    
from autogen import Agent
from autogen.agentchat import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager  
from autogen.oai.openai_utils import config_list_from_json  
import warnings  


import streamlit.components.v1 as components    
def mermaid(placehoder, code: str) -> None:
    with placehoder:
        components.html(
        f"""
        <pre class="mermaid">
            {code}
        </pre>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """, height=250
    )
    return placehoder


def display_graph(placeholder, active_node=None):

    nodes = []
    edges = []
    i = 0
    # flow_key = st.session_state['flow_key']
    with placeholder:
        for k,v in st.session_state.saved_transitions.items():
            color = "red" if k == active_node else "green"
            # nodes.append(Node(id=k, size=40, color= color, title=k[0] ) )
            # nodes.append(StreamlitFlowNode(k, (0, i), {'label': k}, 'default', 'right', 'left', style={'backgroundColor': color}))
            if active_node is not None and k == active_node:
                nodes.append(f"id{k}({k})")
            for _v in v:
                # edges.append( Edge(source=k, target=_v, type="CURVE_SMOOTH"))
                # edges.append(StreamlitFlowEdge(f"{k}-{_v}", k, _v, animated=True))
                edges.append(f"id{k}({k})-->id{_v}({_v})")
            i += 1
        # nodes.sort(key=lambda x: x.id)
    #     streamlit_flow(flow_key, nodes, edges, layout=TreeLayout(direction='right'), fit_view=True)
        
    #     # Delete the old key from the state and make a new key so that streamlit is 
    #     # forced to re-render the component with the updated node list
    #     # if flow_key in st.session_state and flow_key:
    #     #     del st.session_state[flow_key]
    #     #     st.session_state['flow_key'] = f'hackable_flow_{random.randint(0, 1000)}'
    # return nodes, edges

    # construct mermaid code

    code = "flowchart LR\n\n"
    # for node in nodes:
    #     code += f"id{node}({node})[{node}]\n"
    for edge in edges:
        code += f"{edge}\n\n"
    
    code+= f"style id{active_node} fill:#f9f,stroke:#333,stroke-width:4px\n\n"

    # st.write(code)
    mermaid(placeholder, code)


# # TODO: REMOVE THIS DEBUG STUFF
# import json
# st.session_state.saved_agents = json.load(open("agents.json"))
# st.session_state.saved_transitions = json.load(open("agents_transitions.json"))
  
warnings.filterwarnings('ignore')  

# Callback function to print messages
# based on https://github.com/microsoft/autogen/issues/478
def print_messages_callback(recipient, messages, sender, config):     
    message = messages[-1]

    display_graph(placeholder, active_node=message['name'])

    with st.expander(f"From {message['name']} to {recipient.name}", expanded=False):
        # st.write(f"From {sender} to {recipient}: ")
        st.write(message["content"])

    return False, None  # required to ensure the agent communication flow continues

def display_messages_history(messages):
    with st.container(border=True):
        st.write("Chat History:")
        # Output the final chat history showing the original 4 messages and resumed messages
        for i, message in enumerate(messages):
            try:
                sender = message["name"]
            except:
                sender = "AdminX"    
            with st.expander(f"{i+1}: From {sender}", expanded=False):
                st.write(message["content"])

    return False, None  # required to ensure the agent communication flow continues

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
if 'saved_transitions' not in st.session_state:
    st.session_state.saved_transitions = {}
# Initialize session state for messages and first query flag  
if 'messages' not in st.session_state:  
    st.session_state.messages = []  
if 'first_query' not in st.session_state:  
    st.session_state.first_query = True  


# # TODO: REMOVE
# import json
# st.session_state.saved_agents = json.load(open("agents.json"))

info_placeholder = st.empty()

if not st.session_state.info:
    info_placeholder.empty()
else:
    info_placeholder.info(st.session_state.info)

if (st.session_state.saved_agents):
    # st.write("Agents loaded...")
    agents = st.session_state.saved_agents
    st.session_state.able_to_run = True
else:
    st.warning("No agents Created yet!")
    agents = []
    st.write("First, let's create a new agents.")
    st.page_link("pages/01_setup.py", icon="ð¤")
    st.session_state.able_to_run = False

if (st.session_state.saved_transitions):
    st.session_state.able_to_run = True
else:
    st.warning("No transitions defined yet!")
    st.page_link("pages/01_setup.py", icon="ð¤")
    st.session_state.able_to_run = False



with st.expander("Defined agents", expanded=False):
    # st.write("Defined Agents:")
    for val in agents:
        st.json(val)

with st.expander("Defined agents transifions", expanded=False):
    st.write(st.session_state.saved_transitions)

# TODO: add a check if agents are configured
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
                    is_termination_msg=lambda msg: "terminate" in msg.get("content").lower(),
                )
                _a.register_reply(
                    [Agent, None],
                    reply_func=print_messages_callback
                )
                _a.get_human_input = lambda prompt: "exit" # TODO: this is a hack to always exit the conversation
            elif agent["human_input_mode"] == "NEVER":
                _a = UserProxyAgent(
                    name=agent["name"],
                    system_message=agent["system_message"],
                    description=agent["description"],
                    human_input_mode=agent["human_input_mode"],
                    code_execution_config={  
                        "last_n_messages": 20,  
                        "work_dir": "dream",  
                        "use_docker": True,  
                    }
                )
                _a.register_reply(
                    [Agent, None],
                    reply_func=print_messages_callback
                )
        elif agent["type"] == "AssistantAgent":
            _a = AssistantAgent(
                name=agent["name"],
                system_message=agent["system_message"],
                description=agent["description"],
                llm_config=gpt4_config
            )
            _a.register_reply(
                [Agent, None],
                reply_func=print_messages_callback
            )
            
        else:
            st.error(f"Unknown agent type: {agent['type']}")
            st.stop()
        
        

        agents[agent["name"]] = _a

    for k, v in st.session_state.saved_transitions.items():
        allowed_transitions[agents[k]] = [agents[i] for i in v]

    entry_agent = get_entry_agent(agents)
    system_message_manager = "You are the manager of a research group your role is to manage the team and make sure the project is completed successfully."  

    groupchat = GroupChat(  
        agents=[v for _,v in agents.items()],
        allowed_or_disallowed_speaker_transitions=allowed_transitions,  
        speaker_transitions_type=speaker_transitions_type,  
        messages=[], 
        max_round=max_round,  
        send_introductions=True  
    ) 
    manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config, system_message=system_message_manager)
    st.session_state.info = "Agents configured successfully!"
    
    return manager, entry_agent

def run(manager, user_proxy, task):
    st.session_state.info = "Running agents..."
    st.session_state.running = True
    
    if st.session_state.first_query: 
        chat_result = user_proxy.initiate_chat(manager, message=task, clear_history=True)  
        st.session_state.first_query = False  
    else:  
        last_agent, last_message = manager.resume(messages=st.session_state.messages)
        chat_result = user_proxy.initiate_chat(manager, message=task, clear_history=False)  

    st.session_state.messages = chat_result.chat_history
      
    # st.write("Chat Summary:")  
    with st.expander("Chat Summary", expanded=True):
        st.write(chat_result.summary)
    with st.expander("Chat History", expanded=False):
        st.write(chat_result.chat_history)

    st.session_state.running = False
    st.session_state.info = "Running agents done."
    return chat_result
  
    # if st.button("Clear History"):  
    #     st.session_state.messages = []  
    #     st.session_state.first_query = True  
    #     st.write("Chat history cleared.")  
    
    # return None
    

if (st.session_state.able_to_run):

    # display messages if there has been history create by previous runs
    if st.session_state.messages:
        display_messages_history(st.session_state.messages)

    task = st.text_input("Enter your task:", "What are the 10 leading GitHub repositories on llm for the legal domain?")  
    with st.container(border=True):
        placeholder = st.empty()
        display_graph(placeholder, active_node="Admin")

    # handling the button label based on the first query
    if st.session_state.first_query:
        button_label = "Run Agents"
    else:
        button_label = "Continue Agents' flow with new task"

    if st.button(button_label, type="primary"):
        
        manager, user_proxy = config(allowed_transitions={})

        with st.spinner("Running agents..."):
            chat_result = run(manager=manager, user_proxy=user_proxy, task=task)

        st.write("Done! But you can follow-up the conversation with a new task.")
        

