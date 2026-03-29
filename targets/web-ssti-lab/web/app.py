from flask import Flask, render_template_string, request

app = Flask(__name__)
app.config["FLAG"] = "CTF{jinja2_ssti_lands_fast_when_you_verify_the_sink}"


@app.route("/")
def home():
    return """
    <h1>Greeting Preview</h1>
    <p>Preview user greetings with <code>/greet?name=guest</code>.</p>
    <p>Operators sometimes inspect <code>config.FLAG</code> during template debugging.</p>
    """


@app.route("/greet", methods=["GET", "POST"])
def greet():
    name = request.values.get("name", "guest")
    template = f"""
    <html>
      <body>
        <h1>Hello {name}</h1>
        <p>Your greeting has been rendered.</p>
      </body>
    </html>
    """
    return render_template_string(template)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
