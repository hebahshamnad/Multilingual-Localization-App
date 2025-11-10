# 🌍 Multilingual Localization App

The **Multilingual Localization App** is a **serverless, AI-powered web platform** built on **Amazon Web Services (AWS)** that helps brands automatically translate and adapt marketing content for European audiences.  

Using **Generative AI (Amazon Bedrock)** and **Amazon Translate**, the app delivers **context-aware translations** in five languages — **French, Italian, Portuguese, Spanish, and German** — ensuring each message retains its brand tone and cultural relevance.  

The platform allows users to upload **brand-specific context**, so all translations remain consistent, on-brand, and globally effective, powered by a **Python AWS Lambda backend** and fully managed AWS services.

---

## 🚀 Features

- 🌐 **Translate content** into 5 European languages (FR, IT, PT, ES, DE)  
- 🧠 **Context-aware translations** using Amazon Bedrock and Amazon Translate  
- 📂 **Brand context upload** — ensures tone and vocabulary stay relevant to brand identity  
- ⚙️ **Serverless architecture** powered by AWS Lambda (Python), API Gateway, and DynamoDB  
- 🔐 **Secure by design** with Cognito authentication, IAM roles, and KMS encryption  
- 📊 **Scalable & observable** using CloudFront for delivery and CloudWatch for monitoring  


## 🛠️ Tech Stack


## 🛠️ Tech Stack

**AWS Services**
- AWS Lambda  
- Amazon API Gateway  
- Amazon DynamoDB  
- Amazon S3  
- Amazon Translate  
- Amazon Bedrock  
- Amazon Cognito  
- Amazon CloudFront  
- Amazon CloudWatch  

**Languages & Tools**
- Python  
- HTML / CSS / JavaScript  

---

## 📦 How It Works

1. A **brand uploads its context file** (e.g., product descriptions, slogans, or glossary) via the web interface.  
2. The user enters or uploads the **source text** to translate.  
3. The backend (AWS Lambda + Bedrock) processes the text using the **brand context** and **LLMs** to ensure tone and style alignment.  
4. The app translates the content into **five European languages**: French, Italian, Portuguese, Spanish, and German.  
5. Translations are refined, stored in **S3**, and delivered back to the user through the web UI.  
