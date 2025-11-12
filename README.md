# 🎓 Dumroo AI Admin Panel

## Natural Language Querying System with Role-Based Access Control

A sophisticated AI-powered admin panel that allows administrators to ask questions in simple English or Hindi and get instant insights from student data with proper role-based access control.

![Dumroo AI Banner](https://img.shields.io/badge/Dumroo-AI%20Admin%20Panel-blue?style=for-the-badge&logo=graduation-cap)

### 🌟 Features

- **🤖 Natural Language Processing**: Ask questions in English or Hindi
- **🔒 Role-Based Access Control**: Different permission levels for different admin types
- **📊 Interactive Dashboard**: Real-time metrics and visualizations
- **🎯 Smart Query Processing**: AI-powered query understanding and data retrieval
- **📈 Data Visualizations**: Charts and graphs for better insights
- **💬 Conversation History**: Track previous queries and results
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🔄 Follow-up Questions**: AI suggests relevant follow-up queries

### 🏗️ Architecture

```
dumroo-ai-assignment/
├── app.py                 # Main Streamlit application
├── src/
│   ├── rbac.py           # Role-Based Access Control system
│   ├── query_processor.py # Natural language query processing
│   └── data_manager.py   # Data filtering and retrieval
├── data/
│   ├── students_data.csv # Sample student dataset
│   └── upcoming_quizzes.csv # Upcoming quiz data
├── config/
│   └── users.json        # User configuration file
├── generate_data.py      # Data generation script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### 1. Installation

#### Option A: Download and Extract
1. Download the project as ZIP
2. Extract to your desired location
3. Open terminal/command prompt in the project directory

#### Option B: Clone Repository
```bash
git clone <repository-url>
cd dumroo-ai-assignment
```

### 2. Set Up Virtual Environment

**Windows:**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# For PowerShell execution policy issues, use:
# cmd /c "venv\Scripts\activate.bat"
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**If you encounter dependency conflicts, install packages individually:**
```bash
pip install streamlit pandas plotly python-dotenv
pip install langchain-community langchain-core
pip install pydantic requests aiohttp
```

### 4. Generate Sample Data

```bash
python generate_data.py
```

This will create:
- `data/students_data.csv` - Sample student records (248 records)
- `data/upcoming_quizzes.csv` - Upcoming quiz data (54 records)

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 👥 Demo User Accounts

The system comes with pre-configured demo accounts for testing different access levels:

| Username | Password | Access Level | Description |
|----------|----------|--------------|-------------|
| `super_admin` | `admin123` | Super Admin | Full access to all data |
| `north_admin` | `north123` | Region Admin | North region students only |
| `south_admin` | `south123` | Region Admin | South region students only |
| `grade89_admin` | `grade123` | Grade Admin | Grade 8 & 9 students only |
| `classab_admin` | `class123` | Class Admin | Class A & B students only |
| `mathsci_admin` | `subject123` | Subject Admin | Math & Science subjects only |
| `east67_admin` | `combined123` | Combined | East region + Grade 6-7 |

## 🗣️ Query Examples

### English Queries
- "Which students haven't submitted their homework?"
- "Show me Grade 8 performance data"
- "Who are the top performing students?"
- "List all upcoming quizzes"
- "Show poor performing students in Grade 9"
- "What is the homework submission rate?"

### Hindi-English Mixed Queries
- "Kaunse students ne homework submit nahi kiya?"
- "Grade 8 ki performance data dikhao"
- "Sabse acche students kaun hain?"
- "Aane wale quiz ki list dikhao"
- "Grade 9 mein kharab performance wale students"
- "Pichhle week ki performance dikhao"

### Advanced Queries
- "Show me students from North region who scored less than 60"
- "Which subject has the most missing homework?"
- "List students with attendance less than 80%"
- "Show quiz performance for last month"

## 🔒 Role-Based Access Examples

### Super Admin
```python
# Has access to ALL data
- Can see students from all regions
- Can view all grades and classes
- Can access sensitive data (scores, attendance)
- Can export data
```

### Region Admin (North)
```python
# Limited to North region only
Query: "Show all students"
Result: Only shows students from North region
```

### Grade Admin (Grade 8-9)
```python
# Limited to specific grades
Query: "Which students haven't submitted homework?"
Result: Only shows Grade 8 and Grade 9 students
```

### Class Admin (Class A-B)
```python
# Limited to specific classes
Query: "Show performance data"
Result: Only shows students from Class A and Class B
```

## 🛠️ Customization

### Adding New Users

Edit the `src/rbac.py` file to add new users:

```python
new_admin = AdminUser(
    username="new_admin",
    password_hash=self._hash_password("password123"),
    full_name="New Administrator",
    email="new@dumroo.ai",
    permissions=UserPermissions(
        access_level=AccessLevel.REGION_ADMIN,
        regions=["Central"],
        can_view_sensitive_data=True,
        can_export_data=False
    )
)
```

### Adding New Query Types

Extend the `src/query_processor.py` file:

```python
# Add new patterns to query_patterns dictionary
'new_pattern': [
    r'your_regex_pattern_here',
    r'another_pattern'
]
```

### Custom Data Sources

Modify `src/data_manager.py` to connect to your database:

```python
def load_data(self):
    # Replace CSV loading with database connection
    # self.students_df = pd.read_sql("SELECT * FROM students", connection)
    pass
```

## 📊 Data Schema

### Students Data (`students_data.csv`)
| Column | Type | Description |
|--------|------|-------------|
| student_id | int | Unique student identifier |
| student_name | str | Full name of student |
| grade | str | Grade level (Grade 6-10) |
| class_section | str | Class section (A, B, C, D) |
| region | str | Geographic region |
| subject | str | Subject name |
| homework_assignment | str | Assignment description |
| homework_submitted | str | Yes/No submission status |
| submission_date | str | Date of submission |
| quiz_topic | str | Quiz topic |
| quiz_score | str | Quiz score (0-100 or "Not Taken") |
| quiz_date | str | Date of quiz |
| attendance_percentage | int | Attendance percentage |
| last_updated | str | Last update timestamp |

### Upcoming Quizzes (`upcoming_quizzes.csv`)
| Column | Type | Description |
|--------|------|-------------|
| quiz_id | int | Unique quiz identifier |
| grade | str | Grade level |
| class_section | str | Class section |
| subject | str | Subject name |
| topic | str | Quiz topic |
| scheduled_date | str | Scheduled date |
| duration_minutes | int | Quiz duration |
| total_marks | int | Maximum marks |
| created_date | str | Creation date |

## 🔧 Troubleshooting

### Common Issues

1. **PowerShell Execution Policy Error**
   ```powershell
   # Use this instead:
   cmd /c "venv\Scripts\activate.bat && streamlit run app.py"
   ```

2. **Module Import Errors**
   ```bash
   # Make sure you're in the project directory and virtual environment is activated
   python -c "import streamlit; print('OK')"
   ```

3. **Data Loading Issues**
   ```bash
   # Regenerate data if files are missing
   python generate_data.py
   ```

4. **Port Already in Use**
   ```bash
   # Use a different port
   streamlit run app.py --server.port 8502
   ```

### Performance Tips

1. **Large Datasets**: For production, use a proper database instead of CSV files
2. **Caching**: Enable Streamlit caching for better performance
3. **Memory**: Monitor memory usage with large datasets

## 🚀 Deployment

### Local Network Access
```bash
streamlit run app.py --server.address 0.0.0.0
```

### Production Deployment

1. **Streamlit Cloud**: Push to GitHub and deploy on Streamlit Cloud
2. **Heroku**: Use the provided `Procfile`
3. **Docker**: Create a Dockerfile for containerized deployment
4. **AWS/Azure**: Deploy using cloud services

## 🧪 Testing

### Manual Testing
1. Login with different user accounts
2. Try various query types
3. Test role-based access restrictions
4. Verify data visualizations

### Automated Testing
```bash
# Run basic tests
python -m src.rbac           # Test RBAC system
python -m src.query_processor # Test query processing
python -m src.data_manager   # Test data management
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is created for the Dumroo.ai AI Developer Assignment.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with different user accounts
4. Verify data files exist

## 🎯 Future Enhancements

- [ ] Integration with OpenAI API for better NLP
- [ ] Real database connection (PostgreSQL, MySQL)
- [ ] Advanced analytics and reporting
- [ ] Email notifications for low performance
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Advanced data visualization
- [ ] Integration with school management systems

---

**Built with ❤️ for Dumroo.ai** | *Demonstrating AI-powered natural language querying with role-based access control*