#  Price Comparison Bot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Playwright](https://img.shields.io/badge/Playwright-Async-green)
![Flask](https://img.shields.io/badge/Flask-2.3%2B-cyan)
![OOP](https://img.shields.io/badge/Code%20Style-OOP-orange)
![Status](https://img.shields.io/badge/Status-Active-success)


A Python automation tool that fetches the **price**, **rating**, and **product link** for any electronic products from **4 major e-commerce websites** — **Amazon**, **Flipkart**, **Reliance Digital**, and **Croma** — allowing quick **side-by-side comparison** to find the best deals.

---

##  Features
-  Scrapes product **price**, **rating**, and **link** from multiple sites
-  Uses **Playwright Async** for fast, reliable browser automation
-  **Flask**-based web interface to make the bot more user friendly
-  **Fuzzy matching** to select the best search result
-  **Regex-powered** data cleaning and extraction
-  Side-by-side comparison for smarter buying decisions

---

##  Tools Used
- **Python**
- **Object-Oriented Programming (OOP)**
- **Playwright (Async)**
- **Flask**
- **RapidFuzz**
- **Regular Expressions (re)**

---

##  Supported Websites
- Amazon
- Flipkart
- Reliance Digital
- Croma
> **Note:** Planning to add more e-commerce websites

---

##  Example Output

```text
Best match from Amazon (Score: 100.0)
Name: Samsung Galaxy S23 FE 5G (Graphite 128 GB Storage) (8 GB RAM)
Price: ₹38,999
Rating: 4.1
Link: https://www.amazon.in/SAMSUNG-Galaxy-S23-Graphite-Storage/dp/B0CJXQX3MB

--------------------------------------------------

Best match from Flipkart (Score: 100.0)
Name: Samsung Galaxy S23 5G (Cream, 256 GB)
Price: ₹53,990
Rating: 4.6
Link: https://www.flipkart.com/samsung-galaxy-s23-5g-cream-256-gb
```

---

## Installation & Usage
- Clone the repository

```text
git clone https://github.com/Govindshari/Price-Bot.git
cd Price-Bot
```

- Create virtual environment & install dependencies

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the bot

```
python main.py
```

## Note
- Use your own User_agent, locale etc in the scraping file(Amazon, Flipkart, Croma, Reliance_Digital)
  
## Author
- Govind H S





