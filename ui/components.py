import streamlit as st
import shutil
import os

def render_sidebar():
    with st.sidebar:
        st.title("⚡ AI Developer Config")
        
        model_options = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
        model_name = st.selectbox("Model", model_options, key="model_selector")
        
        st.divider()
        
        working_dir = st.text_input("Working Directory", value=st.session_state.get("working_dir", "workspace"))
        
        safe_mode = st.toggle("🛡️ Safe Mode", value=True, help="Require approval for all actions.")
        
        return model_name, working_dir, safe_mode

def render_chat_message(role, content, output=None):
    with st.chat_message(role):
        st.markdown(content)
        if output:
            with st.expander("View Output"):
                st.code(output, language="bash")

def render_action_approval(actions):
    """
    Renders a UI for approving/rejecting actions.
    Returns True if approved, False if rejected, None if pending.
    """
    st.info("⚠️ **Review Proposed Actions**")
    
    for i, action in enumerate(actions):
        st.markdown(f"**{i+1}. {action['type'].upper()}**")
        if action['type'] == 'command':
            st.code(action['command'], language="bash")
        elif action['type'] == 'write':
            st.markdown(f"File: `{action['path']}`")
            if 'diff' in action:
                st.markdown("Changes:")
                st.code(action['diff'], language="diff")
            else:
                with st.expander("View Content"):
                    st.code(action['content'])
        elif action['type'] == 'tool':
            st.markdown(f"Tool: `{action['tool_name']}`")
            st.json(action['args'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve & Run", type="primary", key="approve_btn"):
            return True
    with col2:
        if st.button("❌ Reject", key="reject_btn"):
            return False
            
    return None

def render_file_explorer(project_manager, pinned_files):
    st.sidebar.divider()
    st.sidebar.subheader("📂 Project Files")
    
    # Simple file tree view
    file_tree = project_manager.list_files()
    st.sidebar.code(file_tree, language="text")
    
    # Download Button logic
    if st.sidebar.button("📦 Zip & Download Workspace"):
        # Create a zip file of the working directory
        try:
            # Check if workspace exists
            if not os.path.exists(project_manager.working_dir):
                st.sidebar.error("Workspace directory not found!")
            else:
                # Create zip in a temp location or current dir
                shutil.make_archive("workspace_archive", 'zip', project_manager.working_dir)
                
                with open("workspace_archive.zip", "rb") as f:
                    st.sidebar.download_button(
                        label="⬇️ Download Zip",
                        data=f,
                        file_name="workspace.zip",
                        mime="application/zip"
                    )
        except Exception as e:
            st.sidebar.error(f"Error creating zip: {e}")

    st.sidebar.subheader("📌 Pinned Context")
    for f in pinned_files:
        st.sidebar.caption(f"📄 {f}")
