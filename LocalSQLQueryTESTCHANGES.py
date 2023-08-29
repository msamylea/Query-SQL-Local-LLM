import streamlit as st
import html
from typing import Dict
from langchain_experimental.sql import SQLDatabaseChain
from langchain import SQLDatabase
from langchain.llms import LlamaCpp

def initialize_app():
    st.set_page_config(page_title="SQL Query Helper", page_icon=":cat:", layout="centered", initial_sidebar_state="auto")
    st.markdown(f"""
                <style>
                .stApp {{background-image: url(""); 
                         background-attachment: fixed;
                         background-size: cover}}
             </style>
             """, unsafe_allow_html=True)
    st.title("SQL Query Helper")

def configure_llm(model_path):
    return LlamaCpp(
        model_path=model_path,
        n_gpu_layers=2,
        n_ctx=2048,
        temperature=0
    )

def _parse_example(result: Dict) -> Dict:
    """
    Parses the result dictionary to create a new example dictionary.

    Args:
        result (Dict): The result dictionary to parse.

    Returns:
        Dict: The parsed example dictionary.
    """
    # Define key names
    sql_cmd_key = "sql_cmd"
    sql_result_key = "sql_result"
    table_info_key = "table_info"
    input_key = "input"
    final_answer_key = "answer"

    # Create the example dictionary with the input value
    _example = {
        input_key: result.get("query"),
    }

    # Iterate over the intermediate steps
    steps = result.get("intermediate_steps")
    answer_key = sql_cmd_key  # the first one
    for step in steps:
        if isinstance(step, dict):
            # Grab the table info from input dicts in the intermediate steps once
            if table_info_key not in _example:
                _example[table_info_key] = step.get(table_info_key)

            # Check step type and set the answer_key accordingly
            if input_key in step:
                if step[input_key].endswith("SQLQuery:"):
                    answer_key = sql_cmd_key  # this is the SQL generation input
                if step[input_key].endswith("Answer:"):
                    answer_key = final_answer_key  # this is the final answer input
            elif sql_cmd_key in step:
                _example[sql_cmd_key] = step[sql_cmd_key]
                answer_key = sql_result_key  # this is SQL execution input
        elif isinstance(step, str):
            # The preceding element should have set the answer_key
            _example[answer_key] = step
    
    return _example

example: any

def process_query(QUERY, db_chain, answer_placeholder):
    with st.spinner('Processing...'):
        try:
            result = db_chain(QUERY)
            st.success("Query succeeded")
            example = _parse_example(result)
            escaped_answer = html.escape(example.get('answer'))  # Escape special characters
            answer_placeholder.markdown(f'## Response\n{escaped_answer}')  # Display the answer
            st.code(example.get('sql_cmd'), language='sql')  # Display the SQL command
        except Exception as exc:
            st.error("Query failed")
            result = {
                "query": QUERY,
                "intermediate_steps": exc.intermediate_steps
            }
            example = _parse_example(result)
    return example
# Main execution block
# Main execution block
initialize_app()

pg_uri = "sqlite:///D:/LlamaSQL/ProfMov.db"
db = SQLDatabase.from_uri(pg_uri)

model_path = r'D:/models/llama-2-7b-chat.ggmlv3.q8_0.bin'
llm = configure_llm(model_path)

db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, return_intermediate_steps=True, use_query_checker=True)

with st.form(key='my_form'):
    QUERY = st.text_input("How would you like to search the SQL database:")
    submit_button = st.form_submit_button(label='Submit')

# Create a placeholder for the answer
answer_placeholder = st.empty()

# When the user presses Enter or clicks the submit button, the form is submitted and this code is run
if submit_button:
    example = process_query(QUERY, db_chain, answer_placeholder)
    st.write(example)