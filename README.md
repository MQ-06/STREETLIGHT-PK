<div align="center">

<img src="frontend/assets/images/logo.jpg" alt="StreetLight Logo" width="200"/>

#  STREETLIGHT

### *AI-Powered, Blockchain-Secured Civic Management Platform*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.129.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-3.10.8-02569B.svg?style=flat&logo=Flutter&logoColor=white)](https://flutter.dev)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C.svg?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Solidity](https://img.shields.io/badge/Solidity-0.8+-363636.svg?style=flat&logo=solidity&logoColor=white)](https://soliditylang.org)
[![Ethereum](https://img.shields.io/badge/Ethereum-Blockchain-3C3C3D.svg?style=flat&logo=ethereum&logoColor=white)](https://ethereum.org)
[![License](https://img.shields.io/badge/License-Academic-blue.svg)](LICENSE)

**"No civic hazard should remain in dark"**

[Features](#-key-features) • [Installation](#-quick-start) • [Technology Stack](#-technology-stack) • [Team](#-team)

---

</div>

## 🌟 What is StreetLight?

**StreetLight** is an AI-powered, blockchain-secured civic management platform that bridges the gap between citizens and municipal authorities in Pakistan's rapidly urbanizing cities. Built under the motto *"No civic hazard should remain in dark,"* it transforms how everyday infrastructure problems potholes, garbage accumulation, broken streetlights, sewerage failures are reported, verified, and resolved.

### 🎯 The Challenge We're Solving

In traditional civic reporting systems:

| Problem | Impact | Our Solution |
|---------|--------|--------------|
| 🚫 **Fake Reports** | Wasted resources on non-existent issues | AI classification verifies issue authenticity |
| 📍 **Location Spoofing** | Reports submitted for wrong locations | GPS verification using EXIF + Haversine algorithm |
| 🎭 **Photo Reuse** | Old photos used for new reports | Real-time GPS extraction from photo metadata |
| 💰 **Resource Drain** | Authorities investigate fraudulent claims | Automated fraud detection saves time & money |


## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🛡️ **Anti-Fraud Technology**

- ✅ **GPS Spoofing Detection**  
  Detects location mismatches > 5km

- 🗺️ **EXIF Data Extraction**  
  Extracts embedded GPS from photos

- 📏 **Haversine Distance Calculation**  
  Precise location difference measurement

- 🏛️ **Landmark Cross-Verification**  
  Validates with nearby POIs

- 🎯 **Dynamic Scoring System**  
  +10 bonus for verified, -50 penalty for fraud

- 🔐 **SHA-256 Hashing**  
  Unique hash generated for every report

- ⛓️ **Blockchain Immutability**  
  Hash stored on Ethereum as proof
  
</td>
<td width="50%">

### 🤖 **AI-Powered Classification**

- 🧠 **Deep Learning Model**  
  ResNet18 trained on civic issues

- 🎨 **Multi-Class Detection**  
  Potholes, garbage, broken lights, etc.

- 📊 **Confidence Scoring**  
  Transparent prediction confidence

- ⚠️ **Severity Assessment**  
  Minor, moderate, severe categorization

- 📈 **Continuous Learning**  
  Model improves with new data

</td>
</tr>
<tr>
<td width="50%">

### 📱 **Mobile Experience**

- 📸 **In-App Photo Capture**  
  Auto GPS tagging

- 🗺️ **Interactive Map**  
  Pin exact location

- 📤 **Instant Upload**  
  Fast report submission

- 🔔 **Real-Time Tracking**  
  Monitor report status

- 🔐 **Secure Authentication**  
  JWT-based login system

</td>
<td width="50%">

### 👨‍💼 **Authority Dashboard**

- 📊 **Real-Time Monitoring**  
  Live report feed

- 🚨 **Fraud Alerts**  
  Automatic suspicious report flagging

- 🗺️ **Map Visualization**  
  Geographical issue clustering

- 📈 **Analytics & Insights**  
  Data-driven decision making

- 📋 **Work Order Generation**  
  Streamlined workflow management

</td>
</tr>
</table>

---

## 🚀 Technology Stack

<div align="center">

### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

### Frontend
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)
![Material Design](https://img.shields.io/badge/Material_Design-757575?style=for-the-badge&logo=material-design&logoColor=white)

### AI/ML
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![ResNet](https://img.shields.io/badge/ResNet18-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)

### Blockchain
![Solidity](https://img.shields.io/badge/Solidity-363636?style=for-the-badge&logo=solidity&logoColor=white)
![Ethereum](https://img.shields.io/badge/Ethereum-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white)
![MetaMask](https://img.shields.io/badge/MetaMask-F6851B?style=for-the-badge&logo=metamask&logoColor=white)

### External APIs
![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=for-the-badge&logo=openstreetmap&logoColor=white)
![Nominatim](https://img.shields.io/badge/Nominatim-7EBC6F?style=for-the-badge&logo=openstreetmap&logoColor=white)
![Overpass API](https://img.shields.io/badge/Overpass_API-7EBC6F?style=for-the-badge&logo=openstreetmap&logoColor=white)

</div>

---

## 🚀 Quick Start

### Prerequisites

- 🐍 Python 3.8+
- 📱 Flutter 3.0+
- 🐘 PostgreSQL (optional)
- 📦 Git

### 🔧 Backend Setup (3 minutes)

```bash
# 1️⃣ Clone repository
git clone https://github.com/yourusername/streetlight.git
cd streetlight/backend

# 2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Initialize database
python script/create_tables.py

# 5️⃣ Run server
uvicorn main:app --reload
```

✅ Backend running at `http://localhost:8000`

### 📱 Frontend Setup (2 minutes)

```bash
# 1️⃣ Navigate to frontend
cd ../frontend

# 2️⃣ Get dependencies
flutter pub get

# 3️⃣ Run app
flutter run
```

---

## 👥 Team

<div align="center">

### 👩‍💻 Development Team

<table>
  <tr>
    <td align="center" width="25%">
      <img src="https://ui-avatars.com/api/?name=Mariam+Qadeem&size=100&background=02569B&color=fff" width="100" style="border-radius: 50%"/><br>
      <b>Mariam Qadeem</b>
    </td>
    <td align="center" width="25%">
      <img src="https://ui-avatars.com/api/?name=Areeba+Tahir&size=100&background=009688&color=fff" width="100" style="border-radius: 50%"/><br>
      <b>Areeba Tahir</b>
    </td>
    <td align="center" width="25%">
      <img src="https://ui-avatars.com/api/?name=Kinz+ul+Eman&size=100&background=EE4C2C&color=fff" width="100" style="border-radius: 50%"/><br>
      <b>Kinz-ul-Eman</b>
    </td>
    <td align="center" width="25%">
      <img src="https://ui-avatars.com/api/?name=Shezonia&size=100&background=3776AB&color=fff" width="100" style="border-radius: 50%"/><br>
      <b>Shezonia</b>
    </td>
  </tr>
</table>

### 👨‍🏫 Supervision

**Supervisor:** Adeel Nisar  
**Email:** adeel.nisar@pucit.edu.pk  
**Department:** Information Technology (IT-OC)  
**Institution:** Punjab University College of Information Technology (PUCIT)

</div>

---

<div align="center">


*"No civic hazard should remain in dark"*

[⬆ Back to Top](#-streetlight)

</div>
