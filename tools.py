import os
from typing import List, Dict, Any, Tuple
import venv
import sys
import subprocess
from ui.telegram_ui import TelegramUI

from langchain_core.tools import tool

@tool
def save_content_to_file(filename: str, content: str) -> str:
    """
    Saves the given content to a file.
    Input 'filename' is the name of the file to save.
    Input 'content' is the string content to write into the file.
    Returns a success message with the filename or an error message.
    """
    try:
        filename = f"scripts/{filename}"
        with open(filename, "w") as f:
            f.write(content)
        return {
            "status": "success",
            "message": f"Successfully saved content to '{os.path.abspath(filename)}",
            "script_path": os.path.abspath(filename),
        }
    except Exception as e:
        return f"Error saving file '{filename}': {e}"
    

@tool
def setup_python_environment_and_install_deps(requirements_content: str, filename: str) -> Dict[str, str]:
    """
    Creates a Python virtual environment, and installs dependencies from requirements content.
    'requirements_content' is a string containing package names (e.g., "yfinance\\nrequests").
    'filename' is used to name the virtual environment folder the same as the script.
    Returns a dictionary with the path to the virtual environment's Python interpreter and status.
    """
    venv_name = f"scripts/venv_{filename.replace('-', '_')}"
    requirements_filename = f"scripts/requirements_{filename.replace('-', '_')}.txt"

    try:
        # Save temporary requirements file
        with open(requirements_filename, "w") as f:
            f.write(requirements_content)

        # Create virtual environment
        print(f"Creating virtual environment: {venv_name}...")
        venv.create(venv_name, with_pip=True)
        print(f"Virtual environment '{venv_name}' created.")

        # Determine python and pip paths based on OS
        if sys.platform == "win32":
            python_executable = os.path.join(venv_name, "Scripts", "python.exe")
            pip_executable = os.path.join(venv_name, "Scripts", "pip.exe")
        else: # macOS/Linux
            python_executable = os.path.join(venv_name, "bin", "python")
            pip_executable = os.path.join(venv_name, "bin", "pip")

        # Install dependencies
        print(f"Installing dependencies from {requirements_filename} into {venv_name}...")
        print(f"Executing: {pip_executable} install -r {requirements_filename}")

        # IMPORTANT SECURITY NOTE: subprocess.run executes commands on your system.
        # Ensure you trust the source of 'requirements_content'.
        process = subprocess.run(
            [pip_executable, "install", "-r", requirements_filename],
            capture_output=True, text=True, check=False # check=False to handle errors manually
        )
        if process.returncode != 0:
            error_message = f"Error installing dependencies into '{venv_name}': {process.stderr}"
            print(error_message)
            # Clean up temp requirements file if install fails
            try:
                pass
                #os.remove(requirements_filename)
            except OSError:
                pass # Ignore if already removed or not created
            return {"status": "error", "message": error_message, "venv_python_path": None}

        print(f"Dependencies installed successfully in '{venv_name}'.")
        # Clean up temp requirements file
        # os.remove(requirements_filename)

        return {
            "status": "success",
            "message": f"Environment '{venv_name}' setup with dependencies. Python at: {python_executable}",
            "venv_python_path": os.path.abspath(python_executable),
        }

    except Exception as e:
        message = f"Error setting up Python environment '{venv_name}': {e}"
        print(message)
        return {"status": "error", "message": message, "venv_python_path": None}
    
@tool
def execute_script(script_path: str, run_argument: str) -> str:
    """
    Executes the generated asset price checking Python script in its virtual environment.
    'script_path' is the path to the Python script to run.
    'run_argument' is the argument to pass to the script (e.g., ticker symbol or crypto ID).
    Returns the output of the script (stdout).
    """
    try:
        if '/' not in script_path:
            # full path current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(current_dir, "scripts", script_path)
        script_name = os.path.splitext(os.path.basename(script_path))[0]
        venv_python_path = os.path.join(os.path.dirname(script_path), f"venv_{script_name}", "bin", "python")
        script_path = f"{script_path}"
        print(f"Executing script: {venv_python_path} {script_path} {run_argument}")
        # IMPORTANT SECURITY NOTE: subprocess.run executes the generated script.
        # Ensure you trust the script's origin and content.
        process = subprocess.run(
            [venv_python_path, script_path, run_argument],
            capture_output=True, text=True, check=True, timeout=30 # Added timeout
        )
        output = process.stdout.strip()
        print(f"Script output:\n{output}")
        return output
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing script '{script_path}': {e.stderr.strip()}"
        print(error_message)
        return error_message
    except subprocess.TimeoutExpired:
        error_message = f"Script '{script_path}' timed out after 30 seconds."
        print(error_message)
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred while executing script '{script_path}': {e}"
        print(error_message)
        return error_message
    
@tool
def notify_via_telegram(message: str) -> str:
    """
    Sends a notification via Telegram.
    Returns a success message or an error message.
    """
    try:
        # Replace with your actual bot token and chat ID
        bot_token = os.environ.get("TELEGRAM_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        telegram_ui = TelegramUI(bot_token, chat_id)
        response = telegram_ui.send_message(message)
        
        if response.get("ok"):
            return f"Notification sent successfully: {response['result']['message_id']}"
        else:
            return f"Failed to send notification: {response.get('description')}"
    except Exception as e:
        return f"Error sending notification: {e}"