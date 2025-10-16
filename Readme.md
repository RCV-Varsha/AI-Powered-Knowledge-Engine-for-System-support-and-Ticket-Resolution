# AI-Powered Knowledge Engine for System Support and Ticket Resolution

This project implements an intelligent system designed to automate and enhance the efficiency of customer support workflows. By integrating Retrieval-Augmented Generation (RAG) and Machine Learning models, the system can automatically categorize support tickets and provide suggested knowledge base articles and resolutions, significantly reducing resolution time.

## ✨ Features

* **Ticket Categorization:** Uses a Logistic Regression model trained on TF-IDF features to classify incoming tickets into predefined categories.
* **Intelligent Resolution Suggestion (RAG):** Implements a RAG pipeline (using FAISS for vector storage) to search the knowledge base (`kb/` directory) and suggest the most relevant articles and solutions.
* **Email & Slack Notifications:** Automatically sends notifications for new tickets or suggested resolutions via a configurable notification system (Gmail and Slack integration available).
* **Streamlit Dashboard:** A web-based dashboard for monitoring ticket activity and usage logs of suggested articles.
* **Modular Architecture:** Components for data processing, model training, RAG pipeline, and notification handlers are cleanly separated in the `src/` directory.

## ⚙️ Setup and Installation

### Prerequisites

* Python 3.8+
* A Google Gemini API Key or an equivalent LLM API key.
* Credentials for Email (SMTP) and/or Slack API if using the notification features.

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/rcv-varsha/ai-powered-knowledge-engine-for-system-support-and-ticket-resolution.git](https://github.com/rcv-varsha/ai-powered-knowledge-engine-for-system-support-and-ticket-resolution.git)
    cd ai-powered-knowledge-engine-for-system-support-and-ticket-resolution
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration:**
    Create a `.env` file in the root directory and add your API keys and configuration settings. Refer to `src/setup_env.py` for required variables.

    ```bash
    # Example .env content
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    # Other configuration variables...
    ```

5.  **Build the Knowledge Base Vector Store:**
    The RAG system requires the knowledge base articles in the `kb/` folder to be processed.
    ```bash
    python src/kb_processor.py
    ```

## 🚀 Running the Application

### Launch the Streamlit Dashboard

To view the monitoring dashboard and application insights:
```bash
streamlit run src/dashboard.py
