import openai

openai.api_key = "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"  

def get_gpt_reply(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT ERROR] {e}")
        return "לא הצלחתי להבין. אפשר לנסות שוב?"
