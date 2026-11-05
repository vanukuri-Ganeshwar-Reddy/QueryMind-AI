# 🧠 QueryMind AI – Natural Language to SQL Query Generator

QueryMind AI is an AI-powered application that converts natural language questions into SQL queries using Google's Gemini AI.

It allows users to interact with an SQLite database using simple English questions without manually writing SQL queries.

The application generates SQL queries, allows users to review and edit them, executes read-only queries, and displays the results in an interactive interface.

## 🚀 Features

- **Natural Language to SQL:** Convert English questions into SQL queries using Gemini AI.
- **AI-Powered Query Generation:** Uses Google's Gemini models to generate SQLite-compatible SQL.
- **Interactive SQL Editor:** Review and modify generated SQL queries before execution.
- **Read-Only Query Execution:** Supports SELECT queries and prevents database modifications.
- **SQLite Database Integration:** Works with customers, products, and orders tables.
- **Database Schema Explorer:** View database tables, columns, and relationships.
- **Query History:** Access previously executed queries.
- **Data Visualization:** Display query results in an interactive table.
- **CSV Export:** Download query results as CSV files.
- **Error Handling:** Provides meaningful error messages for invalid queries and AI failures.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | User interface |
| Google Gemini AI | SQL query generation |
| SQLite | Database management |
| Pandas | Data processing |
| SQLGlot | SQL parsing and validation |

## 📁 Project Structure

```text
QueryMind-AI/
│
├── app.py                  # Main Streamlit application
├── ai_engine.py            # Gemini AI integration
├── database.py             # SQLite database operations
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── .gitignore              # Files excluded from GitHub
│
├── .streamlit/
│   └── secrets.toml        # Local API key configuration
│
└── data/
    └── querymind.db        # Generated SQLite database
```

**Note:** The `secrets.toml` file and generated database are excluded from the GitHub repository.

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/QueryMind-AI.git
```

### 2. Navigate to the Project Directory

```bash
cd QueryMind-AI
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Gemini API Key

Create a folder named `.streamlit`:

```powershell
New-Item -ItemType Directory -Force .streamlit
```

Create a file named `secrets.toml` inside the `.streamlit` folder.

Add your Gemini API key:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Replace `YOUR_GEMINI_API_KEY` with your actual Google Gemini API key.

Get your API key from:

https://aistudio.google.com/apikey

**Important:** Never upload your API key or `secrets.toml` file to GitHub.

## ▶️ Run the Application

After completing the installation and API configuration, execute:

```bash
streamlit run app.py
```

The application will open in your browser.

If it does not open automatically, visit:

```text
http://localhost:8501
```

## 🗄️ Database Information

QueryMind AI uses an SQLite database with three main tables:

### Customers
Stores customer information such as:
- Customer ID
- Name
- Email
- City
- Signup Date

### Products
Stores product information such as:
- Product ID
- Product Name
- Category
- Price
- Stock

### Orders
Stores order information such as:
- Order ID
- Customer ID
- Product ID
- Quantity
- Order Total
- Order Date
- Order Status

The database and sample records are initialized automatically when the application runs.

## 💡 Example Questions

Users can ask questions in simple English.

| Natural Language Question | Generated SQL Concept |
|---|---|
| Show all customers | SELECT from customers |
| Find the most expensive product | ORDER BY price DESC |
| Show total number of orders | COUNT(*) |
| Find customers from Hyderabad | WHERE city = 'Hyderabad' |
| Show total sales by product | GROUP BY product |
| Find pending orders | WHERE status = 'Pending' |

## 🔐 Security Features

- API keys are stored using Streamlit secrets.
- Sensitive configuration files are excluded through `.gitignore`.
- Only read-only SQL queries are permitted.
- SQL statements are validated before execution.
- SQLite query-only mode prevents database modifications.
- Query execution is subject to an execution limit.

## 🎯 Project Objective

The main objective of QueryMind AI is to simplify database interaction by allowing users to retrieve information using natural language instead of manually writing SQL queries.

It helps make database querying more accessible to users with limited SQL knowledge.

## 👨‍💻 Author

**Your Name**

GitHub: https://github.com/YOUR_USERNAME

## 📜 License

This project is available for educational and learning purposes.
