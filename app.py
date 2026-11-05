
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from database import (
    create_database,
    get_database_schema,
    get_table_counts,
    execute_read_query,
)
from ai_engine import generate_sql


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="QueryMind AI",
    page_icon="🧠",
    layout="wide",
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

if "sql_editor" not in st.session_state:
    st.session_state.sql_editor = ""

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "last_result_df" not in st.session_state:
    st.session_state.last_result_df = None

if "last_error" not in st.session_state:
    st.session_state.last_error = ""

if "success_message" not in st.session_state:
    st.session_state.success_message = ""


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

try:
    create_database()
    database_ready = True
    database_error = ""
except Exception as error:
    database_ready = False
    database_error = str(error)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def is_mutation_request(question):
    """
    Detect requests that may change database data.
    These requests are declined instead of being executed.
    """

    question = question.strip().lower()

    patterns = [
        r"^\s*(delete|drop|insert|update|alter|truncate|remove)\b",
        r"\b(delete|remove|drop)\s+(all\s+)?(the\s+)?(records|rows|data|customers|orders|products|table)\b",
        r"\b(insert|add)\s+(a\s+)?(new\s+)?(record|row|customer|order|product)\b",
        r"\b(update|change|modify)\s+(the\s+)?(record|row|data|customer|order|product)\b",
        r"\b(clear|empty|erase)\s+(the\s+)?(table|database|records|data)\b",
    ]

    return any(re.search(pattern, question) for pattern in patterns)


def restore_history(index):
    """Restore an earlier query and its results."""

    item = st.session_state.query_history[index]

    st.session_state.question_input = item["question"]
    st.session_state.sql_editor = item["sql"]
    st.session_state.last_result_df = item["results"].copy()
    st.session_state.last_error = ""
    st.session_state.success_message = (
        f"Loaded previous query from {item['time']}."
    )


def show_database_schema():
    """Display database schema information."""

    try:
        schema = get_database_schema()
        st.code(str(schema), language="sql")
    except Exception as error:
        st.error(f"Could not load database schema: {error}")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🧠 QueryMind AI")

