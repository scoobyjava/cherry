import openai


def summarize_with_personality(update_text: str) -> str:
    """
    Rephrase the user's update with slight humor and big-picture commentary using GPT-4.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Cherry, a witty and insightful assistant who adds humor and big-picture commentary."},
                {"role": "user", "content": f"Please summarize the following update with personality: {update_text}"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {e}"
