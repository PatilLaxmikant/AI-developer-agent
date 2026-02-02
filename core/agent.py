import google.generativeai as genai
import json
import os
import requests
import platform
import psutil
import wikipedia
import yfinance as yf
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

class GeminiAgent:
    def __init__(self, api_key: str, model_name: str, project_manager):
        genai.configure(api_key=api_key)
        self.project_manager = project_manager
        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name,
            system_instruction=self._get_system_prompt(),
            generation_config={"response_mime_type": "application/json"}
        )
        self.chat = self.model.start_chat(history=[])
        self.pinned_files = []

    def _get_system_prompt(self):
        return """
        You are an AI Developer and Helpful Assistant.
        
        GOAL:
        Help the user build software, answer questions, and provide information.
        
        CAPABILITIES:
        1.  **Analyze**: Read files and directory structures.
        2.  **Execute**: Run terminal commands.
        3.  **Create/Edit**: Write files.
        4.  **Tools**: Use available tools:
            - `get_weather(city)`: Get weather for a city.
            - `web_search(query)`: Search the web for information.
            - `read_url(url)`: Read content from a webpage.
            - `get_system_info()`: Get system stats (CPU, RAM, OS).
            - `search_wikipedia(query)`: Search Wikipedia for a summary.
            - `get_stock_price(symbol)`: Get current stock price (e.g., AAPL).
            - `get_world_time(timezone)`: Get current time in a timezone (e.g., Europe/London).
        
        RESPONSE FORMAT:
        You must ALWAYS respond with a JSON object following this schema:
        {
            "thought": "Brief reasoning about what to do next.",
            "response": "Message to display to the user.",
            "actions": [
                {
                    "type": "command",
                    "command": "ls -la",
                    "description": "Listing files"
                },
                {
                    "type": "write",
                    "path": "src/app.py",
                    "content": "print('hello')",
                    "description": "Creating app.py"
                },
                {
                    "type": "tool",
                    "tool_name": "get_weather",
                    "args": {"city": "London"},
                    "description": "Checking weather"
                }
            ]
        }
        
        RULES:
        - If no action is needed, "actions" should be empty.
        - You can answer general questions directly in the "response" field.
        - Use tools when appropriate.
        - Always verify your code if possible.
        """

    def get_context_str(self):
        context = f"Current Working Directory: {self.project_manager.working_dir}\n"
        context += "Directory Structure:\n" + self.project_manager.list_files() + "\n"
        
        if self.pinned_files:
            context += "\nPINNED FILES:\n"
            for path in self.pinned_files:
                content = self.project_manager.read_file(path)
                context += f"--- {path} ---\n{content}\n--- End of {path} ---\n"
        
        return context

    def send_message(self, user_input: str):
        try:
            # Inject context into the message
            full_prompt = f"CONTEXT:\n{self.get_context_str()}\n\nUSER REQUEST:\n{user_input}"
            
            response = self.chat.send_message(full_prompt)
            return json.loads(response.text)
        except Exception as e:
            return {
                "thought": "Error processing request",
                "response": f"API Error: {str(e)}",
                "actions": []
            }
    
    def add_pinned_file(self, path):
        if path not in self.pinned_files:
            self.pinned_files.append(path)
            
    def remove_pinned_file(self, path):
        if path in self.pinned_files:
            self.pinned_files.remove(path)

    # Tool Implementation
    def get_weather(self, city: str):
        try:
            url = f"https://wttr.in/{city}?format=%C+%t"
            response = requests.get(url)
            if response.status_code == 200:
                return f"The weather in {city} is {response.text}."
            return "Something went wrong fetching weather."
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

    def web_search(self, query: str):
        try:
            results = DDGS().text(query, max_results=3)
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error searching web: {str(e)}"

    def read_url(self, url: str):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Get text and clean it up
            text = soup.get_text(separator=' ', strip=True)
            return text[:2000] + "..." if len(text) > 2000 else text
        except Exception as e:
            return f"Error reading URL: {str(e)}"

    def get_system_info(self):
        try:
            info = {
                "OS": platform.system(),
                "OS Release": platform.release(),
                "Architecture": platform.machine(),
                "CPU Usage": f"{psutil.cpu_percent()}%",
                "RAM Usage": f"{psutil.virtual_memory().percent}%"
            }
            return json.dumps(info, indent=2)
        except Exception as e:
            return f"Error getting system info: {str(e)}"

    def search_wikipedia(self, query: str):
        try:
            return wikipedia.summary(query, sentences=2)
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"

    def get_stock_price(self, symbol: str):
        try:
            stock = yf.Ticker(symbol)
            price = stock.history(period="1d")['Close'].iloc[-1]
            return f"The current price of {symbol} is ${price:.2f}"
        except Exception as e:
            return f"Error fetching stock price: {str(e)}"

    def get_world_time(self, timezone: str):
        try:
            url = f"http://worldtimeapi.org/api/timezone/{timezone}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return f"The time in {timezone} is {data['datetime']}"
            return "Invalid timezone or API error."
        except Exception as e:
            return f"Error fetching time: {str(e)}"
