from config import OPENAI_API_KEY
import openai

openai.api_key = OPENAI_API_KEY
llm_client = openai.OpenAI()


def request_to_llm(request:str, client=llm_client)->str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system","content": "You are a travel agency."},
            {"role":"user","content":request}
        ],
        max_tokens=1200,
        temperature=0.7,
    )
    return response.choices[0].message.content