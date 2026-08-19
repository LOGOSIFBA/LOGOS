from flask import Flask

app = Flask(_Name_)

@app.route("/")
def home():
  print("Pega a visão")
