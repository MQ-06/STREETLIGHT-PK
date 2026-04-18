import requests

def ask_llm(report):
    prompt = f"""
You are a civic complaint AI assistant.

Report:
Title: {report.title}
Description: {report.description}
Score: {report.combined_score}
Status: {report.status}

Give a short admin decision note.
"""

    # (Gemini API placeholder)
    response = {
        "note": "Escalated due to prolonged IN_PROGRESS state and medium confidence."
    }

    return response["note"]