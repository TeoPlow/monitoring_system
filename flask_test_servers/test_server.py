from flask import Flask, jsonify
import random
import time
import os

app = Flask(__name__)

boot_time = time.time()

def get_uptime():
    uptime_seconds = int(time.time() - boot_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

@app.route('/status')
def status():
    # cpu = random.randint(70, 100)
    cpu = 99
    mem = random.randint(80, 100)
    disk = random.randint(90, 100)

    uptime = get_uptime()
    return jsonify({
        "cpu": cpu,
        "mem": f"{mem}%",
        "disk": f"{disk}%",
        "uptime": uptime
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)