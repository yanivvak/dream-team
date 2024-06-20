import streamlit as st
import random
import string
import json

if 'input_keys' not in st.session_state:
    st.session_state.input_keys= []
if 'saved_agents' not in st.session_state:
    st.session_state.saved_agents = []
if 'able_to_run' not in st.session_state:
    st.session_state.able_to_run = False
if 'saved_transitions' not in st.session_state:
    st.session_state.saved_transitions = {}

if 'info' not in st.session_state:
    st.session_state.info = None

info_placeholder = st.empty()

if not st.session_state.info:
    info_placeholder.info("Please add new agents or load agents from JSON file.")
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
    st.page_link("pages/01_setup.py", icon="🤖")
    st.session_state.able_to_run = False

if st.session_state.able_to_run:
    # st.write("Agents loaded...")


    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        # if st.button("Add new agent"):
        #     st.session_state.input_keys.append(random.choice(string.ascii_uppercase)+str(random.randint(0,999999)))
        #     info_placeholder.success("New agent added successfully!")
        pass

    with c2:
        if st.button("Load agents transitions from JSON"):
            # uploaded_file = st.file_uploader("Choose a file")
            # if uploaded_file is not None:
            #     try:
            #         st.session_state.saved_agents = json.load(uploaded_file)
            #     except json.JSONDecodeError:
            #         st.error("Invalid JSON file!")

            # TODO: Load agents_transitions from JSON file (uncomment above code and remove below code)
            st.session_state.saved_transitions = json.load(open("agents_transitions.json"))

            # # st.session_state.saved_agents = agents
            # for agent in st.session_state.saved_agents:
            #     st.session_state.input_keys.append(agent["input_key"])
            # # st.session_state.input_keys = [random.choice(string.ascii_uppercase)+str(random.randint(0,999999)) for _ in range(len(agents))]
            st.session_state.info = "Agents transitions loaded successfully!"
            st.rerun()

    with c3:
        # if st.button("Clear all agents", type="primary", disabled=not st.session_state.input_keys):
        #     st.session_state.input_keys = []
        #     st.session_state.saved_agents = []
        #     st.session_state.info = "All agents cleared successfully!"
        #     st.rerun()
        pass




    if len(st.session_state.saved_transitions) == 0:
        agents_transitions = {}
        # _agents = [agent["name"] for agent in st.session_state.saved_agents]
        _agents_dict = {agent["name"]: agent for agent in st.session_state.saved_agents}
        with st.expander("Setup allowed transitions", expanded=True):
            # st.write("Setup allowed transitions:")
            for agent in st.session_state.saved_agents:
                agents_transitions[agent["name"]] = st.multiselect(agent["name"], _agents_dict.keys(), _agents_dict.keys())

            # st.write(agents_transitions)

            # allowed_transitions = {}
            # for key, val in agents_transitions.items():
            #     allowed_transitions[_agents_dict[key]] = [_agents_dict[v] for v in val]

            import json
            # save agents_transitions into JSON file

            st.download_button(
                label="Download agents_transitions as JSON",
                data=json.dumps(agents_transitions, indent=4),
                file_name='agents_transitions.json',
                mime='application/json'
            )

            if st.button("Save allowed transitions", disabled=False):
                st.session_state.saved_transitions = agents_transitions
                st.rerun()



            # st.write("Updated allowed transitions:")
            # for key, val in allowed_transitions.items():
            #     st.write(f"{key.name}: {[v.name for v in val]}")
    else:
        st.write("Let's go next to actually run the agents!")
        # agents_transitions = st.session_state.saved_transitions
        with st.expander("Defined agents transifions", expanded=False):
            st.write(st.session_state.saved_transitions)
        st.page_link("pages/02_run.py", label="Run", icon="🏃‍♂️")