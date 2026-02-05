SecureCert: Blockchain-Based Certificate Verification System
          SecureCert is a decentralized application (DApp) designed to eliminate certificate forgery and simplify the verification process using Ethereum Blockchain technology.

📌 Features
  Immutable Storage: Certificate hashes are stored on the Blockchain, making them tamper-proof.

  Instant Verification: Recruiters can verify the authenticity of a document in seconds.

  Admin Dashboard: Centralized panel to issue certificates and manage student records.

Automated Audit: Built-in auditing system to check document integrity against blockchain records.

🛠️ Tech Stack
Frontend: HTML5, CSS3, JavaScript (Flask Templates)

Backend: Python (Flask)

Blockchain: Solidity (Smart Contracts), Ganache (Local Blockchain)

Library: Web3.py (to interact with Ethereum)

📂 Project Structure
Plaintext
├── contract/
│   └── Certificate.sol      # Smart contract code
├── static/
│   ├── uploads/             # Temporarily stored docs for audit
│   └── results/             # Generated reports
├── templates/
│   ├── admin.html           # Admin panel UI
│   └── index.html           # Main user interface
├── cert.py                  # Main Flask application logic
├── deploy.py                # Script to deploy contract to Ganache
└── deployed_info.json       # Stores contract address and ABI
🚀 Getting Started
1. Prerequisites
Python 3.x

Ganache (Truffle Suite)

Metamask (Optional for browser interaction)

2. Setup
Start Ganache: Open Ganache and ensure the RPC Server is running at http://127.0.0.1:7545.

Deploy Contract:

Bash
python deploy.py
Run Application:

Bash
python cert.py
Access UI: Open http://127.0.0.1:5000 in your browser.

📊 System Workflow
Admin logs in and issues a certificate for a Student.

The system generates a Digital Hash of the certificate and records it on the Blockchain.

A Recruiter uploads the certificate to the "Execute Audit" section.

The system compares the uploaded file's hash with the one on the Blockchain.

Result: Returns "Authentic" or "Invalid/Tampered".