st.write(
    "Ask questions about your database in plain English. "
    "AI converts your question into SQL and displays the results."
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("📊 Database")

    if database_ready:
        st.success("Database connected")
    else:
        st.error("Database connection failed")
        st.error(database_error)

    st.subheader("Table Information")

    if database_ready:
        try:
            table_counts = get_table_counts()

            if isinstance(table_counts, dict):
                for table_name, count in table_counts.items():
                    st.write(f"**{table_name}**: {count} rows")
            else:
                st.write(table_counts)

        except Exception as error:
            st.warning(f"Could not load table counts: {error}")

    st.divider()

    st.subheader("🗂️ Schema Explorer")

    with st.expander("View database schema"):
        if database_ready:
            show_database_schema()
        else:
            st.warning("Database is not available.")

    st.divider()

    st.subheader("🕘 Query History")

    if st.session_state.query_history:

        for index, item in enumerate(
            st.session_state.query_history
        ):
            button_label = (
                f"{item['time']} - "
                f"{item['question'][:30]}"
            )

            st.button(
                button_label,
                key=f"history_{index}",
                use_container_width=True,
                on_click=restore_history,
                args=(index,),
            )

        if st.button(
            "Clear History",
            use_container_width=True,
        ):
            st.session_state.query_history = []
            st.rerun()

    else:
        st.caption("Your previous queries will appear here.")


# --------------------------------------------------
# MAIN QUESTION INPUT
# --------------------------------------------------

st.subheader("💬 Ask Your Database")

question = st.text_area(
    "Enter your question in plain English:",
    key="question_input",
    height=100,
    placeholder=(
        "Example: Show the top 5 customers "
        "who placed the most orders."
    ),
)

generate_button, clear_button = st.columns([1, 1])

with generate_button:
    generate_clicked = st.button(
        "✨ Generate SQL",
        type="primary",
        use_container_width=True,
        disabled=not database_ready,
    )

with clear_button:
    clear_clicked = st.button(
        "Clear",
        use_container_width=True,
    )


# --------------------------------------------------
# CLEAR INPUT
# --------------------------------------------------

if clear_clicked:
    st.session_state.question_input = ""
    st.session_state.sql_editor = ""
    st.session_state.last_result_df = None
    st.session_state.last_error = ""
    st.session_state.success_message = ""
    st.rerun()


# --------------------------------------------------
# GENERATE SQL USING GEMINI
# --------------------------------------------------

if generate_clicked:

    st.session_state.last_error = ""
    st.session_state.success_message = ""
    st.session_state.last_result_df = None

    if not question or len(question.strip()) < 3:

        st.session_state.last_error = (
            "Please enter a meaningful question."
        )

    elif is_mutation_request(question):

        st.session_state.last_error = (
            "This request may modify database data. "
            "For safety, QueryMind AI only supports "
            "read-only questions such as SELECT queries."
        )

    else:

        try:
            with st.spinner("Generating SQL with AI..."):

                schema = get_database_schema()

                generated_sql = generate_sql(
                    question.strip(),
                    schema,
                )

                st.session_state.sql_editor = generated_sql
                st.session_state.success_message = (
                    "SQL query generated successfully. "
                    "Review it before execution."
                )

        except Exception as error:

            st.session_state.last_error = str(error)


# --------------------------------------------------
# DISPLAY GENERATED SQL
# --------------------------------------------------

if st.session_state.sql_editor:

    st.divider()

    st.subheader("📝 Generated SQL")

    st.caption(
        "Review the SQL below. You can edit it before "
        "executing the query."
    )

    sql = st.text_area(
        "SQL Editor",
        key="sql_editor",
        height=180,
    )

    execute_clicked = st.button(
        "▶️ Execute SQL",
        type="primary",
        use_container_width=True,
        disabled=not database_ready,
    )

else:
    execute_clicked = False


# --------------------------------------------------
# EXECUTE SQL QUERY
# --------------------------------------------------

if execute_clicked:

    st.session_state.last_error = ""
    st.session_state.success_message = ""

    sql_to_execute = st.session_state.sql_editor.strip()

    if not sql_to_execute:

        st.session_state.last_error = (
            "SQL query cannot be empty."
        )

    else:

        try:
            with st.spinner("Executing SQL query..."):

                result_df = execute_read_query(
                    sql_to_execute
                )

                st.session_state.last_result_df = result_df.copy()

                history_item = {
                    "question": st.session_state.question_input,
                    "sql": sql_to_execute,
                    "results": result_df.copy(),
                    "time": datetime.now().strftime("%H:%M:%S"),
                }

                st.session_state.query_history.insert(
                    0,
                    history_item,
                )

                # Keep only the latest 20 queries.
                st.session_state.query_history = (
                    st.session_state.query_history[:20]
                )

                st.session_state.success_message = (
                    "Query executed successfully."
                )

        except Exception as error:

            st.session_state.last_error = str(error)
            st.session_state.last_result_df = None


# --------------------------------------------------
# DISPLAY MESSAGES
# --------------------------------------------------

if st.session_state.success_message:
    st.success(st.session_state.success_message)

if st.session_state.last_error:
    st.error(st.session_state.last_error)


# --------------------------------------------------
# DISPLAY QUERY RESULTS
# --------------------------------------------------

if st.session_state.last_result_df is not None:

    result_df = st.session_state.last_result_df

    st.divider()

    st.subheader("📋 Query Results")

    total_rows = len(result_df)
    total_columns = len(result_df.columns)

    metric1, metric2 = st.columns(2)

    metric1.metric(
        "Rows Returned",
        total_rows,
    )

    metric2.metric(
        "Columns",
        total_columns,
    )

    if result_df.empty:

        st.info(
            "Query executed successfully, but no matching "
            "records were found."
        )

    else:

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True,
            height=350,
        )

        csv_data = result_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv_data,
            file_name="query_results.csv",
            mime="text/csv",
            use_container_width=True,
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "QueryMind AI | Natural Language to SQL Engine | "
    "Built with Python, Streamlit, SQLite and Gemini AI"
)