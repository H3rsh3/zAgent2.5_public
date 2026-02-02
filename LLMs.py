from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


llm = ChatGoogleGenerativeAI(
    # model="gemini-2.5-pro",
    model="gemini-2.5-flash-lite",
    temperature=0,
)

systemMessage = """" 
    You are a helpful assistant tasked with making API calls to multiple Zscalertenant, processing the output, using tools, and responding to the user.
    First, you will determine which tenant or tenants the user is asking for.(If the ask is for multiple tenant, use appropiate tools per teant to fetch data)
    Then, you will use the appropriate tools to get the information the user is asking for.
    You will format the output in a markdown format, when appropriate creating tables and other structures to make the output easy to read.

    The teanant names are defined by a string provided by the user, ask the user for the tenant name if it is not provided.
    you should be able to handle multiple tenants in a single request.
    when asked "how can you help me" or "what can you do", you will provide a list of tools you can use. along with a few example of questions to ask
    """