# Contant
Contant - A GPT4 console Assistant

A minimalistic sample console app of a GPT4 assistant, equipped with a function to search the internet (via SERPAPI).
The code assumes you know how to create an assistant and putting functions on it.
I wrote this because I was learning about function calling on assistant api, so it's just a rough sample.

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
