<div align="center">

<img src="frontend/assets/images/logo.jpg" alt="StreetLight Logo" width="200"/>

#  STREETLIGHT

### *AI-Powered Civic Reporting Platform with GPS Verification*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.129.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-3.10.8-02569B.svg?style=flat&logo=Flutter&logoColor=white)](https://flutter.dev)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C.svg?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-Academic-blue.svg)](LICENSE)

**Combat fraudulent civic reports using AI-powered image classification and GPS verification**

[Features](#-key-features) • [Demo](#-demo) • [Installation](#-quick-start) • [Architecture](#-system-architecture) • [Team](#-team)

---

</div>

## 🌟 What is StreetLight?

**StreetLight** is an intelligent civic engagement platform that revolutionizes how citizens report infrastructure issues. Using cutting-edge AI and GPS verification technology, we ensure every report is authentic—**preventing fraud and saving government resources**.

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


---

## 🏗️ System Architecture

<div align="center">



</div>




    # 1. Extract GPS from photo EXIF 

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
      <b>Mariam Qadeem</b><br>NO    
    </td>
    <td align="center" width="25%">
      <img src="https://ui-avatars.com/api/?name=Areeba+Tahir&size=100&background=009688&color=fff" width="100" style="border-radius: 50%"/><br>
      <b>Areeba Tahir</b><br>
  
    </td>
    <td align="center" width="25%">
      <img src="https://ui-avatars.com/api/?name=Kinz+ul+Eman&size=100&background=EE4C2C&color=fff" width="100" style="border-radius: 50%"/><br>
      <b>Kinz-ul-Eman</b><br>

    </td>
    <td align="center" width="25%">
      <img src="https://ui-avatars.com/api/?name=Shezonia&size=100&background=3776AB&color=fff" width="100" style="border-radius: 50%"/><br>
      <b>Shezonia</b><br>
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

## 🎓 Academic Context

<div align="center">

**🏛️ Final Year Project (FYP) / Capstone Project**

**Department of Information Technology**  
Faculty of Computing & Information Technology  
**University of the Punjab, Lahore**

*Session: 2022-2026*

</div>

---


## 📄 License

This project is developed for **academic purposes** as part of a university capstone project.

**© 2024 StreetLight Team - Punjab University**

---

## 🙏 Acknowledgments

Special thanks to:

- 🏛️ **Punjab University College of Information Technology (PUCIT)** - For academic support and resources
- 👨‍🏫 **Adeel Nisar** - For exceptional guidance and mentorship
- 🗺️ **OpenStreetMap Community** - For free geocoding and mapping APIs
- 🤖 **PyTorch Community** - For the ResNet18 model and framework
- 🚀 **FastAPI & Flutter Teams** - For amazing frameworks
- 💻 **Open Source Community** - For invaluable tools and libraries

---

## 📞 Contact & Support

<div align="center">

### Get in Touch

📧 **Email:** adeel.nisar@pucit.edu.pk  
🏛️ **Institution:** University of the Punjab, Lahore  
🏢 **Department:** Information Technology (IT-OC)

### Connect With Us

[![GitHub](https://img.shields.io/badge/GitHub-StreetLight-181717?style=for-the-badge&logo=github)](https://github.com/yourusername/streetlight)
[![Documentation](https://img.shields.io/badge/Docs-Read%20More-blue?style=for-the-badge&logo=readthedocs)](docs/)

</div>

---


<div align="center">


[⬆ Back to Top](#-streetlight)

</div>
