"""
Data Filtering and Retrieval System for Dumroo AI Admin Panel
Handles data access with role-based filtering and query execution
"""

import pandas as pd
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import os
import json

from .rbac import rbac, AccessLevel
from .query_processor import QueryIntent, query_processor

class DataManager:
    """Main data management class with role-based access control"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.students_file = os.path.join(data_dir, "students_data.csv")
        self.quizzes_file = os.path.join(data_dir, "upcoming_quizzes.csv")
        
        # Load data
        self.students_df = None
        self.quizzes_df = None
        self.load_data()
    
    def load_data(self):
        """Load data from CSV files"""
        try:
            if os.path.exists(self.students_file):
                self.students_df = pd.read_csv(self.students_file)
            
            if os.path.exists(self.quizzes_file):
                self.quizzes_df = pd.read_csv(self.quizzes_file)
                
        except Exception as e:
            print(f"Error loading data: {e}")
            # Create empty dataframes if files don't exist
            self.students_df = pd.DataFrame()
            self.quizzes_df = pd.DataFrame()
    
    def reload_data(self):
        """Reload data from files"""
        self.load_data()
    
    def get_user_filtered_data(self, username: str, data_type: str = "students") -> pd.DataFrame:
        """Get data filtered according to user permissions"""
        permissions = rbac.get_user_permissions(username)
        if not permissions:
            return pd.DataFrame()  # Return empty if user not found
        
        # Get the appropriate dataset
        if data_type == "students":
            df = self.students_df.copy() if self.students_df is not None else pd.DataFrame()
        elif data_type == "quizzes":
            df = self.quizzes_df.copy() if self.quizzes_df is not None else pd.DataFrame()
        else:
            return pd.DataFrame()
        
        if df.empty:
            return df
        
        # Super admin gets all data
        if permissions.access_level == AccessLevel.SUPER_ADMIN:
            return df
        
        # Apply filters based on user permissions
        mask = pd.Series([True] * len(df))
        
        # Region filter
        if permissions.regions and 'region' in df.columns:
            mask = mask & df['region'].isin(permissions.regions)
        
        # Grade filter
        if permissions.grades and 'grade' in df.columns:
            mask = mask & df['grade'].isin(permissions.grades)
        
        # Class filter
        if permissions.classes and 'class_section' in df.columns:
            mask = mask & df['class_section'].isin(permissions.classes)
        
        # Subject filter
        if permissions.subjects and 'subject' in df.columns:
            mask = mask & df['subject'].isin(permissions.subjects)
        
        return df[mask]
    
    def execute_query(self, username: str, query_text: str) -> Dict[str, Any]:
        """Execute a natural language query with user permissions"""
        try:
            # Process the natural language query
            query_result = query_processor.process_query(query_text, username)
            
            if query_result['status'] != 'success':
                return query_result
            
            intent = query_result['intent']
            
            # Get user-filtered data
            if intent['entity'] in ['students', 'quiz_performance', 'performance']:
                df = self.get_user_filtered_data(username, "students")
            elif intent['entity'] == 'upcoming_quizzes':
                df = self.get_user_filtered_data(username, "quizzes")
            else:
                df = self.get_user_filtered_data(username, "students")
            
            if df.empty:
                return {
                    'status': 'success',
                    'data': [],
                    'message': 'No data available for your access level.',
                    'query_info': query_result
                }
            
            # Apply query-specific filters
            filtered_df = self._apply_query_filters(df, intent)
            
            # Format and return results
            result_data = self._format_query_results(filtered_df, intent, username)
            
            return {
                'status': 'success',
                'data': result_data['data'],
                'summary': result_data['summary'],
                'visualization_data': result_data.get('visualization_data', {}),
                'message': result_data['message'],
                'query_info': query_result,
                'total_records': len(filtered_df)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'query': query_text,
                'timestamp': datetime.now().isoformat()
            }
    
    def _apply_query_filters(self, df: pd.DataFrame, intent: Dict) -> pd.DataFrame:
        """Apply filters based on query intent"""
        filtered_df = df.copy()
        
        # Apply basic filters from intent
        for key, value in intent['filters'].items():
            if key in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[key] == value]
        
        # Apply special conditions
        for condition in intent['conditions']:
            if condition == 'homework_not_submitted':
                filtered_df = filtered_df[filtered_df['homework_submitted'] == 'No']
            
            elif condition == 'top_performers':
                # Filter out students who haven't taken quiz
                filtered_df = filtered_df[filtered_df['quiz_score'] != 'Not Taken']
                # Convert quiz_score to numeric and sort
                filtered_df['quiz_score_numeric'] = pd.to_numeric(filtered_df['quiz_score'], errors='coerce')
                filtered_df = filtered_df.dropna(subset=['quiz_score_numeric'])
                filtered_df = filtered_df.nlargest(intent.get('limit', 10), 'quiz_score_numeric')
            
            elif condition == 'poor_performers':
                # Filter out students who haven't taken quiz and score < 60
                filtered_df = filtered_df[filtered_df['quiz_score'] != 'Not Taken']
                filtered_df['quiz_score_numeric'] = pd.to_numeric(filtered_df['quiz_score'], errors='coerce')
                filtered_df = filtered_df.dropna(subset=['quiz_score_numeric'])
                filtered_df = filtered_df[filtered_df['quiz_score_numeric'] < 60]
                if intent.get('limit'):
                    filtered_df = filtered_df.nsmallest(intent['limit'], 'quiz_score_numeric')
        
        # Apply time range filters
        if intent.get('time_range'):
            start_date, end_date = intent['time_range']
            date_column = 'quiz_date' if 'quiz_date' in filtered_df.columns else 'submission_date'
            if date_column in filtered_df.columns:
                # Convert date column to datetime
                filtered_df[date_column] = pd.to_datetime(filtered_df[date_column], errors='coerce')
                mask = (filtered_df[date_column] >= start_date) & (filtered_df[date_column] <= end_date)
                filtered_df = filtered_df[mask]
        
        return filtered_df
    
    def _format_query_results(self, df: pd.DataFrame, intent: Dict, username: str) -> Dict:
        """Format query results for display"""
        permissions = rbac.get_user_permissions(username)
        
        if df.empty:
            return {
                'data': [],
                'summary': 'No records found matching your query.',
                'message': 'Try adjusting your search criteria or check your access permissions.'
            }
        
        # Select relevant columns based on intent
        display_columns = self._get_display_columns(intent, df.columns, permissions)
        display_df = df[display_columns].copy()
        
        # Generate summary statistics
        summary = self._generate_summary(df, intent)
        
        # Generate visualization data
        viz_data = self._generate_visualization_data(df, intent)
        
        # Convert to records for JSON serialization
        records = display_df.to_dict('records')
        
        # Limit results if needed
        if intent.get('limit') and len(records) > intent['limit']:
            records = records[:intent['limit']]
        
        return {
            'data': records,
            'summary': summary,
            'visualization_data': viz_data,
            'message': f"Found {len(records)} records matching your query."
        }
    
    def _get_display_columns(self, intent: Dict, available_columns: List, permissions) -> List[str]:
        """Determine which columns to display based on intent and permissions"""
        base_columns = ['student_name', 'grade', 'class_section']
        
        if intent['entity'] == 'students':
            if 'homework_not_submitted' in intent['conditions']:
                additional = ['homework_assignment', 'submission_date', 'subject']
            elif 'top_performers' in intent['conditions'] or 'poor_performers' in intent['conditions']:
                additional = ['quiz_score', 'quiz_topic', 'quiz_date']
            else:
                additional = ['region', 'attendance_percentage']
            
        elif intent['entity'] == 'quiz_performance':
            additional = ['quiz_score', 'quiz_topic', 'quiz_date', 'subject']
            
        elif intent['entity'] == 'performance':
            additional = ['quiz_score', 'attendance_percentage', 'subject', 'homework_submitted']
            
        elif intent['entity'] == 'upcoming_quizzes':
            return ['subject', 'topic', 'scheduled_date', 'grade', 'class_section', 'duration_minutes', 'total_marks']
        
        else:
            additional = ['subject', 'homework_submitted']
        
        # Combine and filter based on available columns
        all_columns = base_columns + additional
        display_columns = [col for col in all_columns if col in available_columns]
        
        # Remove sensitive columns if user doesn't have permission
        if not permissions.can_view_sensitive_data:
            sensitive_columns = ['attendance_percentage', 'quiz_score']
            display_columns = [col for col in display_columns if col not in sensitive_columns]
        
        return display_columns
    
    def _generate_summary(self, df: pd.DataFrame, intent: Dict) -> str:
        """Generate a summary of the query results"""
        if df.empty:
            return "No data found."
        
        total_records = len(df)
        summary_parts = [f"Total records: {total_records}"]
        
        # Add specific summaries based on intent
        if 'homework_not_submitted' in intent['conditions']:
            if 'grade' in df.columns:
                grade_counts = df['grade'].value_counts()
                summary_parts.append(f"Grade breakdown: {dict(grade_counts)}")
            
            if 'subject' in df.columns:
                subject_counts = df['subject'].value_counts()
                top_subject = subject_counts.index[0] if not subject_counts.empty else "N/A"
                summary_parts.append(f"Most affected subject: {top_subject} ({subject_counts.iloc[0]} students)")
        
        elif 'top_performers' in intent['conditions']:
            if 'quiz_score_numeric' in df.columns:
                avg_score = df['quiz_score_numeric'].mean()
                max_score = df['quiz_score_numeric'].max()
                summary_parts.append(f"Average score: {avg_score:.1f}, Highest score: {max_score}")
        
        elif 'poor_performers' in intent['conditions']:
            if 'quiz_score_numeric' in df.columns:
                avg_score = df['quiz_score_numeric'].mean()
                min_score = df['quiz_score_numeric'].min()
                summary_parts.append(f"Average score: {avg_score:.1f}, Lowest score: {min_score}")
        
        elif intent['entity'] == 'upcoming_quizzes':
            if 'scheduled_date' in df.columns:
                # Count quizzes by date
                df['scheduled_date'] = pd.to_datetime(df['scheduled_date'])
                upcoming_week = df[df['scheduled_date'] <= (datetime.now() + timedelta(days=7))]
                summary_parts.append(f"Quizzes in next 7 days: {len(upcoming_week)}")
        
        # Add grade/class distribution if available
        if 'grade' in df.columns and len(df['grade'].unique()) > 1:
            grade_dist = df['grade'].value_counts().to_dict()
            summary_parts.append(f"Grade distribution: {grade_dist}")
        
        return " | ".join(summary_parts)
    
    def _generate_visualization_data(self, df: pd.DataFrame, intent: Dict) -> Dict:
        """Generate data for visualizations"""
        viz_data = {}
        
        if df.empty:
            return viz_data
        
        try:
            # Grade distribution
            if 'grade' in df.columns:
                grade_counts = df['grade'].value_counts().to_dict()
                viz_data['grade_distribution'] = {
                    'labels': list(grade_counts.keys()),
                    'values': list(grade_counts.values()),
                    'type': 'bar'
                }
            
            # Class distribution
            if 'class_section' in df.columns:
                class_counts = df['class_section'].value_counts().to_dict()
                viz_data['class_distribution'] = {
                    'labels': list(class_counts.keys()),
                    'values': list(class_counts.values()),
                    'type': 'pie'
                }
            
            # Quiz score distribution (for performance queries)
            if 'quiz_score' in df.columns and intent['entity'] in ['quiz_performance', 'performance']:
                numeric_scores = pd.to_numeric(df['quiz_score'], errors='coerce').dropna()
                if not numeric_scores.empty:
                    # Create score ranges
                    bins = [0, 40, 60, 80, 100]
                    labels = ['Below 40', '40-60', '60-80', '80-100']
                    score_ranges = pd.cut(numeric_scores, bins=bins, labels=labels, include_lowest=True)
                    range_counts = score_ranges.value_counts().to_dict()
                    
                    viz_data['score_distribution'] = {
                        'labels': list(range_counts.keys()),
                        'values': list(range_counts.values()),
                        'type': 'bar'
                    }
            
            # Subject distribution
            if 'subject' in df.columns:
                subject_counts = df['subject'].value_counts().to_dict()
                viz_data['subject_distribution'] = {
                    'labels': list(subject_counts.keys()),
                    'values': list(subject_counts.values()),
                    'type': 'horizontal_bar'
                }
                
        except Exception as e:
            print(f"Error generating visualization data: {e}")
        
        return viz_data
    
    def get_dashboard_data(self, username: str) -> Dict[str, Any]:
        """Get dashboard overview data for the user"""
        try:
            # Get user-filtered student data
            students_df = self.get_user_filtered_data(username, "students")
            quizzes_df = self.get_user_filtered_data(username, "quizzes")
            
            if students_df.empty:
                return {
                    'status': 'success',
                    'data': {
                        'total_students': 0,
                        'total_assignments': 0,
                        'pending_submissions': 0,
                        'upcoming_quizzes': 0,
                        'message': 'No data available for your access level.'
                    }
                }
            
            # Calculate key metrics
            total_students = students_df['student_name'].nunique()
            total_assignments = len(students_df)
            pending_submissions = len(students_df[students_df['homework_submitted'] == 'No'])
            upcoming_quizzes = len(quizzes_df) if not quizzes_df.empty else 0
            
            # Calculate submission rate
            submission_rate = ((total_assignments - pending_submissions) / total_assignments * 100) if total_assignments > 0 else 0
            
            # Quiz performance stats
            quiz_scores = pd.to_numeric(students_df[students_df['quiz_score'] != 'Not Taken']['quiz_score'], errors='coerce').dropna()
            avg_quiz_score = quiz_scores.mean() if not quiz_scores.empty else 0
            
            # Recent activity (last 7 days)
            recent_submissions = 0
            if 'submission_date' in students_df.columns:
                recent_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                students_df['submission_date'] = pd.to_datetime(students_df['submission_date'], errors='coerce')
                recent_submissions = len(students_df[students_df['submission_date'] >= recent_date])
            
            return {
                'status': 'success',
                'data': {
                    'total_students': total_students,
                    'total_assignments': total_assignments,
                    'pending_submissions': pending_submissions,
                    'submission_rate': round(submission_rate, 1),
                    'upcoming_quizzes': upcoming_quizzes,
                    'avg_quiz_score': round(avg_quiz_score, 1),
                    'recent_submissions': recent_submissions,
                    'grade_distribution': students_df['grade'].value_counts().to_dict() if 'grade' in students_df.columns else {},
                    'subject_distribution': students_df['subject'].value_counts().to_dict() if 'subject' in students_df.columns else {}
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Initialize the data manager
data_manager = DataManager()

if __name__ == "__main__":
    # Test the data manager
    print("=== DUMROO AI DATA MANAGER TEST ===\n")
    
    # Test with different users
    test_users = ["super_admin", "north_admin", "grade89_admin", "classab_admin"]
    test_queries = [
        "Which students haven't submitted their homework?",
        "Show me Grade 8 performance data",
        "Who are the top performing students?",
        "List upcoming quizzes"
    ]
    
    for username in test_users:
        print(f"\n--- Testing with user: {username} ---")
        
        # Test dashboard data
        dashboard = data_manager.get_dashboard_data(username)
        if dashboard['status'] == 'success':
            data = dashboard['data']
            print(f"Dashboard: {data['total_students']} students, {data['pending_submissions']} pending submissions")
        
        # Test a sample query
        query = test_queries[0]  # Test homework submission query
        result = data_manager.execute_query(username, query)
        
        if result['status'] == 'success':
            print(f"Query '{query}': Found {result['total_records']} records")
            print(f"Summary: {result['summary']}")
        else:
            print(f"Query failed: {result.get('error', 'Unknown error')}")
        
        print("-" * 60)