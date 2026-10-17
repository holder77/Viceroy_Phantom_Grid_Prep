from flask import Flask, request, make_response

app = Flask(__name__)

CSS = '''
<style>
    body {
        background-color: #0b0f19;
        color: #00ffcc;
        font-family: 'Courier New', Courier, monospace;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
        text-align: center;
    }
    .container {
        background: rgba(0, 20, 40, 0.8);
        border: 1px solid #00ffcc;
        box-shadow: 0 0 15px #00ffcc;
        padding: 40px;
        border-radius: 8px;
        width: 350px;
    }
    h2 {
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    input[type="text"], input[type="password"] {
        width: 90%;
        padding: 10px;
        margin: 10px 0;
        background: #000;
        border: 1px solid #00ffcc;
        color: #00ffcc;
        outline: none;
    }
    input[type="submit"] {
        background: #00ffcc;
        color: #000;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        cursor: pointer;
        text-transform: uppercase;
        transition: 0.3s;
        margin-top: 15px;
    }
    input[type="submit"]:hover {
        background: #fff;
        box-shadow: 0 0 10px #fff;
    }
    img {
        max-width: 100%;
        border: 2px solid #00ffcc;
        margin-top: 20px;
    }
    .error {
        color: #ff3366;
        text-shadow: 0 0 5px #ff3366;
    }
</style>
'''

@app.route('/.env')
def exposed_env():
    return "DB_USER=admin\nDB_PASS=P@ssw0rd123\nSECRET_KEY=supersecretkey\nFLAG_PART_1=viceroy{nuc13i_f0und", 200, {'Content-Type': 'text/plain'}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        resp = make_response("Redirecting to dashboard...")
        resp.set_cookie('role', 'operator')
        resp.headers['Location'] = '/dashboard'
        return resp, 302
        
    return f'''
        <!DOCTYPE html>
        <html>
        <head><title>SENTINEL-01 Relay</title></head>
        {CSS}
        <body>
            <div class="container">
                <h2>SENTINEL-01<br>Ground Relay Portal</h2>
                <form method="POST">
                    <input type="text" name="user" placeholder="USERNAME" required/><br>
                    <input type="password" name="pass" placeholder="PASSWORD" required/><br>
                    <input type="submit" value="Authenticate"/>
                </form>
            </div>
        </body>
        </html>
    '''

@app.route('/dashboard')
def dashboard():
    role = request.cookies.get('role', 'guest')
    if role == 'admin':
        return f'''
            <!DOCTYPE html>
            <html>
            <head><title>Dashboard</title></head>
            {CSS}
            <body>
                <div class="container">
                    <h2>Welcome Admin</h2>
                    <p>Access Granted.</p>
                    <p>FLAG_PART_2=_th3_0p3n_d00r}}</p>
                    <img src="/static/computerkid.gif" alt="Thumbs Up">
                </div>
            </body>
            </html>
        '''
    return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard</title></head>
        {CSS}
        <body>
            <div class="container">
                <h2 class="error">Access Denied</h2>
                <p>Current role: <strong>{role}</strong></p>
                <p>Administrator privileges required.</p>
            </div>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)