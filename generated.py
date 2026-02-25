import subprocess
import sys

def install_flask():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        print("Flask installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install Flask")
        return False

def create_flask_server():
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Hello from Flask Server!"
    
    @app.route('/about')
    def about():
        return "This is a simple Flask server"
    
    @app.route('/sum')
    def show_sum():
        from previous_code import sum_numbers
        result = sum_numbers()
        return f"The sum from previous code is: {result}"
    
    return app

def run_server():
    if install_flask():
        app = create_flask_server()
        print("Starting Flask server on http://127.0.0.1:5000")
        print("Press Ctrl+C to stop the server")
        app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    run_server()