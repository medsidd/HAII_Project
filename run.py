import subprocess
import os
import platform

def start_flask():
    """Start the Flask backend."""
    print("Starting Flask backend...")
    flask_process = subprocess.Popen(["python", "backend/app.py"], cwd=os.getcwd())
    return flask_process

def start_react():
    """Start the React frontend."""
    print("Starting React frontend...")
    # Determine the command based on the platform
    npm_command = "npm.cmd" if platform.system() == "Windows" else "npm"
    react_process = subprocess.Popen([npm_command, "start"], cwd=os.path.join(os.getcwd(), "frontend"))
    return react_process

def main():
    print("Starting the Mental Health Companion App...")
    
    # Start Flask and React processes
    flask_process = start_flask()
    react_process = start_react()

    try:
        # Wait for both processes
        flask_process.wait()
        react_process.wait()
    except KeyboardInterrupt:
        print("Shutting down the application...")
        flask_process.terminate()
        react_process.terminate()

if __name__ == "__main__":
    main()
