from flask import Flask, jsonify
import psutil
import time
import os

app = Flask(__name__)

boot_time = psutil.boot_time()

def get_uptime():
    uptime_seconds = int(time.time() - boot_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

@app.route('/status')
def status():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    uptime = get_uptime()
    return jsonify({
        "cpu": int(cpu),
        "mem": f"{int(mem)}%",
        "disk": f"{int(disk)}%",
        "uptime": uptime
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
