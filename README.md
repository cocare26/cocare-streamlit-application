# CoCare
### Intelligent AI-Powered Customer Service System for Telecom Companies

CoCare is an AI-powered customer service prototype designed for the telecommunications sector. It combines Natural Language Processing (NLP), sentiment analysis, network issue prediction, intelligent decision logic, and interactive dashboards to improve customer support and assist telecom employees in monitoring customer and network-related issues.

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
- Functional FastAPI backend prototype
- Initial Flutter / Dart mobile UI prototype

## AI Models

| Component | Model | Result | Trained Model Size |
|---|---|---:|---:|
| English Intent Classification | DistilBERT | 96.05% Accuracy | 255.5 MB |
| Arabic Intent Classification | XLM-RoBERTa | 89.61% Accuracy | 1.04 GB |
| Arabic Sentiment Analysis | AraBERT | 87.04% Accuracy | 515.8 MB |
| English Sentiment Analysis | Twitter-RoBERTa | 84.61% Accuracy | 475.5 MB |
| Network Issue Prediction | XGBoost | 85.33% Accuracy | Included in repository |

### Trained Model Artifacts

The trained Transformer model artifacts are **not stored directly in this GitHub repository because of their large file sizes**.

The complete trained models are preserved separately in Google Drive and include the required model weights, configurations, tokenizers, label mappings, and related artifacts.

Current trained model artifacts:

- **Arabic Intent – XLM-RoBERTa:** approximately **1.04 GB**
- **English Intent – DistilBERT:** approximately **255.5 MB**
- **Arabic Sentiment – AraBERT:** approximately **515.8 MB**
- **English Sentiment – Twitter-RoBERTa:** approximately **475.5 MB**

The XGBoost network prediction model is significantly smaller and is included directly in the `prediction/` directory of this repository.

The Transformer model artifacts can be provided separately for technical evaluation or deployment.

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
Decision & Escalation Logic  
↓  
Response / Alert / Escalation

## Main Project Components

- `backend/` – FastAPI backend, AI processing pipeline, database, notification and escalation logic
- `pages/` – Streamlit customer and employee application pages
- `intent_arabic/` – Arabic intent classification training resources and datasets
- `intent_eng/` – English intent classification resources and datasets
- `sentiment_arabic/` – Arabic sentiment analysis training notebook
- `sentiment_eng/` – English sentiment analysis training resources and dataset
- `prediction/` – Network issue prediction model, features, dataset, and experimentation notebook
- `mobile_prototype/` – Initial Flutter / Dart mobile interface prototype
- `app.py` – Main Streamlit application entry point
- `main_app.py` – Streamlit page routing
- `language_guard.py` – Arabic / English interface routing support

## Technologies

- Python
- Streamlit
- FastAPI
- Hugging Face Transformers
- PyTorch
- Scikit-learn
- XGBoost
- Pandas
- Plotly
- SQLite
- Natural Language Processing (NLP)
- Flutter / Dart

## Backend API Prototype

CoCare includes a functional FastAPI backend prototype that connects the AI processing pipeline with the local SQLite database and exposes API endpoints for customer interaction and employee-side monitoring.

The current backend includes:

- Customer chat processing
- Chat log retrieval
- Network alert retrieval
- Dashboard statistics
- AI intent and sentiment processing
- Network issue prediction
- Notification and escalation logic

Further development is required to evolve the backend into a production-grade telecom backend with authentication, authorization, security hardening, scalable deployment, production databases, and real telecom API integrations.

## Current Project Status

CoCare is currently a **functional academic prototype**.

The current version demonstrates the integration of AI-based customer support, bilingual intent classification, sentiment analysis, network issue prediction, customer and employee dashboards, notification and escalation logic, and a functional backend prototype.

The system currently uses academic, public, simulated, and synthetic data for development and evaluation.

CoCare is **not currently connected to live telecom infrastructure, real customer accounts, production billing systems, or live network APIs**.

The trained AI models have been preserved externally in Google Drive due to their large storage requirements, while the source code, training resources, application components, and network prediction model are maintained in this repository.

## Future Vision

The next stage of CoCare aims to evolve the prototype into a secure and scalable telecom platform through:

- Production-grade backend development
- Authentication and authorization
- Scalable database architecture
- Ticketing and complaint management
- Human-agent handoff
- Secure telecom API integration
- Real customer-service data integration
- Real network KPI integration
- AI model validation and retraining using real telecom data
- Production mobile application development
- Cloud deployment
- Monitoring and security hardening
- Controlled pilot with a telecom company

## Potential Telecom Integration

In a real telecom environment, CoCare could be integrated with authorized company systems to support:

- Customer account and subscription information
- Package and balance information
- Billing and payment services
- Customer complaints and support tickets
- Network KPIs and service-quality indicators
- Regional network issue detection
- Employee alerts and escalation workflows
- Human-agent support and case handoff

These integrations would require secure company APIs, appropriate access controls, data governance, and production infrastructure.

## Project Vision

Our long-term goal is to connect:

**Customer Service + Artificial Intelligence + Customer Sentiment + Network Intelligence + Human Agents + Telecom Operations**

CoCare aims to evolve beyond a traditional chatbot into an intelligent platform that supports both telecom customers and employees by combining customer-service intelligence with network-aware AI capabilities.

## Project Status

**Academic Graduation Project – Artificial Intelligence & Robotics**

## Contact

For collaboration, technical evaluation, or pilot opportunities:

**Wasan Alarman**  
Artificial Intelligence & Robotics
