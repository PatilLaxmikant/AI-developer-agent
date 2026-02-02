# 🤖 Gemini AI Developer

An advanced AI developer agent built with **Streamlit** and **Google Gemini API**. This tool can help you write code, execute commands, analyze your project, and fetch real-world data—all through a chat interface.

## ✨ Features

*   **Chat with AI**: Ask coding questions or general queries.
*   **Project Management**:
    *   📂 **File Explorer**: View your project structure and read files.
    *   📌 **Workspace**: All generated files are safely isolated in a `workspace/` directory.
    *   📦 **Download**: Zip and download your entire workspace with one click.
*   **Autonomous Agent**:
    *   Can write files and run shell commands (with "Safe Mode" approval).
    *   Executes complex tasks by chaining multiple steps.
*   **Real-World Tools**:
    *   🌤️ **Weather**: Get current weather (`get_weather`).
    *   🌐 **Web Search**: Search the internet (`web_search`).
    *   📖 **Wikipedia**: Get summaries (`search_wikipedia`).
    *   📈 **Stocks**: Get stock prices (`get_stock_price`).
    *   🔗 **Read URL**: Extract text from websites (`read_url`).
    *   🖥️ **System Info**: View CPU/RAM usage (`get_system_info`).
    *   🌍 **World Time**: Check time in any timezone (`get_world_time`).

## 🛠️ Installation

1.  **Clone the repository** (or download the source):
    ```bash
    git clone https://github.com/PatilLaxmikant/AI-developer-agent.git
    cd AI-developer-agent
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

1.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

2.  **Configure**:
    *   **API Key**: The key is hardcoded in the app for convenience, but for production, use environment variables.
    *   **Working Directory**: Defaults to `workspace`.
    *   **Safe Mode**: Enabled by default. You will be asked to approve any file writes or terminal commands. Tool usage (like weather) is auto-approved.

## 📂 Project Structure

*   `app.py`: Main application entry point.
*   `core/`: Core logic.
    *   `agent.py`: Gemini Agent implementation (prompts, tools, context).
    *   `project_manager.py`: File system and command execution logic.
*   `ui/`: User Interface.
    *   `components.py`: Reusable Streamlit components (sidebar, chat bubbles).
*   `requirements.txt`: Python dependencies.
*   `workspace/`: Default directory where the AI creates code files.

## 🛡️ Security Note

*   This tool allows execution of shell commands. Use **Safe Mode** to review actions before they run.
*   Do not run this on a public server without adding authentication and containerization (Docker).
