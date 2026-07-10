# Real Estate Document Intelligence — Production RAG Pipeline

A production-grade RAG (Retrieval-Augmented Generation) system for querying Indian real estate legal documents (Builder Buyer Agreements, RERA filings, Sale Deeds) using natural language.



## RAGAS Evaluation Results

| Metric | Score |
|---|---|
| Faithfulness | 1.0 |
| Context Recall | 1.0 |
| Context Precision | 1.0 |


## Run Locally

```bash
# Install Ollama and pull models
ollama pull llama3.2
ollama pull nomic-embed-text

# Setup
git clone https://github.com/YOUR_USERNAME/real-estate-rag
cd real-estate-rag
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run API
python3 main.py

# API docs at http://localhost:8000/docs
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| /health | GET | Service health check |
| /upload | POST | Upload and ingest PDF |
| /query | POST | Natural language query |

## Example

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the penalty if builder delays possession?"}'
```

Response:
```json
{
  "answer": "Rs. 10/- per sq. ft. per month as per Section 8.10",
  "sources": [{"page": 10, "content": "..."}]
}
```
