import streamlit as st 
import pandas as pd
from sqlalchemy import create_engine
import re

# Setting up the MS-SQL SERVER CONNECTION
def create_connection(server, database):
    connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(connection_string)
    return engine

# Highlight SQL keywords
def highlight_sql_keywords(query):
    sql_keywords = ["SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "DROP", "ALTER"]
    for keyword in sql_keywords:
        query = re.sub(rf'\b{keyword}\b', f'<span class="sql-keyword">{keyword}</span>', query, flags=re.IGNORECASE)
    return query

# Streamlit application title
st.title("SQL Query App")

# Database Connection parameters
server = st.text_input('Server')
database = st.text_input('Database')

# Create database connection
if st.button('Connect to Database', key='connect'):
    try:
        st.session_state.conn = create_connection(server, database)
        st.success('Connected to database successfully!')
    except Exception as e:
        st.error(f'Error connecting to database: {e}')

# File Uploader
uploaded_file = st.file_uploader("Choose a File", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
        
    st.write('Uploaded Data')
    st.write(df)

    # Upload the dataframe to the database
    table_name = st.text_input('Table Name')
    if st.button('Upload to Database', key='upload'):
        if table_name:
            try:
                # Check if connection exists
                if 'conn' in st.session_state:
                    conn = st.session_state.conn
                    with conn.begin() as transaction:
                        df.to_sql(table_name, conn, if_exists='replace', index=False)
                        transaction.commit()
                    st.success(f'Table {table_name} created successfully!')
                else:
                    st.error('Please connect to the database first')
            except Exception as e:
                st.error(f'Error uploading table: {e}')

    # Button to calculate null, missing, and duplicated values
    if st.button('Calculate Null, Missing, Duplicated Values', key='calculate'):
        null_values = df.isnull().sum().sum()
        duplicated_values = df.duplicated().sum()
        st.write(f'Total Null Values: {null_values}')
        st.write(f'Total Duplicated Values: {duplicated_values}')

    # Button to remove null, missing, and duplicated values
    if st.button('Remove Null, Missing, Duplicated Values', key='remove'):
        df_cleaned = df.dropna().drop_duplicates()
        st.write('Cleaned Data')
        st.write(df_cleaned)
        
        # Update the cleaned dataframe in the database
        if table_name:
            try:
                if 'conn' in st.session_state:
                    conn = st.session_state.conn
                    with conn.begin() as transaction:
                        df_cleaned.to_sql(table_name, conn, if_exists='replace', index=False)
                        transaction.commit()
                    st.success(f'Table {table_name} updated with cleaned data successfully!')
                else:
                    st.error('Please connect to the database first')
            except Exception as e:
                st.error(f'Error updating table with cleaned data: {e}')

# SQL Query Input
query = st.text_area('Enter your SQL Query')

if st.button('Execute Query', key='execute'):
    if 'conn' in st.session_state:
        try:
            query_result = pd.read_sql_query(query, st.session_state.conn)
            st.write('Query Results')
            st.write(query_result)
        except Exception as e:
            st.error(f'Error executing query: {e}')
    else:
        st.error('Please connect to the database first')

# List Tables
if st.button('List Tables', key='list'):
    if 'conn' in st.session_state:
        try:
            query_result = pd.read_sql_query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'", st.session_state.conn)
            st.write('Tables in Database:')
            st.write(query_result)
        except Exception as e:
            st.error(f'Error listing tables: {e}')

# Display highlighted SQL query
if query:
    highlighted_query = highlight_sql_keywords(query)
    st.markdown(f"<pre>{highlighted_query}</pre>", unsafe_allow_html=True)

# Visualization
if 'conn' in st.session_state:
    tables_query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    tables = pd.read_sql_query(tables_query, st.session_state.conn)
    table_name = st.selectbox('Select Table', tables['TABLE_NAME'])

    col1, col2 = st.columns(2)
    with col1:
        x_col = st.text_input('X-axis Column')
    with col2:
        y_col = st.text_input('Y-axis Column')

    chart_type = st.selectbox('Select Chart Type', ['Bar Chart', 'Scatter Chart', 'Bubble Chart', 'Histogram'])
    num_rows = st.number_input('Number of Rows', min_value=1, value=100)

    if st.button('Generate Chart', key='chart'):
        if x_col and y_col and chart_type:
            if table_name:
                query = f"SELECT TOP {num_rows} {x_col}, {y_col} FROM {table_name}"
                data = pd.read_sql_query(query, st.session_state.conn)
                
                if chart_type == 'Bar Chart':
                    st.bar_chart(data.set_index(x_col))
                elif chart_type == 'Scatter Chart':
                    st.write(st.plotly_chart(data.plot.scatter(x=x_col, y=y_col)))
                elif chart_type == 'Bubble Chart':
                    st.write(st.plotly_chart(data.plot.scatter(x=x_col, y=y_col, s=data[y_col]*100)))
                elif chart_type == 'Histogram':
                    st.write(st.plotly_chart(data[x_col].plot.hist()))
            else:
                st.error('Please select a table first')
        else:
            st.error('Please input both column names and select a chart type')
else:
    st.error('Please connect to the database first')
