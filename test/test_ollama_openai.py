from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1/',

    # required but ignored
    api_key='ollama',
)

completion = client.completions.create(
    model="llama3.1",
    prompt="just say this is a test, nothing more.",
)

# print(completion)
text_output = completion.choices[0].text
print(text_output)