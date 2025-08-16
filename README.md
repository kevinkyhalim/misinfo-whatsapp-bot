## **🧭 PROJECT ROADMAP: Misinformation Detector with WhatsApp Integration (AWS)**

---

### **🚀 Phase 1: Build the MVP (End-to-End Working Flow)**

**🎯 Objective:**
Allow a user to send a **message or link** on WhatsApp → system extracts text (and article text if a link) → classifies it as True/False → replies on WhatsApp with a verdict and explanation.

**📅 Step 1: Set Up WhatsApp Messaging Interface**

* Create a **Twilio account** and activate **WhatsApp sandbox**.
* Set up webhook infrastructure:
  * Use **FastAPI** (Python).
  * Add route `/webhook` to receive POST messages from Twilio.
  * Handle both **plain text** and **URL** inputs (detect URLs with regex).
  * For URLs, fetch and extract main text using `trafilatura`.
  * Reply to messages using Twilio’s Python SDK.
* Test manually: user sends message or link → echo reply works.

**Outcome:**
You can send and receive text or link messages via WhatsApp using Twilio, and the app can extract text from URLs.

**New Files:**
* main -> FastAPI backend
* handlers -> function to handle the url or message
* utils -> recognizes a url
* test -> testing file

**Testing:**
Local testing steps:
1. Run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 
2. Run ngrok http 8000
3. Copy and paste the ngrok link + /webhook to twilio
4. Send a message in whatsapp.

**Step 1 Checklist**
* [✅] Twilio Sandbox joined and verified.
* [✅] FastAPI webhook implemented.
* [✅] URL detection + extraction working.
* [✅] Local test successful with ngrok.

---

**📅 Step 2: Implement Search & RAG with Gemini API & FAISS Library**

* Incorporate Gemini API to fact check your message (text &/ URL).
* Implement FAISS query to check for evidence in local document.
* Create logic to only use FAISS query when prompt includes certain keywords.
* Integrate this into webhook after URL/text extraction.

**Outcome:**
User sends message or link → system extracts claim text → gets verdict &/ reply (either with Gemini or with FAISS).

**New & Modified Files:**
* All .py file  under app/rag folder (build_faiss_index, faiss_store, private_matcher)
* gemini.py -> containes 3 functions (with url_check, verify_with_evidence, verify_with_search)
* handlers.py -> revamped the process_incoming_message_hybried to include the FAISS query

**Testing:**
1. Make sure that you update the .env -> GEMINI_API_KEY with your gemini API keyl
2. Populate the corpus.jsonl in the data folder with the private data.
3. run `python -m app.rag.build_faiss_index --input data/corpus.jsonl --out_dir data`.
4. revise the keywords under .env -> PRIVATE_DOMAIN_KEYWORDS.
5. Ask your query in whatsapp and ensure that a keyword in 3. exists in the query.

**Step 2 Checklist**
* [✅] Gemini Search tested for general claims.
* [✅] FAISS index loaded with private dataset (e.g., internal fact-check reports).
* [✅] Local test successful with ngrok.

---

**📅 Step 3: Deploy MVP to AWS**

*	Build Docker image locally, push to **ECR**.
*	Deploy FastAPI as **Lambda** using container image.
*	Configure **API Gateway → Lambda** for Twilio webhook.
*	Store secrets in **AWS Secrets Manager** (Gemini API key, dataset paths).
*	Set up **CloudWatch** logs for monitoring requests.
* Create **OpenSearch Serverless** collection for private dataset index.


**AWS Services:**
* API Gateway — webhook endpoint.
* Lambda (container) — FastAPI app.
* ECR — store Docker image.
* OpenSearch Serverless — private dataset vector index.
* Secrets Manager — Gemini API key.
* CloudWatch — logs & metrics.

**New & Modified Files:**

**Outcome:**
Your misinformation detector runs entirely on AWS, triggered by real WhatsApp messages and handling both text and URLs.

**Testing:**

**Step 3 Checklist**
* [ ] Docker Setup
  * [ ] Dockerfile + docker-compose.yml created.
  *	[ ] FAISS index built & mounted as volume.
  *	[ ] .env file loaded in Docker container (API keys, FAISS paths, keywords).
