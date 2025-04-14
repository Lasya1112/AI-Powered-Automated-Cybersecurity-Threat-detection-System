# **MalWhere: AI-Powered Cybersecurity System**  

## **📌 Table of Contents**
1. [Introduction](#introduction)  
2. [Problem Statement](#problem-statement)  
3. [Objectives](#objectives)  
4. [Solution Overview](#solution-overview)  
5. [Technologies and Tools](#technologies-and-tools)  
6. [Deployment Guide](#deployment-guide)  
7. [Testing and Evaluation](#testing-and-evaluation)  
8. [Challenges Faced](#challenges-faced)  
9. [Ethical Considerations](#ethical-considerations)  
10. [Future Improvements](#future-improvements)  
11. [Conclusion](#conclusion)  

---

## **📌 1. Introduction**  
With the rise of **cyber threats**, detecting **network intrusions, malware, and phishing attacks** is essential for digital security. **MalWhere** leverages **AI and Azure services** to provide **real-time, intelligent threat detection**.  

---

## **📌 2. Problem Statement**  
Traditional cybersecurity systems struggle with **scalability, real-time threat detection, and false positives**. Our AI-driven approach enhances detection accuracy and **automates cybersecurity defenses**.  

---

## **📌 3. Objectives**  
- **Anomaly Detection (NIDS):** Identify suspicious network activity in real-time.  
- **Malware Detection:** Detect and classify malicious files before execution.  
- **Phishing Detection:** Flag phishing emails and malicious URLs.  
- **Cybersecurity Awareness Chatbot:** Educate users on cybersecurity best practices.  

---

## **📌 4. Solution Overview**  

### **🔹 4.1 Anomaly Detection (NIDS)**  
✔ **Captures live network packets** using **Scapy**.  
✔ **Extracts critical network features** (IP, ports, protocol, packet size).  
✔ **Classifies packets** using a **RandomForestClassifier** trained on **USTCTFC2016**.  
✔ **Detects threats in real-time** and enhances security monitoring.  

### **🔹 4.2 Malware Detection**  
✔ **Extracts file features** using **pefile** for Portable Executable (PE) analysis.  
✔ **Classifies files** as safe or malicious using a **Random Forest model**.  
✔ **Monitors the Downloads folder** for suspicious files.  
✔ **FastAPI backend handles malware classification requests**.  

### **🔹 4.3 Phishing Detection**  
✔ **Scans incoming emails** for phishing threats automatically.  
✔ **Categorizes emails** into **safe, suspicious, or phishing**.  
✔ **Logs phishing attempts** for security audits.  
✔ **Guides users** on preventing phishing attacks.  

### **🔹 4.4 Cybersecurity Awareness Chatbot**  
✔ **Uses Azure OpenAI GPT-4** to provide **AI-driven cybersecurity assistance**.  
✔ **Helps users handle security incidents** with step-by-step guidance.  
✔ **Available 24/7** to answer cybersecurity queries.  

---

## **📌 5. Technologies and Tools**  
| **Component**            | **Technology Used**  |
|--------------------------|---------------------|
| **AI Models**            | RandomForest, GPT-4 |
| **Network Traffic Analysis** | Scapy (Packet Sniffing) |
| **Malware Detection**    | pefile, FastAPI |
| **Email Processing**     | Azure Cognitive Services |
| **Deployment**           | Azure AI, Uvicorn, FastAPI |

---

## Deployment Guide
1. Set up Azure Storage and AI Services.
2. Add the following `.env` files:
   - **Phishing Detection:**
     ```
     AZURE_OPENAI_ENDPOINT=<your_endpoint>
     AZURE_API_KEY=<your_api_key>
     FETCH_EMAILS_URL=<your_fetch_emails_url>
     AZURE_OPENAI_DEPLOYMENT=<your_deployment>
     ```
   - **Chatbot:**
     ```
     AZURE_OPENAI_ENDPOINT=<your_endpoint>
     AZURE_API_KEY=<your_api_key>
     AZURE_OPENAI_DEPLOYMENT=<your_deployment>
     ```
3. Run the following scripts:
   - **Malware Classification Server:** `uvicorn server:app --host 0.0.0.0 --port 8000`
   - **File Monitoring Script:** `python MalwareDetectionInFiles/detectMalware.py`
   - **Network Packet Monitoring Script:** `python networkIntrusion/demo.py`
   - **Email Fetching Script:** `python phishingDetection/emailFetching.py`
   - **Phishing Detection Server:** `python phishingDetection/server.py`
   - **Chatbot Server:** `uvicorn server:app --host 127.0.0.1 --port 8000`
4. Deploy the application on Azure App Service or a cloud-based platform.

## Demo
[Link](https://drive.google.com/file/d/13Zn_wJayLrsKWwE3O22Ib9UM8TUL24Wd/view?usp=drive_link)

## Testing and Evaluation
- **Dataset Used:** Public cybersecurity datasets.
- **Metrics Evaluated:**
  - Accuracy & Precision
  - Recall
  - Inference Time
- **Testing Results:** Evaluated using standard cybersecurity datasets.

## Challenges Faced
- Handling imbalanced datasets for anomaly detection.
- Reducing false positives in phishing detection.
- Ensuring real-time processing without performance bottlenecks.

## Ethical Considerations
- **Bias Mitigation:** Ensuring fair and unbiased AI decision-making.
- **Data Privacy & Compliance:** Following GDPR and Microsoft Responsible AI guidelines.
- **Explainability:** Providing clear reasons for threat detection to end-users.

## Conclusion
MalWhere is an innovative AI-powered cybersecurity system that detects network intrusions, malware, and phishing threats. By integrating Azure AI services and machine learning, it enables organizations to enhance their security posture with real-time, AI-driven threat detection.
