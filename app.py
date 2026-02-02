import streamlit as st
import os
from dotenv import load_dotenv
from core.project_manager import ProjectManager
from core.agent import GeminiAgent
from ui.components import render_sidebar, render_chat_message, render_action_approval, render_file_explorer

# Load environment variables
load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="Gemini AI Developer", page_icon="🤖", layout="wide")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_actions" not in st.session_state:
    st.session_state.pending_actions = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "should_continue" not in st.session_state:
    st.session_state.should_continue = False

# --- Sidebar & Config ---
model_name, working_dir, safe_mode = render_sidebar()
api_key = os.getenv("GEMINI_API_KEY")

# --- Initialization ---
if api_key and working_dir:
    if st.session_state.agent is None or st.session_state.agent.model_name != model_name:
        pm = ProjectManager(working_dir)
        st.session_state.agent = GeminiAgent(api_key, model_name, pm)
        st.success(f"Agent initialized in {working_dir}")

    # Render File Explorer
    render_file_explorer(st.session_state.agent.project_manager, st.session_state.agent.pinned_files)

else:
    st.warning("Please enter API Key and Working Directory to start.")
    st.stop()

# --- Main Chat Interface ---
st.title("🤖 Gemini AI Developer")

# Display History
for msg in st.session_state.messages:
    if not msg.get("hidden"):
        render_chat_message(msg["role"], msg["content"], msg.get("output"))

# --- Action Handling ---
def execute_actions(actions):
    results = []
    for action in actions:
        if action["type"] == "command":
            out = st.session_state.agent.project_manager.run_command(action["command"])
            results.append(f"$ {action['command']}\n{out}")
        elif action["type"] == "write":
            res = st.session_state.agent.project_manager.write_file(action["path"], action["content"])
            results.append(f"Writing {action['path']}: {res}")
        elif action["type"] == "tool":
            tool_name = action["tool_name"]
            args = action.get("args", {})
            
            if tool_name == "get_weather":
                out = st.session_state.agent.get_weather(**args)
                results.append(f"Tool 'get_weather' output: {out}")
            elif tool_name == "web_search":
                out = st.session_state.agent.web_search(**args)
                results.append(f"Tool 'web_search' output: {out}")
            elif tool_name == "read_url":
                out = st.session_state.agent.read_url(**args)
                results.append(f"Tool 'read_url' output: {out}")
            elif tool_name == "get_system_info":
                out = st.session_state.agent.get_system_info()
                results.append(f"Tool 'get_system_info' output: {out}")
            else:
                results.append(f"Unknown tool: {tool_name}")
    return "\n".join(results)

# Pending Actions (Safe Mode)
if st.session_state.pending_actions:
    approval = render_action_approval(st.session_state.pending_actions)
    
    if approval is True: # Approved
        with st.spinner("Executing actions..."):
            output = execute_actions(st.session_state.pending_actions)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "✅ Actions executed successfully.",
                "output": output
            })
            # Feed output back to agent
            st.session_state.messages.append({
                "role": "user",
                "content": f"System Execution Result:\n{output}\n\nProceed with the next step."
            })
            st.session_state.pending_actions = []
            st.session_state.should_continue = True # Trigger loop
            st.rerun()
            
    elif approval is False: # Rejected
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❌ Actions rejected by user."
        })
        st.session_state.pending_actions = []
        st.session_state.should_continue = False
        st.rerun()

# --- Autonomous Loop ---
if st.session_state.should_continue and not st.session_state.pending_actions:
    with st.spinner("🤖 AI is thinking..."):
        # Get last message (System Result)
        last_msg = st.session_state.messages[-1]["content"]
        response_data = st.session_state.agent.send_message(last_msg)
        
        thought = response_data.get("thought", "")
        response_text = response_data.get("response", "")
        actions = response_data.get("actions", [])
        
        print(f"DEBUG: Thought: {thought}")
        print(f"DEBUG: Response: {response_text}")
        print(f"DEBUG: Actions: {actions}")
        
        full_response = f"_{thought}_\n\n{response_text}"
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        if actions:
            # Check if all actions are tools
            all_tools = all(action["type"] == "tool" for action in actions)

            if safe_mode and not all_tools:
                for action in actions:
                    if action["type"] == "write":
                        res = st.session_state.agent.project_manager.write_file(action["path"], action["content"], dry_run=True)
                        if res["success"]:
                            action["diff"] = res["diff"]
                st.session_state.pending_actions = actions
                st.session_state.should_continue = False # Pause for approval
                st.rerun()
            else:
                output = execute_actions(actions)
                
                # Show output directly
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": output, # Show output directly
                    "output": None
                })
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"System Execution Result:\n{output}\n\nProceed with the next step.",
                    "hidden": True
                })
                st.session_state.should_continue = True # Continue loop
                st.rerun()
        else:
            st.session_state.should_continue = False # Stop if no actions
            st.rerun()

# --- Chat Input ---
if prompt := st.chat_input("How can I help you?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get Agent Response
    with st.spinner("Thinking..."):
        response_data = st.session_state.agent.send_message(prompt)
    
    thought = response_data.get("thought", "")
    response_text = response_data.get("response", "")
    actions = response_data.get("actions", [])

    # Display Agent Response
    full_response = f"_{thought}_\n\n{response_text}"
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    with st.chat_message("assistant"):
        st.markdown(full_response)

    # Handle Actions
    if actions:
        # Check if all actions are tools (safe to auto-run)
        all_tools = all(action["type"] == "tool" for action in actions)
        
        if safe_mode and not all_tools:
            # Calculate diffs for write actions
            for action in actions:
                if action["type"] == "write":
                    res = st.session_state.agent.project_manager.write_file(action["path"], action["content"], dry_run=True)
                    if res["success"]:
                        action["diff"] = res["diff"]
            
            st.session_state.pending_actions = actions
            st.session_state.should_continue = False # Wait for approval
            st.rerun()
        else:
            # Auto-execute (Safe Mode OFF OR All Actions are Tools)
            output = execute_actions(actions)
            
            # Show output directly
            st.session_state.messages.append({
                "role": "assistant",
                "content": output, # Show output directly
                "output": None
            })
            st.session_state.messages.append({
                "role": "user",
                "content": f"System Execution Result:\n{output}\n\nProceed with the next step.",
                "hidden": True
            })
            st.session_state.should_continue = True # Start loop
            st.rerun()
