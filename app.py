from flask import Flask, render_template
import tv

app = Flask(__name__)
@app.route('/')
def index():
  return render_template('index.html')


# Get commands take no parameters
@app.route('/get/<name>')
def get(name):
  return getattr(tv,"get" + name.title())()

# Set commands all take 1 parameter, most a number between 0-100, some On or Off (or 1 or 0), and an input name for setInput
@app.route('/set/<name>/<value>')
def set(name, value):
  # Make sure TV is on first - try up to 10 times while waiting for the TV to start
  if(name.title() != "Power" and tv.getPower() != "On"):
    for _ in range(10):
      tv.setPower(1)
      if (tv.getPower() == "On"):
        break

  return getattr(tv,"set" + name.title())(value)



if __name__ == '__main__':
  # Note:  App runs on port 8080, but iptables rule redirects port 80 to 8080
  # iptables -t nat -A PREROUTING -p tcpo --dport 80 -j REDIRECT --to-port 8080
  app.run(host='0.0.0.0',port=8080,debug=True)
