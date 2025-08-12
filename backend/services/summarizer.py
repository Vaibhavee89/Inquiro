import os
import requests

# Load your GPT-5 API key from environment variables
GPT_API_KEY = os.getenv("OPENAI_API_KEY")

API_URL = "https://api.openai.com/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GPT_API_KEY}",
    "Content-Type": "application/json"
}

def summarize_paper(content: str, max_words: int = 200) -> str:
    """
    Summarize the given research paper content using GPT-5.

    Args:
        content (str): The text content of the research paper.
        max_words (int): Maximum word length for the summary.

    Returns:
        str: Summary of the paper.
    """
    if not GPT_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY not found in environment variables.")

    prompt = (
        f"Summarize the following research paper in clear bullet points, "
        f"highlighting the main contributions, methodology, and results. Limit to {max_words} words.\n\n"
        f"Paper Content:\n{content}"
    )

    payload = {
        "model": "gpt-5",
        "messages": [
            {"role": "system", "content": "You are an expert research paper summarizer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        raise RuntimeError(f"OpenAI API Error {response.status_code}: {response.text}")
    
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

def summarize_multiple(papers: list, max_words: int = 200) -> dict:
    """
    Summarize multiple research papers.

    Args:
        papers (list): List of paper texts.
        max_words (int): Maximum word length per summary.

    Returns:
        dict: {index: summary} mapping.
    """
    summaries = {}
    for idx, paper_content in enumerate(papers):
        try:
            summaries[idx] = summarize_paper(paper_content, max_words)
        except Exception as e:
            summaries[idx] = f"Error summarizing paper {idx}: {e}"
    return summaries

if __name__ == "__main__":
    # Example usage
    example_text = """Deep learning has revolutionized computer vision in recent years..."""
    print(summarize_paper(example_text))