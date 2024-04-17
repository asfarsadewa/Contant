import time
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(ASSISTANT_ID) #see readme if you are not familiar on how to create an assistant

thread = client.beta.threads.create()

def searchInternet(query):
    search = GoogleSearch({"q": query, "api_key": SERPAPI_API_KEY})
    results = search.get_dict()
    return results.get('organic_results', [])

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

def get_response(thread):
    messages = client.beta.threads.messages.list(thread_id=thread.id, order="desc", limit=1)
    return messages.data[0].content[0].text.value

def wait_on_run(run, thread):
    while run.status in ["queued", "in_progress", "requires_action"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        if run.status == "requires_action":
            required_action = run.required_action
            if required_action.type == 'submit_tool_outputs':
                tool_call = required_action.submit_tool_outputs.tool_calls[0]
                query = json.loads(tool_call.function.arguments).get('query')
                output = searchInternet(query)
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output)
                    }]
                )
        time.sleep(0.2)
    return run

def consult():
    print(f"{assistant.name} - Session Opened..")
    while True:
        user_input = input("Me: ")
        if user_input == "!quit":
            break
        run = submit_message(assistant.id, thread, user_input)    
        run = wait_on_run(run, thread)
        print(f"{assistant.name}: " + "\033[92m" + get_response(thread) + "\033[0m")

consult()