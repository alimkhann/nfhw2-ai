from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# Upload file and create a vector store
pdf_path = "data/calculus_basics.pdf"
print("📤 Uploading PDF:", pdf_path)
file = client.files.create(file=open(pdf_path, "rb"), purpose="assistants")

print("📦 Creating vector store...")
vector_store = client.vector_stores.create(name="Study Vector Store")
client.vector_stores.files.create_and_poll(vector_store_id=vector_store.id, file_id=file.id)

print("✅ File added to vector store:", vector_store.id)

print("\n🎓 Ask a study question (type 'exit' to quit):\n")

while True:
    question = input("❓ Question: ").strip()
    if question.lower() in {"exit", "quit"}:
        print("👋 Goodbye!")
        break

    # Create a response using the Responses API
    response = client.responses.create(
        model="gpt-4o",
        input=question,
        instructions="You are a helpful tutor. Use the attached PDF to answer clearly and cite when possible.",
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store.id]
        }]
    )

    print("\n📘 Answer:\n", response.output_text, "\n")
