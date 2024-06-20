import streamlit as st
import random
import string
import json

if 'input_keys' not in st.session_state:
    st.session_state.input_keys= []
if 'saved_agents' not in st.session_state:
    st.session_state.saved_agents = []

if 'info' not in st.session_state:
    st.session_state.info = None

info_placeholder = st.empty()

if not st.session_state.info:
    info_placeholder.info("Please add new agents or load agents from JSON file.")
else:
    info_placeholder.info(st.session_state.info)

number_agents_placeholder = st.write(f"Number of agents: {len(st.session_state.input_keys)}")

c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    if st.button("Add new agent"):
        st.session_state.input_keys.append(random.choice(string.ascii_uppercase)+str(random.randint(0,999999)))
        info_placeholder.success("New agent added successfully!")

with c2:
    if st.button("Load agents from JSON"):
        # uploaded_file = st.file_uploader("Choose a file")
        # if uploaded_file is not None:
        #     try:
        #         st.session_state.saved_agents = json.load(uploaded_file)
        #     except json.JSONDecodeError:
        #         st.error("Invalid JSON file!")

        # TODO: Load agents from JSON file (uncomment above code and remove below code)
        st.session_state.saved_agents = json.load(open("agents.json"))

        # st.session_state.saved_agents = agents
        for agent in st.session_state.saved_agents:
            st.session_state.input_keys.append(agent["input_key"])
        # st.session_state.input_keys = [random.choice(string.ascii_uppercase)+str(random.randint(0,999999)) for _ in range(len(agents))]
        st.session_state.info = "Agents loaded successfully!"
        st.rerun()

with c3:
    if st.button("Clear all agents", type="primary", disabled=not st.session_state.input_keys):
        st.session_state.input_keys = []
        st.session_state.saved_agents = []
        st.session_state.info = "All agents cleared successfully!"
        st.rerun()

def remove_agent(idx):
    st.session_state.input_keys.remove(idx)
    st.write(f"Agent {idx} removed successfully!")
    st.rerun()


def get_agent(idx):
    for agent in st.session_state.saved_agents:
        if agent["input_key"] == idx:
            return agent
    return None

if (st.session_state.saved_agents):
    # st.write("Agents loaded...")
    agents = st.session_state.saved_agents
else:
    # st.write("No agents loaded yet!")
    agents = []

# TODO: when loading agent from JSON, cannot add new agent (filled details are not propagated to the object, keeps being NULL)
for input_key in st.session_state.input_keys:
    with st.expander(f"Agent {input_key}", expanded=True):
        agent = get_agent(input_key)
        # st.write(agent)
        # st.caption(f"Agent {len(agents)+1}")
        agent_type = st.selectbox("Type", ["UserProxyAgent", "AssistantAgent"], key=f"type{input_key}", index=0 if agent and agent["type"] == "UserProxyAgent" else 1)
        agent_name = st.text_input("Name", key=f"name{input_key}", value=agent["name"] if agent else None)
        system_message = st.text_area("System Message", key=f"sys{input_key}", value=agent["system_message"] if agent else None)
        description = st.text_area("Description", key=f"desc{input_key}", value=agent["description"] if agent else None)
        human_input_mode = st.selectbox("Human Input Mode", ["ALWAYS", "NEVER"], key=f"mode{input_key}", index=0 if agent and agent["human_input_mode"] == "ALWAYS" else 1)
        if st.button("Remove Agent", key=f"remove{input_key}"):
            remove_agent(input_key)
            continue
        if not agent:
            agents.append(
                {
                    "input_key": input_key,
                    "type": agent_type,
                    "name": agent_name,
                    "system_message": system_message,
                    "description": description,
                    "human_input_mode": human_input_mode
                }
            )
            st.info(f"Agent {input_key} added successfully!")

with st.expander("Defined agents", expanded=False):
    # st.write("Defined Agents:")
    for val in agents:
        st.json(val)


if (agents):
    if st.button("Save Agents", disabled=not agents):
        if len(agents):
            st.session_state.saved_agents = agents
            st.session_state.info = "Agents saved successfully!"
            # Optionally, provide a download link for the JSON file
            st.download_button(
                label="Download Agents as JSON",
                data=json.dumps(st.session_state.saved_agents, indent=4),
                file_name='agents.json',
                mime='application/json'
            )
            st.page_link("pages/01_setup_transitions.py", label="Setup transitions", icon="🔄")
        else:
            st.session_state.info = "No agents defined yet!"
