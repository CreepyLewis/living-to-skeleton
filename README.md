{
  "name": "interactive-workspace",
  "version": "1.0.0",
  "description": "An interactive workspace with clickable icons",
  "main": "src/app.js",
  "scripts": {
    "start": "webpack serve --mode development",
    "build": "webpack --mode production",
    "dev": "nodemon src/app.js",
    "test": "jest",
    "deploy": "gh-pages -d dist",
    "docker:build": "docker build -t workspace .",
    "docker:run": "docker run -p 3000:3000 workspace",
    "setup": "npm install && cp .env.example .env"
  },
  "keywords": ["workspace", "interactive", "starter", "template"],
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.4.0",
    "socket.io": "^4.6.1"
  },
  "devDependencies": {
    "webpack": "^5.88.0",
    "webpack-cli": "^5.1.4",
    "webpack-dev-server": "^4.15.1",
    "nodemon": "^2.0.22",
    "jest": "^29.5.0",
    "gh-pages": "^5.0.0",
    "eslint": "^8.44.0"
  }
}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Interactive Workspace</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🏗️ Interactive Workspace</h1>
            <p class="subtitle">Click icons to launch your development environment</p>
        </header>

        <div class="workspace-grid">
            <!-- Online IDEs -->
            <div class="workspace-card" onclick="window.open('https://codesandbox.io', '_blank')">
                <div class="icon">⚡</div>
                <h3>CodeSandbox</h3>
                <p>Browser-based IDE for web development</p>
                <button class="launch-btn">Launch</button>
            </div>

            <div class="workspace-card" onclick="window.open('https://replit.com', '_blank')">
                <div class="icon">💻</div>
                <h3>Replit</h3>
                <p>Instant coding workspace with collaboration</p>
                <button class="launch-btn">Launch</button>
            </div>

            <div class="workspace-card" onclick="window.open('https://stackblitz.com', '_blank')">
                <div class="icon">🎨</div>
                <h3>StackBlitz</h3>
                <p>Web IDE for full-stack applications</p>
                <button class="launch-btn">Launch</button>
            </div>

            <div class="workspace-card" onclick="window.open('https://glitch.com', '_blank')">
                <div class="icon">🔧</div>
                <h3>Glitch</h3>
                <p>Remix and deploy web apps instantly</p>
                <button class="launch-btn">Launch</button>
            </div>

            <!-- Local Setup -->
            <div class="workspace-card" onclick="showSetupGuide()">
                <div class="icon">📦</div>
                <h3>Local Setup</h3>
                <p>Set up project on your machine</p>
                <button class="setup-btn">Setup Guide</button>
            </div>

            <div class="workspace-card" onclick="window.open('https://github.com/codespaces', '_blank')">
                <div class="icon">☁️</div>
                <h3>GitHub Codespaces</h3>
                <p>Cloud development environment</p>
                <button class="launch-btn">Launch</button>
            </div>

            <div class="workspace-card" onclick="window.open('https://gitpod.io', '_blank')">
                <div class="icon">🚀</div>
                <h3>Gitpod</h3>
                <p>Ready-to-code development environment</p>
                <button class="launch-btn">Launch</button>
            </div>

            <div class="workspace-card" onclick="window.open('https://labs.play-with-docker.com', '_blank')">
                <div class="icon">🐳</div>
                <h3>Docker Playground</h3>
                <p>Docker environment in your browser</p>
                <button class="launch-btn">Launch</button>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
            <h2>⚡ Quick Actions</h2>
            <div class="action-buttons">
                <button onclick="runCommand('npm install')" class="action-btn">
                    <span class="action-icon">📦</span> Install Dependencies
                </button>
                <button onclick="runCommand('npm start')" class="action-btn">
                    <span class="action-icon">🚀</span> Start Server
                </button>
                <button onclick="runCommand('npm run build')" class="action-btn">
                    <span class="action-icon">🏗️</span> Build Project
                </button>
                <button onclick="runCommand('npm test')" class="action-btn">
                    <span class="action-icon">🧪</span> Run Tests
                </button>
                <button onclick="showTerminal()" class="action-btn">
                    <span class="action-icon">💻</span> Open Terminal
                </button>
            </div>
        </div>

        <!-- Setup Guide Modal -->
        <div id="setupGuide" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <h2>📋 Local Setup Guide</h2>
                <div class="steps">
                    <div class="step">
                        <span class="step-number">1</span>
                        <h3>Clone Repository</h3>
                        <pre><code>git clone https://github.com/yourusername/workspace-starter.git
