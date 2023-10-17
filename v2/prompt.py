import streamlit as st

QUALIFIED_TABLE_NAMES = [
    "RETAILDATA.BIGSUPPLYCO.CUSTOMERS",
    "RETAILDATA.BIGSUPPLYCO.CATEGORIES",
"RETAILDATA.BIGSUPPLYCO.PRODUCTS",
"RETAILDATA.BIGSUPPLYCO.DEPARTMENTS"]

TABLE_DESCRIPTIONS = {
    "RETAILDATA.BIGSUPPLYCO.CUSTOMERS": """
        This table has customer data for people who ordered from Big Supply
        """,
    "RETAILDATA.BIGSUPPLYCO.CATEGORIES": """
        This table has information about different categories at Big Supply
        """,
    "RETAILDATA.BIGSUPPLYCO.PRODUCTS": """
        This table has information about different products at Big Supply
        """,
    "RETAILDATA.BIGSUPPLYCO.DEPARTMENTS": """
        This table has information about different DEPARTMENTS at Big Supply
        """
}
# This query is optional if running Frosty on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Frosty what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
#METADATA_QUERY = "SELECT VARIABLE_NAME, DEFINITION FROM FROSTY_SAMPLE.CYBERSYN_FINANCIAL.FINANCIAL_ENTITY_ATTRIBUTES_LIMITED;"

GEN_SQL = """
You will be acting as an AI Snowflake SQL Expert named Chatbot.
Your goal is to give correct, executable sql query to users.
You will be replying to users who will be confused if you don't respond in the character of Chatbot.
You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.
The user will ask questions, for each question you should respond and include a sql query based on the question and the table. 

{context}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST MUST wrap the generated sql code within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single snowflake sql code, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names
6. DO NOT put numerical at the very front of sql variable.
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with ``` sql code markdown in this format e.g:
```sql
(select 1) union (select 2)
```

For each question from the user, make sure to include a query in your response.

Now to get started, please briefly introduce yourself, describe the table at a high level, and share the available metrics in 2-3 sentences.
Then provide 3 example questions using bullet points.
"""

@st.cache_data(show_spinner=False)
def get_table_context(table_name: str, table_description: str):
    table = table_name.split(".")
    conn = st.experimental_connection("snowpark")
    columns = conn.query(f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """,
    )
    columns = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns}\n\n</columns>
    """
    return context

# def get_system_prompt():
#     table_context = ""
#     for table_name in QUALIFIED_TABLE_NAMES:
#         table_context = table_context + (get_table_context(
#             table_name=table_name,
#             table_description=TABLE_DESCRIPTIONS.get(table_name, "")))
#     return GEN_SQL.format(context=table_context)

def get_system_prompt():
    system_intro = "Hello there! I am Chatbot, an AI Snowflake SQL Expert. I specialize in helping you with queries related to the following tables:\n\n"

    table_info = ""
    for table_name, table_description in TABLE_DESCRIPTIONS.items():
        table_info += f"- Table: {table_name}\n  Description: {table_description}\n\n"

    example_questions = "Here are three example questions you could ask me:\n\n" \
                        "1. What are the email addresses of customers from California?\n" \
                        "2. How many categories are there in Big Supply Co's inventory?\n" \
                        "3. What Products are available at Big Supply Co?.\n\n" \
                        "Feel free to ask any questions related to these tables!\n"

    return system_intro + table_info + example_questions

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Chatbot")
    st.markdown(get_system_prompt())
