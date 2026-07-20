# 🛠️ Product Listing Generator

Generate structured ecommerce product listings from product information and images using the OpenAI API.

---

> [!TIP]
> This project focuses on clean architecture, modular design and robust error handling while keeping the generation workflow simple and easy to extend.

---

## ✨ Overview

Creating high-quality product descriptions is repetitive and time-consuming.

This project automates that process by combining structured product data with image analysis to generate consistent ecommerce listings.

The application validates each product, prepares the prompt, sends the request to the OpenAI API and stores the generated results as structured JSON.

---

## ⚙️ Workflow

```text
Product Data
      │
      ▼
Validate Input
      │
      ▼
Create Prompt
      │
      ▼
Encode Image
      │
      ▼
OpenAI API
      │
      ▼
Parse Response
      │
      ▼
Save JSON Output
```

---

## 🚀 Features

- AI-generated ecommerce listings
- Image-aware product descriptions
- Modular architecture
- Input validation
- Structured JSON output
- Dedicated API and file error handling

---

## 📂 Project Structure

```text
.
├── images/
├── screenshots/
├── output/
├── product_listing_generator_refactored.py
├── lab_proof.md
├── lab_summary.md
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

- Python
- OpenAI API
- JSON
- python-dotenv

---

## ▶️ Getting Started

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
OPENAI_API_KEY=your_api_key
```

Run the application:

```bash
python product_listing_generator_refactored.py
```

---

## 📸 Example

![Successful Processing](screenshots/example_successful_processing.png)

---

## 💭 Future Ideas

- Batch processing for large catalogues
- Schema validation
- Unit testing
- Web interface
- Structured logging