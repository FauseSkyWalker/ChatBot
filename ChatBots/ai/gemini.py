import os
from langchain_experimental.sql import SQLDatabaseChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities.sql_database import SQLDatabase

if "GOOGLE_API_KEY" not in os.environ:
    raise Exception('Please set the GOOGLE_API_KEY env variable')

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

# Construct the URI for PostgreSQL
db_uri = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}"
db = SQLDatabase.from_uri(db_uri)

llm = ChatGoogleGenerativeAI(model="gemini-pro")
db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True)

QUERY = """
Given an input question, first create a syntactically correct postgresql query
(without surrounding it in this quotes ``` or ```sql to specify that it is a
SQL query) to run, then look at the results of the query and return the answer.
Unless the user specifies in his question a specific number of examples he
wishes to obtain, always limit your query to at most 10 results. You can order
the results by a relevant column to return the most interesting examples in the
database.

Your answer need to be friendly and cheerful, always ask the user if they wants
to know anything else and your answer MUST contain relevant information for the
user, where possible tell them more about what are they asking for not just a
number or a word, e.g, if they asks for quantity of something Not only tell
them the exact amount but also more information about that product.

Never query for all the columns from a specific table, only ask for a the few
relevant columns given the question.

Pay attention to use only the column names that you can see in the schema
description. Be careful to not query for columns that do not exist. Also,
pay attention to which column is in which table.

Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

The SQL query must be outputted plainly, remember do not surround it in quotes
or anything else to specify that is a code block, it don't need it'. Start
the postgresSQL query immediately, like "SELECT ..." and don't do something
like ```sql

Question: {question}
"""


def get_response(prompt):
    try:
        question = QUERY.format(question=prompt)
        res = db_chain.invoke(question)
        # print(res)
        # print(res['result'])
        return res['result']
    except Exception as e:
        print('error:', e)
        raise e


if __name__ == "__main__":
    prompt = "Is there any discounts right now?"
    print(getResponse(prompt))
