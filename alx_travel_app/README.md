 Background Jobs for Email Notifications

## 📘 Overview
This milestone enhances the **`alx_travel_app`** project by introducing **asynchronous background processing** using **Celery** with **RabbitMQ** as the message broker.  
The goal is to offload time-consuming email sending tasks from the main request–response cycle, improving **performance**, **scalability**, and **user experience**.

---

## 🚀 Objectives
- Integrate **Celery** into the Django project.
- Configure **RabbitMQ** as the Celery message broker.
- Set up a **worker process** to handle background tasks.
- Implement **email notification** jobs.
- Ensure that email sending happens **asynchronously** and does **not block** user actions.
- Use **Docker Compose** for environment setup.

---

## 🧩 Tech Stack
| Component | Description |
|------------|-------------|
| **Django** | Web framework |
| **Celery** | Task queue for asynchronous jobs |
| **RabbitMQ** | Message broker |
| **Redis** | Result backend (optional but recommended) |
| **Docker** | Containerization |
| **Python 3.x** | Language |
| **SMTP** | Email sending (e.g., Gmail, Mailtrap, etc.) |

