# Project Hub: Deloitte IoT Converter & Proposal Generator

Welcome to the workspace! This repository contains a collection of utility scripts, templates, and documents developed for Deloitte client proposals and IoT system testing.

---

## 📂 Project Structure & Files

Here is the complete list of files in the workspace and their roles:

### 1. IoT Telemetry JSON Format Converter
- **[main.py](file:///c:/Users/HP/OneDrive/Desktop/Deloitte/main.py)**: A Python utility that normalizes IoT telemetry data. It converts two different JSON payload structures from IoT devices into a single standardized output structure. It also hosts a basic HTTP server to trigger its test suite dynamically.
- **[.replit](file:///c:/Users/HP/OneDrive/Desktop/Deloitte/.replit)**: Configuration file for running the project environment, specifying run commands, port forwarding (`8080` -> `80`), and Replit workflows.

### 2. Daikibo Proposal Generator
- **[generate_docx.py](file:///c:/Users/HP/OneDrive/Desktop/Deloitte/generate_docx.py)**: A Python script utilizing `python-docx` to programmatically build a highly styled Word document proposal (`Daikibo_Development_Proposal.docx`).
- **[Daikibo_Development_Proposal.docx](file:///c:/Users/HP/OneDrive/Desktop/Deloitte/Daikibo_Development_Proposal.docx)**: The generated software development proposal detailing the real-time status dashboard for Daikibo Manufacturing (36 devices across 4 factories).

### 3. Additional Assets
- **[Certificate.pdf](file:///c:/Users/HP/OneDrive/Desktop/Deloitte/Certificate.pdf)**: A PDF certificate file relevant to the project or candidate verification.

---

## 🚀 How to Run the Applications

### A. Run the JSON Converter and HTTP Server
To execute the tests and start the local HTTP server, run:
```bash
python main.py
```
- **Tests**: The script runs self-contained test cases and outputs `All tests passed` in the terminal if everything works.
- **HTTP Server**: Starts a server on port `8080`. Sending a `GET` request to `http://localhost:8080` will trigger the tests dynamically and return a JSON status response:
  ```json
  {
    "status": "success",
    "message": "All tests passed"
  }
  ```

### B. Generate the Daikibo Proposal Document
To (re)generate the styled Word document proposal (`Daikibo_Development_Proposal.docx`), run:
```bash
python generate_docx.py
```
This script dynamically applies margins, custom color themes (Navy/Slate), table styling, and bullet points to generate the final Word document.

---

## 🛠️ Telemetry Conversion Specifications

The `main.py` tool converts:
- **Format 1**: Flat format with a forward-slash separated path for location (e.g., `japan/tokyo/keiyō-industrial-zone/factory-1/section-2`) and flat telemetry fields.
- **Format 2**: Nested format with device attributes, ISO-8601 timestamps (parsed to epoch milliseconds), and structured telemetry.
- **Normalized Output**: Consistently produces a structured JSON with:
  - `deviceID` & `deviceType`
  - `timestamp` (as milliseconds epoch)
  - `location` (split into `country`, `city`, `area`, `factory`, `section`)
  - `data` (containing normalized metrics like `status` and `temperature`)