cd workspace-starter</code></pre>
                    </div>
                    <div class="step">
                        <span class="step-number">2</span>
                        <h3>Install Dependencies</h3>
                        <pre><code>npm install</code></pre>
                    </div>
                    <div class="step">
                        <span class="step-number">3</span>
                        <h3>Configure Environment</h3>
                        <pre><code>cp .env.example .env
# Edit .env with your settings</code></pre>
                    </div>
                    <div class="step">
                        <span class="step-number">4</span>
                        <h3>Start Development Server</h3>
                        <pre><code>npm start</code></pre>
                        <p>Open <a href="http://localhost:3000" target="_blank">http://localhost:3000</a></p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Terminal Simulator -->
        <div id="terminal" class="terminal">
            <div class="terminal-header">
                <h3>💻 Terminal</h3>
                <button onclick="closeTerminal()" class="close-terminal">×</button>
            </div>
            <div class="terminal-body">
                <div id="terminal-output"></div>
                <div class="terminal-input">
                    <span class="prompt">$</span>
                    <input type="text" id="command-input" placeholder="Type a command...">
                </div>
            </div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    text-align: center;
    color: white;
    margin-bottom: 40px;
    padding: 20px;
}

.header h1 {
    font-size: 3rem;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
}

.workspace-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px;
    margin-bottom: 40px;
}

.workspace-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
    cursor: pointer;
}

.workspace-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.3);
}

.workspace-card .icon {
    font-size: 3rem;
    margin-bottom: 15px;
}

.workspace-card h3 {
    color: #333;
    margin-bottom: 10px;
    font-size: 1.4rem;
}

.workspace-card p {
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 20px;
    line-height: 1.4;
}

.launch-btn, .setup-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 10px 25px;
    border-radius: 25px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.setup-btn {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.launch-btn:hover, .setup-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.quick-actions {
    background: rgba(255,255,255,0.9);
    border-radius: 15px;
    padding: 30px;
    margin-bottom: 30px;
}

.quick-actions h2 {
    text-align: center;
    margin-bottom: 25px;
    color: #333;
}

.action-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    justify-content: center;
}

.action-btn {
    background: white;
    border: 2px solid #667eea;
    color: #667eea;
    padding: 12px 25px;
    border-radius: 30px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 10px;
}

.action-btn:hover {
    background: #667eea;
    color: white;
    transform: translateY(-2px);
}

.action-icon {
    font-size: 1.2rem;
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.8);
    z-index: 1000;
}

.modal-content {
    background: white;
    margin: 5% auto;
    padding: 30px;
    border-radius: 15px;
    width: 90%;
    max-width: 800px;
    position: relative;
}

.close {
    position: absolute;
    right: 25px;
    top: 15px;
    font-size: 28px;
    cursor: pointer;
    color: #666;
}

.steps {
    margin-top: 20px;
}

.step {
    background: #f8f9fa;
    border-left: 4px solid #667eea;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 0 8px 8px 0;
}

.step-number {
    background: #667eea;
    color: white;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
}

.step h3 {
    display: inline;
    color: #333;
}

.step pre {
    background: #2d2d2d;
    color: #f8f8f2;
    padding: 15px;
    border-radius: 5px;
    margin: 15px 0;
    overflow-x: auto;
}

.step code {
    font-family: 'Courier New', monospace;
}

/* Terminal Styles */
.terminal {
    position: fixed;
    bottom: 0;
    right: 20px;
    width: 600px;
    max-width: 90vw;
    height: 400px;
    background: #1e1e1e;
    border-radius: 10px 10px 0 0;
    display: none;
    flex-direction: column;
    box-shadow: 0 -5px 25px rgba(0,0,0,0.3);
    z-index: 1001;
}

.terminal-header {
    background: #333;
    color: white;
    padding: 15px;
    border-radius: 10px 10px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.terminal-body {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
}

#terminal-output {
    color: #00ff00;
    font-family: 'Courier New', monospace;
    margin-bottom: 15px;
    white-space: pre-wrap;
}

.terminal-input {
    display: flex;
    align-items: center;
    gap: 10px;
}

.prompt {
    color: #00ff00;
    font-family: 'Courier New', monospace;
}

#command-input {
    flex: 1;
    background: transparent;
    border: none;
    color: white;
    font-family: 'Courier New', monospace;
    font-size: 1rem;
    outline: none;
}

.close-terminal {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0 10px;
}

/* Responsive Design */
@media (max-width: 768px) {
    .workspace-grid {
        grid-template-columns: 1fr;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .action-buttons {
        flex-direction: column;
    }
    
    .action-btn {
        width: 100%;
        justify-content: center;
    }
    
    .terminal {
        width: 100%;
        right: 0;
        height: 300px;
    }
}
