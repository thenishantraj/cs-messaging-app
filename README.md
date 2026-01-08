# 💬 Branch CS Messaging Platform

A modern, interactive customer service messaging application built with Streamlit for handling high-volume customer inquiries with smart prioritization.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![SQLite](https://img.shields.io/badge/SQLite-3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Live Demo
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app/)

## 📋 Features

### 🤖 **Smart Message Management**
- **AI-Powered Urgency Detection**: Automatic priority scoring based on keywords
- **Real-time Chat Interface**: Live messaging with customer context
- **Multi-Agent Support**: Concurrent agent collaboration
- **Automated Categorization**: Messages sorted by type (Loan, Payment, Technical, etc.)

### ⚡ **Productivity Tools**
- **Quick Response Templates**: Pre-configured canned responses
- **Advanced Search & Filters**: Real-time message filtering
- **Customer Profile Integration**: Contextual customer information
- **Auto-Refresh**: Live updates without manual refresh

### 🎨 **User Experience**
- **Three-Panel Dashboard**: Message queue, chat, customer info side-by-side
- **Priority Color Coding**: Visual urgency indicators
- **Mobile-Responsive Design**: Works on all devices
- **Slack-Inspired UI**: Familiar chat interface

## 🛠️ Tech Stack

**Frontend:**
- ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
- ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
- ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

**Backend:**
- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge)
- ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

**Database:**
- ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

**Visualization:**
- ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)



## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

```bash
# 1. Clone repository
git clone https://github.com/your-username/branch-cs-messaging.git
cd branch-cs-messaging

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python setup.py

# 5. Run application
streamlit run app.py
