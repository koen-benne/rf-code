from gpt4all import GPT4All
model = GPT4All("wizardlm-13b-v1.2.Q4_0.gguf")

with model.chat_session():
    response1 = model.generate(prompt='hello', temp=0)
    response2 = model.generate(prompt='write me a short poem', temp=0)
    response3 = model.generate(prompt='what was it about?', temp=0)
    print(model.current_chat_session)
