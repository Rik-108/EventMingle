# EventMingle: Cloud-Native Event Management 📅☁️

## 📌 Project Overview
**EventMingle** is a full-stack, cloud-native event management platform designed to connect organizers and attendees seamlessly. Built with a **Flask** backend and deployed on **AWS EC2**, the application leverages a fully serverless AWS data layer to handle high-volume event registration, real-time attendance tracking, and user feedback. It features a robust Role-Based Access Control (RBAC) system, offering dedicated, dynamic dashboards for Admins, Organizers, and Attendees.

## 🚀 Key Features
* **Role-Based Architecture:** Secure authentication system using `Werkzeug` password hashing, routing users to specific Jinja2 dashboards based on their profile (Admin oversight, Organizer creation, Attendee participation).
* **Serverless Data Layer:** Utilizes **AWS DynamoDB** for fast, scalable NoSQL storage, managing highly relational data across 6 distinct tables (Users, Events, RSVPs, Attendance, Feedback, CommunicationLog).
* **Event-Driven Notifications:** Integrated with **AWS SNS** (Simple Notification Service) to automatically publish real-time alerts to organizers the moment an attendee submits event feedback.
* **Automated Infrastructure Provisioning:** Includes a custom Bash deployment script (`setup.sh`) utilizing `boto3` to automatically verify and provision the required DynamoDB schema upon deployment.
* **Modern Frontend:** Built with **Tailwind CSS** and vanilla JavaScript, featuring dynamic participation trend tracking, interactive forms, and asynchronous UI alerts.

---

## 🏗️ Architecture Details

### The Application Backend (`Flask`)
The core routing and application logic acts as the bridge between the client and the AWS cloud.
* **Session Management:** Implements secure, server-side session persistence to maintain stateful user logins across the various interactive dashboards.
* **Security & Auditing:** Features comprehensive request logging (`app.log`) to track authentication attempts, API calls, and system errors for compliance monitoring and debugging.

### Cloud Infrastructure (`AWS / Boto3`)
The system is designed for high availability and low-latency data retrieval.
* **DynamoDB Integration:** Replaces traditional SQL with a highly scalable key-value NoSQL structure. The backend utilizes `boto3` to perform rapid `put_item` and `scan` operations for dashboard rendering.
* **Communication Oversight:** Maintains a dedicated `CommunicationLog` table mapped with unique `uuid4` identifiers to track the flow of automated SNS notifications and user feedback securely.

---

## ⚖️ Application Workflow Logic
The platform is engineered to handle the complete lifecycle of a corporate or social event:

1.  **Event Instantiation:** Organizers create events, storing metadata (Date, Description, Title) directly in DynamoDB.
2.  **Participation Tracking:** Attendees view available events, generating specific RSVP and Attendance records that update the Organizer's live dashboard.
3.  **Feedback Loop & Alerting:** Upon event completion, attendees submit reviews. The backend simultaneously writes this to the NoSQL database *and* triggers an SNS push notification to alert the administrative team instantly.

---

## 🛠️ Technology Stack
* **Backend Framework:** Python 3, Flask, Werkzeug
* **Cloud Infrastructure:** AWS EC2, AWS DynamoDB (NoSQL), AWS SNS (Pub/Sub)
* **Cloud SDK:** Boto3
* **Frontend UI:** HTML5, Tailwind CSS, JavaScript, Jinja2 Templates

---

## ⚙️ Setup & Deployment
To provision and run this application on an AWS EC2 instance:

1. **Install Dependencies & Provision Database:**
   Run the setup script to install packages and automatically build the DynamoDB tables.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
2. **Configure AWS Credentials:**
   Ensure your `.aws/credentials` file is configured with the correct IAM roles to access DynamoDB and SNS. Update `config.py` with your specific `AWS_REGION` and `SNS_TOPIC_ARN`.
3. **Launch the Server:**
   ```bash
   python3 app.py
   ```
   *The application will be accessible via port 5000 on your EC2 instance's public IP.*

---

## 👥 Contributors
This project was developed to showcase scalable cloud architecture.
* **Anik Basu** 
