# 📚 Agentic AI Study Assistant

A beginner-friendly **Agentic AI Study Assistant** built using **LangChain** and the **Groq LLM API**. The assistant can answer study-related questions by deciding when to use external tools such as a calculator or a file reader.

---
## 🚀 Live Demo

👉 **[Launch AI Study Assistant](https://agentic-ai-study-assistant-nla5bufhtvx6p6vpb5gxfr.streamlit.app/)**

## 🚀 Features

- 🤖 AI Agent powered by LangChain
- 🧠 Groq LLM integration
- 🧮 Calculator Tool
  - Solves arithmetic expressions safely.
- 📄 File Reader Tool
  - Reads `.txt`, `.md`, and `.json` files.
  - Restricted to the `data/` directory for security.
- 📝 Logging
  - Stores user queries, tool usage, results, and responses.
- 🔒 Safe tool execution
- 📂 Beginner-friendly project structure

---

# 🏗️ Project Architecture

```
                User
                  │
                  ▼
             app.py
                  │
                  ▼
            LangChain Agent
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 Calculator Tool      File Reader Tool
        │                   │
        ▼                   ▼
 Mathematical        Read study notes
 Calculations        from data folder
        │                   │
        └─────────┬─────────┘
                  ▼
              Groq LLM
                  │
                  ▼
            Final Response
```

---

# 📁 Project Structure

```
agentic_ai_study_agent/
│
├── main.py
├── agent.py
├── config.py
│
├── tools/
│   ├── calculator.py
│   └── file_reader.py
│
├── data/
│   └── notes.txt
│
├── logs/
│   └── agent.log
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# ⚙️ Requirements

- Python 3.10+
- Groq API Key
- Internet Connection

---

# 📦 Installation

## Clone Repository

```bash
git clone <repository-url>
cd agentic_ai_study_agent
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
```

---

## Activate Virtual Environment

PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt

```cmd
.venv\Scripts\activate.bat
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Configure API Key

Copy

```
.env.example
```

Rename it to

```
.env
```

Add your Groq API key.

Example

```
GROQ_API_KEY=your_api_key_here
```

---

# ▶️ Run the Application

```bash
python app.py
```

---

# 💬 Example Questions

```
Calculate (250 * 18) / 6
```

```
Read notes.txt and summarize it
```

```
What topics are covered in notes.txt?
```

```
Explain Machine Learning from notes.txt
```

---

# 🧰 Tools

## Calculator Tool

- Addition
- Subtraction
- Multiplication
- Division
- Parentheses

Example

```
125 * 45
```

---

## File Reader Tool

Supports

- txt
- md
- json

Restricted to

```
data/
```

for security.

---

# 📝 Logs

Every interaction is saved in

```
logs/agent.log
```

including

- User question
- Tool selected
- Tool output
- Final answer

---

# 🔒 Security

The File Reader Tool only reads files inside the

```
data/
```

folder.

This prevents unauthorized file access and demonstrates secure Agentic AI design.

---

# 🛠️ Technologies Used

- Python
- LangChain
- Groq LLM
- Python-dotenv
- Logging
- Tool Calling

---

# 📈 Future Improvements

- PDF Reader
- Memory
- RAG
- Web Search
- Quiz Generator
- Voice Assistant
- Streamlit Interface
- FastAPI Backend

---

# 👨‍💻 Author

Hemnath KK

B.Tech Artificial Intelligence and Data Science


| Criteria | Our Project (Groq + Llama 3.3) | Typical AI Chatbot |
|----------|-------------------------------|--------------------|
| LLM | Llama-3.3-70B | Varies |
| Tool Calling | ✅ Calculator & File Reader | ❌ Often not integrated |
| Local Study Notes | ✅ Supported | ❌ Usually not |
| Deployment | Streamlit Cloud | Depends |
| Cost for Students | ✅ Free Tier Available | Often API costs apply |
| Development Language | Python Only | Multiple languages may be required |
| Extensibility | High (new tools can be added) | Varies |
