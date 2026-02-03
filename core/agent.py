# import json
# from openai import OpenAI
# from config import API_KEY, BASE_URL, MODEL_NAME
# from tools import available_tools

# # Initialize Client
# client = OpenAI(
#     api_key=API_KEY,
#     base_url=BASE_URL
# )

# SYSTEM_PROMPT = """
# You are a powerful AI Assistant capable of using various tools to solve problems.
# You operate in a loop of: PLAN -> ACTION -> OBSERVE -> OUTPUT.

# 1. **PLAN**: Analyze the user's request and plan the next step.
# 2. **ACTION**: Select a tool to execute that step.
# 3. **OBSERVE**: Read the output of the tool.
# 4. **OUTPUT**: If the task is complete, provide the final answer.

# **Rules:**
# - Always output strictly in JSON format.
# - Do not output markdown code blocks (like ```json).
# - Only use the tools listed below.
# - If a tool fails, try to understand why and retry or ask the user.
# - For ACTION, the "input" field can be:
#   - a simple string for single-argument tools, OR
#   - a JSON string representing an object (e.g. "{\\"path\\": \\"file.txt\\", \\"content\\": \\"hello\\"}")

# **Output JSON Structure:**
# {
#     "step": "plan" | "action" | "output",
#     "content": "Your thought process or final answer",
#     "function": "tool_name_here" (only for 'action'),
#     "input": "tool_input_here" (only for 'action')
# }

# **Available Tools:**

# Core:
# - get_weather(city)
# - run_command(cmd)
# - web_search(query)
# - get_system_info()
# - read_file(path)
# - write_file(path, content)
# - calculate(expression)
# - get_time()

# NLP / Knowledge:
# - wiki_summary(query, sentences=3)
# - translate_text(text, target_lang="en")
# - detect_language(text)
# - sentiment(text)
# - summarize_text(text, max_tokens=130)
# - solve_equation(equation, var="x")

# System / Files:
# - get_disk_usage(path="/")
# - list_processes(limit=10)
# - list_files(path=".")
# - zip_path(path, zip_name="archive.zip")
# - unzip_file(zip_path, dest="./unzipped")
# - system_uptime()
# - tail_file(path, lines=20)

# Networking / Web:
# - ip_geolocate(ip="")
# - get_public_ip()
# - fetch_page_title(url)
# - fetch_page_meta(url)
# - shorten_url(url)
# - hn_top_stories(limit=5)
# - rss_headlines(url, limit=5)
# - network_speed_test()
# - get_ticker_price(symbol)

# Date / Time / Geo:
# - convert_time(time_str, from_tz, to_tz, fmt="%Y-%m-%d %H:%M")
# - is_public_holiday(date_str, country="IN")
# - geocode_address(address)
# - reverse_geocode(lat, lon)

# Data / Utils:
# - convert_currency(amount, from_cur, to_cur)
# - pretty_json(raw)
# - markdown_to_html(text)
# - generate_password(length=16)
# - generate_uuid()

# Productivity:
# - add_todo(item)
# - list_todos()
# - add_note(text)
# - list_notes(limit=10)

# Media:
# - image_info(path)
# - text_to_speech(text, out_file="output.wav")
# - generate_qr(data, filename="qr.png")
# - pdf_to_text(path)

# Dev tools:
# - format_python(code)
# - lint_python(code, filename="temp_code.py")

# Clipboard & Fun:
# - clipboard_set(text)
# - clipboard_get()
# - programming_joke()
# """

# def process_request(messages):
#     """
#     Process a user request and yield events for the UI.
#     messages: List of message dicts [{"role": "user", "content": "..."}]
#     """
#     # Ensure system prompt is first
#     if not messages or messages[0]["role"] != "system":
#         messages.insert(0, { "role": "system", "content": SYSTEM_PROMPT })

#     while True:
#         try:
#             response = client.chat.completions.create(
#                 model=MODEL_NAME,
#                 response_format={"type": "json_object"},
#                 messages=messages
#             )

#             content = response.choices[0].message.content
#             messages.append({ "role": "assistant", "content": content })
            
#             try:
#                 parsed_response = json.loads(content)
#             except json.JSONDecodeError:
#                 yield {"type": "error", "content": f"Invalid JSON from LLM: {content}"}
#                 # Feed error back to LLM
#                 messages.append({ "role": "user", "content": "Error: You returned invalid JSON. Please correct it." })
#                 continue

#             step = parsed_response.get("step")

#             if step == "plan":
#                 yield {"type": "plan", "content": parsed_response.get("content")}
#                 continue

#             elif step == "action":
#                 tool_name = parsed_response.get("function")
#                 tool_input = parsed_response.get("input")

#                 yield {"type": "action", "tool": tool_name, "input": tool_input}

#                 if tool_name in available_tools:
#                     tool_func = available_tools[tool_name]
#                     try:
#                         # Argument parsing logic
#                         args = tool_input
#                         if isinstance(tool_input, str):
#                             try:
#                                 args = json.loads(tool_input)
#                             except json.JSONDecodeError:
#                                 pass
                        
#                         if isinstance(args, dict):
#                             output = tool_func(**args)
#                         elif isinstance(args, list):
#                             output = tool_func(*args)
#                         elif args in ("", None):
#                              # Handle no-arg tools called with empty string/None
#                             output = tool_func()
#                         else:
#                             output = tool_func(args)
                                
#                     except Exception as e:
#                          output = f"Error calling tool: {str(e)}"

#                     yield {"type": "observe", "content": output}
                    
#                     messages.append({ 
#                         "role": "user", 
#                         "content": json.dumps({ "step": "observe", "output": output }) 
#                     })
#                 else:
#                     error_msg = f"Tool '{tool_name}' not found."
#                     yield {"type": "error", "content": error_msg}
#                     messages.append({ 
#                         "role": "user", 
#                         "content": json.dumps({ "step": "error", "output": error_msg }) 
#                     })
#                 continue

#             elif step == "output":
#                 yield {"type": "output", "content": parsed_response.get("content")}
#                 break
            
#             else:
#                 yield {"type": "error", "content": f"Unknown step: {step}"}
#                 break

#         except Exception as e:
#             yield {"type": "error", "content": f"Critical Error: {str(e)}"}
#             break