* [ ] End-to-end message → verdict pipeline working in Docker.
* [ ] Deployed on AWS and Twilio webhook updated.
  *	[ ] ECR repo created & container pushed.
  *	[ ] Lambda deployed from ECR container.
  *	[ ] API Gateway endpoint linked to Twilio webhook.
  *	[ ] Secrets Manager storing Gemini API key.
  *	[ ] OpenSearch Serverless populated with FAISS-exported dataset.
*	[ ] Test end-to-end claim verification in AWS.

---

**Phase 1 Checklist**
* [✅] Step 1
* [✅] Step 2
* [  ] Step 3

---


<!-- Maybe this should be deleted?
Phase 2.1 — Claim Decision Flow
•	Detect if claim belongs to private domain dataset.
o	If yes → RAG pipeline (OpenSearch + Gemini reasoning).
o	If no → Gemini Search mode (Google search-based fact-checking). -->

<!-- Maybe can add this to the AWS deployment? 
Phase 2.2 — RAG Pipeline (AWS Production)
AWS Workflow:
1.	Ingestion Lambda — pulls new curated/private data.
2.	Text Cleaning + Chunking Lambda — prepares structured text.
3.	Embedding Lambda — generates embeddings, stores in S3 + OpenSearch Serverless.
4.	Retrieval Lambda — queries OpenSearch with claim embeddings.
5.	Gemini Reasoning — final verdict with evidence.
Checklist:
•	 Ingestion Lambda deployed (with scheduler).
•	 Text preprocessing Lambda deployed.
•	 Embedding Lambda tested (S3 + OpenSearch updates).
•	 Retrieval Lambda integrated with FastAPI service.
•	 End-to-end private dataset RAG tested in AWS. -->
 
### **🧩 Phase 2: Hybrid Fact-Checking Production with Agentic AI**

**📅 Step 4: Agentic AI Layer Enhancements**
Agents to add intelligence & reliability:
•	Controller Agent: chooses between Gemini Search vs. RAG.
•	Source Validator Agent: filters unreliable domains from Gemini or OpenSearch results.
•	Timeline Builder Agent: generates chronological fact flow for evolving claims.
•	Cross-Source Consensus Agent: checks agreement across multiple trusted outlets before final verdict.

**📅 Step 5: Feedback & Continuous Learning**
•	WhatsApp feedback (👍/👎) captured in DynamoDB.
•	Feedback loop:
  o	RAG retrieval tuning.
  o	Prompt engineering improvements for Gemini.
  o	Logging to CloudWatch Dashboard for monitoring claim accuracy & latency.
•	Optional: retrain embeddings periodically with feedback data.
Checklist:
•	 WhatsApp feedback integrated.
•	 DynamoDB storing logs.
•	 CloudWatch Dashboard created for KPIs.
•	 Feedback-driven updates tested (retrieval & prompts).

### **🧠 Phase 3: Expansion to Telegram**

•	Replicate Twilio → WhatsApp integration logic for Telegram Bot API.
•	Deploy same FastAPI webhook endpoint with route for Telegram.
•	Add cross-channel orchestration: WhatsApp + Telegram requests go through the same claim pipeline.
•	Test multi-platform feedback logging to DynamoDB.
Checklist:
•	 Telegram Bot API credentials stored in Secrets Manager.
•	 FastAPI route added for Telegram.
•	 Docker container updated with Telegram dependencies.
•	 End-to-end test from Telegram → AWS → Gemini/RAG → reply.

### **🧲 Optional Stretch Goals**

| Feature              | Description                                                |
| -------------------- | ---------------------------------------------------------- |
| Image Fact-Checking  | OCR on screenshots + NLP pipeline.                         |
| Multilingual Support | Auto-translate inputs before analysis.                     |
| Bias Filter          | Add Perspective API or Detoxify for hate speech detection. |
| Chrome Extension     | Submit claims from web pages directly.                     |

---

### **🧰 Suggested Tech Stack**

| Layer              | Technology                              |
| ------------------ | --------------------------------------- |
| WhatsApp Interface | Twilio WhatsApp API                     |
| Backend            | Python (FastAPI)                        |
| Retrieval          | FAISS + Sentence-BERT                   |
| Agentic LLM        | OpenAI GPT-4o / Claude / AWS Bedrock    |
| Cloud Deployment   | AWS Lambda + API Gateway or ECS Fargate |
| Monitoring         | AWS CloudWatch, Sentry                  |
| Storage            | DynamoDB (logs)         |

---