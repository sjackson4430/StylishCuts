from app import app

if __name__ == "__main__":
    # Run the application on port 5000 without debug mode
    # Using HTTP for local development
    app.run(host="0.0.0.0", port=5000, debug=False)
