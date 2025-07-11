# 📦 Supply Chain Optimization using Time LLM

This is a full-stack web application that helps businesses forecast product demand, manage inventory, track logistics, and get real-time alerts — all through an intuitive dashboard interface.

Built using:
- 🔧 Flask (Python)
- 📊 Prophet (Time-Series Forecasting)
- 🗄 MySQL (Real-time database)
- 📁 HTML/CSS + Jinja2 Templates
- 🕒 Windows Task Scheduler for automation

---


🔗 **Try it on GitHub Codespaces:**  
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=eshani123-bit%2Fsupply-chain-optimization-using-Time-LLM)

---

## 🔑 Features

### ✅ User Authentication
- Role-based login (admin, staff)
- Secure registration & session management

### 📈 Demand Forecasting
- Uses Prophet to predict 7-day demand
- Forecast results are visualized and shown on the home page

### 🗃 Inventory & Logistics Dashboard
- View current stock vs predicted demand
- Shows restock alerts if stock is below safety levels
- Smart logistics optimization table

### 📊 Sales Analytics Dashboard
- Top-selling product
- Sales trend over last 7 days (line chart)
- Sales per product (bar chart)

### 📁 Sales CSV Upload
- Admin can upload daily sales CSV manually
- Auto-upload scheduled daily at *1:00 AM* using *Windows Task Scheduler*

### ⚠ Real-time Alerts
- Inventory alerts when stock falls below reorder level
- Logistics alerts for stock gaps vs predicted demand

---

## 📂 Folder Structure

