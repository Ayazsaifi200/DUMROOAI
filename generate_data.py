import pandas as pd
import random
from datetime import datetime, timedelta
import csv

# Set random seed for reproducibility
random.seed(42)

# Define data for generating realistic student dataset
indian_names = [
    "Aarav Sharma", "Vivaan Gupta", "Aditya Kumar", "Vihaan Singh", "Arjun Patel",
    "Sai Reddy", "Reyansh Agarwal", "Krishna Joshi", "Ishaan Verma", "Shaurya Yadav",
    "Ananya Sharma", "Diya Gupta", "Saanvi Kumar", "Aadhya Singh", "Kavya Patel",
    "Pihu Reddy", "Myra Agarwal", "Sara Joshi", "Aanya Verma", "Navya Yadav",
    "Aryan Mehta", "Kabir Shah", "Atharv Malhotra", "Rudra Sinha", "Shivansh Kapoor",
    "Avni Bansal", "Kiara Saxena", "Riya Bhardwaj", "Tara Choudhary", "Zara Goyal",
    "Dev Pandey", "Ayaan Tiwari", "Vedant Sharma", "Yash Gupta", "Dhruv Kumar",
    "Isha Singh", "Maya Patel", "Nisha Reddy", "Priya Agarwal", "Sakshi Joshi",
    "Advaith Verma", "Karan Yadav", "Rohan Mehta", "Tanvi Shah", "Urvashi Malhotra",
    "Varun Sinha", "Harsh Kapoor", "Manvi Bansal", "Nidhi Saxena", "Ojas Bhardwaj"
]

grades = ["Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"]
classes = ["A", "B", "C", "D"]
regions = ["North", "South", "East", "West", "Central"]
subjects = ["Mathematics", "Science", "English", "Hindi", "Social Studies"]

# Generate homework assignments
homework_assignments = [
    "Math Chapter 5 Exercises", "Science Lab Report", "English Essay Writing",
    "Hindi Grammar Practice", "History Project", "Geography Map Work",
    "Physics Numerical Problems", "Chemistry Reactions", "Biology Diagrams",
    "Literature Review", "Math Problem Solving", "Science Experiment",
    "English Creative Writing", "Hindi Story Writing", "Social Studies Research"
]

# Generate quiz topics
quiz_topics = [
    "Algebra Basics", "Cell Biology", "Grammar Rules", "Ancient History",
    "Chemical Bonding", "Geometry Theorems", "Plant Biology", "Sentence Formation",
    "Medieval Period", "Periodic Table", "Statistics", "Human Body Systems",
    "Poetry Analysis", "Modern History", "Environmental Science"
]

def generate_student_data():
    students = []
    student_id = 1001
    
    for name in indian_names:
        # Basic student info
        grade = random.choice(grades)
        class_section = random.choice(classes)
        region = random.choice(regions)
        
        # Generate multiple entries for each student (different assignments/quizzes)
        num_entries = random.randint(3, 7)  # Each student has 3-7 records
        
        for _ in range(num_entries):
            # Homework data
            assignment = random.choice(homework_assignments)
            submitted = random.choices([True, False], weights=[75, 25])[0]  # 75% submission rate
            submission_date = None
            
            if submitted:
                # Random submission date in last 30 days
                days_ago = random.randint(1, 30)
                submission_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            # Quiz data
            quiz_topic = random.choice(quiz_topics)
            quiz_score = random.randint(45, 100) if random.random() > 0.1 else None  # 10% haven't taken quiz
            quiz_date = (datetime.now() - timedelta(days=random.randint(1, 45))).strftime("%Y-%m-%d")
            
            # Performance metrics
            attendance_percentage = random.randint(75, 98)
            subject = random.choice(subjects)
            
            student = {
                "student_id": student_id,
                "student_name": name,
                "grade": grade,
                "class_section": class_section,
                "region": region,
                "subject": subject,
                "homework_assignment": assignment,
                "homework_submitted": "Yes" if submitted else "No",
                "submission_date": submission_date if submitted else "Not Submitted",
                "quiz_topic": quiz_topic,
                "quiz_score": quiz_score if quiz_score else "Not Taken",
                "quiz_date": quiz_date,
                "attendance_percentage": attendance_percentage,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            students.append(student)
        
        student_id += 1
    
    return students

def create_upcoming_quizzes():
    upcoming_quizzes = []
    quiz_id = 5001
    
    for grade in grades:
        for class_section in classes:
            # Generate 2-3 upcoming quizzes per class
            num_quizzes = random.randint(2, 3)
            for _ in range(num_quizzes):
                days_ahead = random.randint(1, 14)  # Quiz in next 2 weeks
                quiz_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                
                quiz = {
                    "quiz_id": quiz_id,
                    "grade": grade,
                    "class_section": class_section,
                    "subject": random.choice(subjects),
                    "topic": random.choice(quiz_topics),
                    "scheduled_date": quiz_date,
                    "duration_minutes": random.choice([30, 45, 60]),
                    "total_marks": random.choice([20, 25, 30, 50]),
                    "created_date": datetime.now().strftime("%Y-%m-%d")
                }
                
                upcoming_quizzes.append(quiz)
                quiz_id += 1
    
    return upcoming_quizzes

# Generate the datasets
print("Generating student data...")
student_data = generate_student_data()
upcoming_quiz_data = create_upcoming_quizzes()

# Create DataFrames
df_students = pd.DataFrame(student_data)
df_upcoming_quizzes = pd.DataFrame(upcoming_quiz_data)

# Save to CSV files
df_students.to_csv('data/students_data.csv', index=False)
df_upcoming_quizzes.to_csv('data/upcoming_quizzes.csv', index=False)

print(f"Generated {len(student_data)} student records")
print(f"Generated {len(upcoming_quiz_data)} upcoming quiz records")
print("Data saved to:")
print("- data/students_data.csv")
print("- data/upcoming_quizzes.csv")

# Display sample data
print("\nSample Student Data:")
print(df_students.head())
print("\nSample Upcoming Quizzes:")
print(df_upcoming_quizzes.head())

# Generate summary statistics
print("\n=== DATA SUMMARY ===")
print(f"Total students: {df_students['student_name'].nunique()}")
print(f"Total records: {len(df_students)}")
print("\nGrade distribution:")
print(df_students['grade'].value_counts())
print("\nRegion distribution:")
print(df_students['region'].value_counts())
print(f"\nHomework submission rate: {(df_students['homework_submitted'] == 'Yes').mean():.1%}")
print(f"Average quiz score: {df_students[df_students['quiz_score'] != 'Not Taken']['quiz_score'].astype(float).mean():.1f}")