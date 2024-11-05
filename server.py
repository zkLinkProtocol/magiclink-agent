from phi.playground import Playground, serve_playground_app
from main import chatbot

app = Playground(agents=[chatbot]).get_app()

if __name__ == "__main__":
  serve_playground_app("server:app", reload=True)