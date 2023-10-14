import streamlit as st
import mysql.connector

# MySQL connection configuration
mysql_config = {
    'user': 'root',
    'password': 'Tina3099*',
    'host': '127.0.0.1',
    'database': 'RetailData'  # Replace with your actual schema/database name
}

# List of tables with their descriptions
TABLES = [
    {
        "name": "customers",
        "description": "customer data"
    },
    {
        "name": "categories",
        "description": "category data"
    },
    # Add more tables as needed in a similar format
]

# Function to get column names for a given table
def get_columns_for_table(table_name, connection):
    cursor = connection.cursor()
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = [column[0] for column in cursor.fetchall()]
    cursor.close()
    return columns

# Modify get_table_context to handle multiple tables and fetch column names
@st.cache_data(show_spinner=False)
def get_table_context(tables, connection):
    context = ""
    for table_info in tables:
        table_name = table_info['name']
        table_description = table_info['description']
        # Fetch column information for each table
        columns = get_columns_for_table(table_name, connection)
        columns_info = "\n".join([f"- **{col}**: Data Type" for col in columns])
        context += f"""
        \n\nHere is the table name <tableName> {table_name} </tableName>
        \n<tableDescription>{table_description}</tableDescription>
        \n\nHere are the columns of the {table_name}
        \n<columns>\n\n{columns_info}\n\n</columns>"""
    return context

# Modify get_system_prompt to handle multiple tables
def get_system_prompt(tables, connection):
    table_context = get_table_context(tables, connection)
    return GEN_SQL.format(context=table_context)

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Frosty")

    # Establish MySQL connection
    try:
        connection = mysql.connector.connect(**mysql_config)
        st.markdown("MySQL connection successful!")
        st.markdown(get_system_prompt(TABLES, connection))
        connection.close()
    except mysql.connector.Error as err:
        st.error(f"Error: Unable to connect to MySQL - {err}")
