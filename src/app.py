import asyncio
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import asyncio
import os
from datetime import datetime
from magentic_one_helper import MagenticOneHelper


# Initialize session state for instructions
if 'instructions' not in st.session_state:
    st.session_state['instructions'] = ""

if 'running' not in st.session_state:
    st.session_state['running'] = False

if "final_answer" not in st.session_state:
    st.session_state["final_answer"] = None

st.title("MagenticOne Workflow Runner")
st.caption("This app runs a MagenticOne workflow based on the instructions provided.")
# Input for instructions
instructions = st.text_input("Enter your instructions:", value="generate code to calculate 34*87 in Python and calculate the result")
run_button = st.button("Run Agents", type="primary")

def display_log_message(log_entry):     
    # _log_entry_json  = json.loads(log_entry)
    _log_entry_json  = log_entry

    _type = _log_entry_json.get("type", None)
    _timestamp = _log_entry_json.get("timestamp", None)
    _timestamp = datetime.fromisoformat(_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    if _type == "OrchestrationEvent":
        st.markdown(f"**From {_log_entry_json['source']} @ {_timestamp}:**")
        st.write(_log_entry_json["message"])
        st.write("---")
    elif _type == "LLMCallEvent":
        st.caption(f'{_timestamp} LLM Call [prompt_tokens: {_log_entry_json["prompt_tokens"]}, completion_tokens: {_log_entry_json["completion_tokens"]}]')
    else:
        st.caption("Invalid log entry format.")


async def main(task, logs_dir="./logs"):
    
    # create folder for logs if not exists
    if not os.path.exists(logs_dir):    
        os.makedirs(logs_dir)

    # Initialize MagenticOne
    magnetic_one = MagenticOneHelper(logs_dir=logs_dir)
    await magnetic_one.initialize()
    print("MagenticOne initialized.")

    # Create task and log streaming tasks
    task_future = asyncio.create_task(magnetic_one.run_task(task))
    final_answer = None

    with st.container(border=True):    
        # Stream and process logs
        async for log_entry in magnetic_one.stream_logs():
            display_log_message(log_entry=log_entry)

    # Wait for task to complete
    await task_future

    # Get the final answer
    final_answer = magnetic_one.get_final_answer()

    if final_answer is not None:
        print(f"Final answer: {final_answer}")
        st.session_state["final_answer"] = final_answer
    else:
        print("No final answer found in logs.")
        st.session_state["final_answer"] = None
        st.warning("No final answer found in logs.")

if run_button and instructions:
    st.session_state['instructions'] = instructions
    st.session_state['running'] = True
    st.write("Instructions:", st.session_state['instructions'])

    with st.spinner("Running the workflow..."):
        # asyncio.run(main("generate code and calculate with python 132*82"))
        asyncio.run(main(st.session_state['instructions']))

    final_answer = st.session_state["final_answer"]
    if final_answer:
        st.success("Task completed successfully.")
        st.write("## Final answer:")
        st.write(final_answer)
    else:
        st.error("Task failed.")
        st.write("Final answer not found.")
