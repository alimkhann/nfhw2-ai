import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional

load_dotenv()
client = OpenAI()

VECTOR_STORE_ID = "vs_6840341401ec8191877500a6f932cede"

class Note(BaseModel):
    id: int = Field(..., ge=1, le=10)
    heading: str = Field(..., example="Mean Value Theorem")
    summary: str = Field(..., max_length=150)
    page_ref: Optional[int] = Field(None)

system = (
    "You are a study summarizer. "
    "Return exactly 10 unique notes that will help prepare for the exam. "
    "Respond ONLY with valid JSON matching this format:\n"
    '{"notes": [{"id": 1, "heading": "Mean Value Theorem", "summary": "...", "page_ref": 5}, ...]}'
)

response = client.responses.create(
    model="gpt-4o",
    instructions=system,
    input="Extract 10 concise exam notes from the attached calculus PDF.",
    tools=[{
        "type": "file_search",
        "vector_store_ids": [VECTOR_STORE_ID]
    }]
)

# Remove ```json ... ``` if present
cleaned = re.sub(r"^```json|```$", "", response.output_text.strip(), flags=re.IGNORECASE).strip()

try:
    cleaned = re.sub(r"^```json|```$", "", response.output_text.strip(), flags=re.IGNORECASE).strip()
    data = json.loads(cleaned)
    notes = [Note(**{**item, "summary": item["summary"][:150]}) for item in data["notes"]]
except Exception as e:
    print("❌ Failed to parse cleaned JSON or match schema:", e)
    print("🔎 Raw content was:\n", response.output_text)
    exit(1)

with open("exam_notes.json", "w") as f:
    json.dump([n.dict() for n in notes], f, indent=2)

print("\n✅ Generated 10 exam notes:\n")
for note in notes:
    print(f"{note.id}. {note.heading} — {note.summary} (page {note.page_ref})")
