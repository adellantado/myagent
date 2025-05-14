import os
import subprocess

from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

from tools import (
    save_content_to_file,
    setup_python_environment_and_install_deps,
    execute_script,
    notify_via_telegram,
)

load_dotenv()

def create_asset_pricer_agent():
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        print("To run this example, get a key from https://platform.openai.com/api-keys")
    else:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)

    tools = [
        save_content_to_file,
        setup_python_environment_and_install_deps,
        execute_script,
        notify_via_telegram,
    ]

    # Define the prompt for the agent
    # This prompt needs to guide the LLM to use the tools in sequence.
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that helps users building python scripts to automate different tasks on a pc.
        Also you can run the scripts you build.
        You have access to the following tools:
        {{tools}}
         
        To build a script, you must follow these steps strictly:
        1.  Make a python script that does what user asked for. The script should be able to run on its own and not depend on any other files.
        2.  Call `save_content_to_file` to save the generated Python script.
        3.  Call `setup_python_environment_and_install_deps` to create a virtual environment and install the required dependencies.
        4.  Call `execute_script` to run the generated script in the virtual environment.
        5.  If the script requires any additional input, ask the user for it.
        6.  If the script generates any output, return it to the user.
        7.  If the script fails, report the error to the user.
        
        To run existing scripts, you must:
        1. Call `execute_script` to run the script in the virtual environment.
        2. If needed notify the user about results with `notify_via_telegram` tool, add a header description about what was sent, apply beautiful formatting.

        Use the tool_names and tool_input arguments correctly.
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # This is a modern way to create an agent that can call tools.
    # It requires an LLM that supports tool calling (e.g., OpenAI's newer models, Gemini, Anthropic Claude 3).
    # If your LLM doesn't support native tool calling in this way, you might need
    # to use a ReAct agent or a structured chat agent with different prompting.
    try:
        
        agent = create_tool_calling_agent(llm, tools, prompt_template)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor
    except ImportError:
        print("Could not import `create_tool_calling_agent`. Ensure you have a compatible LangChain version.")
        print("You might need to use an older agent creation method (e.g., initialize_agent) if your LLM or LangChain version requires it.")
        return None


# --- Main Execution ---
if __name__ == "__main__":
    print("WARNING: This script can execute commands (pip install) and run generated Python code.")
    print("Understand the security risks before proceeding.\n")

    # --- Check for OpenAI API Key (example) ---
    if not os.environ.get("OPENAI_API_KEY"):
        print("Reminder: The OPENAI_API_KEY environment variable is not set.")
        print("The agent will use a placeholder LLM and will not function as intended.")
        print("Set this variable if you want to use OpenAI's LLM.\n")

    asset_pricer_agent_executor = create_asset_pricer_agent()

    if asset_pricer_agent_executor:

            input = input("Ask the agent below:\n")
            try:
                result = asset_pricer_agent_executor.invoke({
                    "input": f"{input}",
                    "agent_scratchpad": "",
                    "chat_history": [] # Add chat history if needed for conversational context
                })
                print("\n--- Agent Final Output ---")
                print(result.get("output", "No output from agent."))
            except Exception as e:
                print(f"\nAn error occurred while running the agent: {e}")
    else:
        print("Failed to create the agent executor. Check LLM configuration and LangChain setup.")

    print("\n--- Agentic Process Complete ---")