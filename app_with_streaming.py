import os
import json
from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
from serpapi import GoogleSearch
from typing_extensions import override

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

thread = client.beta.threads.create()

def searchInternet(query):
    search = GoogleSearch({"q": query, "api_key": SERPAPI_API_KEY})
    results = search.get_dict()
    return results.get('organic_results', [])

class EventHandler(AssistantEventHandler):
    def __init__(self, thread_id):
        super().__init__()
        self.thread_id = thread_id
        self.is_tool_call_active = False
        self.first_response = True
        self.function_call_args_buffer = ""

    @override
    def on_text_created(self, text) -> None:
        if self.first_response:
            print()  # Add a new line before the assistant's first response
            self.first_response = False
        print(f"{assistant.name}: ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"{assistant.name}: {tool_call.type}", flush=True)
        self.is_tool_call_active = True
        self.function_call_args_buffer = ""  # Reset the buffer for new tool calls

    @override
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'function':
            if hasattr(delta.function, 'arguments') and delta.function.arguments:
                self.function_call_args_buffer += delta.function.arguments
        elif delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print("\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    @override
    def on_event(self, event):
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool_call in data.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "searchInternet":
                # Use accumulated arguments
                query = json.loads(self.function_call_args_buffer)["query"]
                output = searchInternet(query)
                tool_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps({"results": output})})

        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Create a separate EventHandler instance for this stream
        new_event_handler = EventHandler(self.thread_id)
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            event_handler=new_event_handler,
        ) as stream:
            stream.until_done()
            print()

def submit_user_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant_id,
        event_handler=EventHandler(thread.id),
    ) as stream:
        stream.until_done()
        print()

def consult():
    print(f"{assistant.name} - Session Opened..")
    while True:
        user_input = input("\nMe: ")
        if user_input == "!quit":
            break
        submit_user_message(assistant.id, thread, user_input)

consult()
