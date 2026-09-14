# CoCare
### Intelligent AI-Powered Customer Service System for Telecom Companies

CoCare is an AI-powered customer service prototype designed for the telecommunications sector. It combines Natural Language Processing (NLP), sentiment analysis, network issue prediction, and interactive dashboards to improve customer support and assist telecom employees in monitoring customer and network-related issues.

## Current Features

- Bilingual Arabic and English AI chatbot
- Arabic and English intent classification
- Arabic and English sentiment analysis
- Network issue prediction
- Customer dashboard
- Employee dashboard
- Network diagnostics and monitoring
- Alerts and escalation logic
- Telecom service features such as package inquiries, renewal, and data usage

## AI Models

| Component | Model | Result |
|---|---|---|
| English Intent Classification | DistilBERT | 96.05% Accuracy |
| Arabic Intent Classification | XLM-RoBERTa | 89.61% Accuracy |
| Arabic Sentiment Analysis | AraBERT | 87.04% Accuracy |
| English Sentiment Analysis | Twitter-RoBERTa | 84.61% Accuracy |
| Network Issue Prediction | XGBoost | 85.33% Accuracy |

## How CoCare Works

Customer Message  
↓  
Language Detection  
↓  
Intent Classification  
↓  
Sentiment Analysis  
↓  
Network Prediction Check  
↓  
Decision Logic  
↓  
Response / Alert / Escalation

## Main Project Components

- `backend/` – Backend-related components
- `cocare-streamlit-app/` – Streamlit application
- `intent_arabic/` – Arabic intent classification
- `intent_eng/` – English intent classification
- `sentiment_arabic/` – Arabic sentiment analysis
- `sentiment_eng/` – English sentiment analysis
- `prediction/` – Network issue prediction
- `pages/` – Application pages
- `utils/` – Utility functions

## Technologies

- Python
- Streamlit
- HuggingFace Transformers
- Scikit-learn
- XGBoost
- Pandas
- Plotly
- SQLite
- NLP

## Current Project Status

CoCare is currently a functional academic prototype.

The current version demonstrates the integration of AI-based customer support, sentiment analysis, network issue prediction, and customer/employee dashboards.

The prototype is not currently connected to live telecom infrastructure, real customer accounts, production billing systems, or live network APIs. Network-related testing currently relies on simulated telecom data.

## Future Vision

The next stage of CoCare aims to evolve the prototype into a secure and scalable telecom platform through:

- Production-oriented backend development
- Scalable database architecture
- Ticketing and complaint management
- Human-agent handoff
- Secure telecom API integration
- Real customer-service data integration
- Real network KPI integration
- AI model validation and retraining using real telecom data
- Mobile application development
- Cloud deployment
- Controlled pilot with a telecom company

## Project Vision

Our long-term goal is to connect:

**Customer Service + Artificial Intelligence + Customer Sentiment + Network Intelligence + Human Agents + Telecom Operations**

CoCare aims to evolve beyond a traditional chatbot into an intelligent platform that supports both telecom customers and employees.

## Project Status

Academic Graduation Project – Artificial Intelligence & Robotics

## Contact

For collaboration, technical evaluation, or pilot opportunities:

**Wasan Alarman**  
Artificial Intelligence & Robotics
