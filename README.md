# Contant
Contant - A GPT-4 console Assistant

A minimalistic sample console app of an OpenAI GPT-4 assistant, equipped with a function to search the internet (via SERPAPI).
I wrote this because I was learning about function calling on the assistant API, so it's just a rough sample.
The code assumes you know how to create an assistant and putting functions on it.
If not, maybe this helps:

```
assistant = client.beta.assistants.create(
    name="AssistantMan",
    instructions="You answer to everything concisely. If you don't know the answer, you search the internet for it.",
    tools=[{"type": "code_interpreter"},
           {
               "type": "function",
               "function": {
                      "name": "searchInternet",
                      "description": "Search the internet for information beyond your knowledge cut-off date",
                      "parameters": {
                          "type": "object",
                          "properties": {
                              "query": {
                                  "type": "string",
                                  "description": "The search query to be used to search the internet."
                              }
                          }
                      }
               }
            }],
    model="gpt-4-turbo"
)
```
