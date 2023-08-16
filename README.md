# Query-SQL-Local-LLM
Query a SQL database using a local LLM.

pip install streamlit
pip install langchain-experimental
pip install langchain
pip install llama-cpp
pip install bitsandbytes-windows

The code is set up to work with an SQLite database, so you'll need to change the pg_uri format if you're working with another type.

Set paths to db (pg_uri =), model (model_path =)

I downloaded a model locally, so I used an absolute path in my model path. Your model type may require changing "llm = LlamaCpp(..." to another format. For example, you may need llm = OpenAI(... if you're using an OpenAI model (you would also need an API key entry in that case).

Depending on the size of your database and the complexity of your queries, you will need to set n_ctx accordingly for token size. It defaults to 512, which was not enough for my testing even on a smaller database.


