"""
AI Query Processing Engine for Dumroo Admin Panel
Handles natural language query parsing and converts queries to data operations
Supports Hindi-English mixed queries using LangChain
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

# For now, we'll create a rule-based system since we don't have OpenAI API key
# This can be easily replaced with LangChain + OpenAI later

@dataclass
class QueryIntent:
    """Represents the parsed intent of a user query"""
    action: str  # 'find', 'count', 'list', 'show', 'get'
    entity: str  # 'students', 'homework', 'quiz', 'performance'
    filters: Dict[str, str]  # Column filters
    conditions: List[str]  # Special conditions
    time_range: Optional[Tuple[str, str]] = None
    sort_by: Optional[str] = None
    limit: Optional[int] = None

class NaturalLanguageProcessor:
    """Processes natural language queries and extracts structured information"""
    
    def __init__(self):
        self.hindi_to_english = {
            # Basic Hindi translations
            "kaunse": "which", "kaun": "who", "kitne": "how many", "kya": "what",
            "students": "students", "bachche": "students", "vidyarthi": "students",
            "homework": "homework", "ghar ka kaam": "homework", "assignment": "homework",
            "quiz": "quiz", "test": "quiz", "pariksha": "quiz",
            "submit": "submitted", "jama": "submitted", "diya": "submitted",
            "nahi": "not", "nahin": "not", "kiya": "done", "hai": "is",
            "grade": "grade", "class": "class", "kaksha": "class",
            "pichhla": "last", "pichhe": "last", "week": "week", "hafta": "week",
            "performance": "performance", "pradarshan": "performance",
            "marks": "score", "ank": "score", "number": "score",
            "dikhao": "show", "dekho": "show", "batao": "tell",
            "list": "list", "suchi": "list", "aane": "upcoming", "wale": "upcoming",
            "sabse": "top", "acche": "good", "best": "best", "highest": "highest",
            "kam": "low", "kharab": "poor", "worst": "worst", "lowest": "lowest"
        }
        
        self.query_patterns = {
            # Student-related patterns
            'students_not_submitted': [
                r'(which|kaunse|kaun).*(students|bachche|vidyarthi).*(not|nahi|nahin).*(submit|jama|diya).*(homework|assignment)',
                r'(students|bachche|vidyarthi).*(homework|assignment).*(not|nahi|nahin).*(submit|jama|diya)',
                r'(homework|assignment).*(not|nahi|nahin).*(submit|jama|diya).*(students|bachche|vidyarthi)'
            ],
            'students_by_grade': [
                r'(grade|class|kaksha)\s*(\d+|[A-Z])',
                r'(\d+).*(grade|class|kaksha)',
            ],
            'quiz_performance': [
                r'(quiz|test|pariksha).*(performance|pradarshan|marks|score|ank)',
                r'(performance|pradarshan|marks|score|ank).*(quiz|test|pariksha)',
                r'(show|dikhao|dekho).*(quiz|test|pariksha).*(result|natija)'
            ],
            'upcoming_quizzes': [
                r'(upcoming|aane|wale).*(quiz|test|pariksha)',
                r'(quiz|test|pariksha).*(scheduled|aane|wale)',
                r'(next|agla).*(quiz|test|pariksha)'
            ],
            'performance_data': [
                r'(performance|pradarshan).*(data|jaankaari)',
                r'(show|dikhao|dekho).*(performance|pradarshan)',
                r'(last|pichhla|pichhe).*(week|hafta).*(performance|pradarshan)'
            ],
            'top_performers': [
                r'(top|sabse|acche|best|highest).*(students|bachche|vidyarthi)',
                r'(best|acche|sabse).*(performance|pradarshan)',
                r'(highest|sabse).*(marks|score|ank)'
            ],
            'poor_performers': [
                r'(poor|kharab|worst|lowest|kam).*(students|bachche|vidyarthi)',
                r'(low|kam).*(performance|pradarshan)',
                r'(struggling|mushkil).*(students|bachche|vidyarthi)'
            ]
        }
    
    def translate_query(self, query: str) -> str:
        """Translate Hindi words to English for processing"""
        words = query.lower().split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for translation
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.hindi_to_english:
                translated_words.append(self.hindi_to_english[clean_word])
            else:
                translated_words.append(word)
        
        return ' '.join(translated_words)
    
    def extract_grade_class_info(self, query: str) -> Dict[str, str]:
        """Extract grade and class information from query"""
        filters = {}
        
        # Extract grade information
        grade_patterns = [
            r'grade\s*(\d+)',
            r'class\s*(\d+)',
            r'kaksha\s*(\d+)',
            r'(\d+)(?:th|nd|rd|st)?\s*grade',
            r'(\d+)(?:th|nd|rd|st)?\s*class'
        ]
        
        for pattern in grade_patterns:
            match = re.search(pattern, query.lower())
            if match:
                grade_num = match.group(1)
                filters['grade'] = f"Grade {grade_num}"
                break
        
        # Extract class section
        class_patterns = [
            r'class\s*([A-Da-d])',
            r'section\s*([A-Da-d])',
            r'([A-Da-d])\s*section'
        ]
        
        for pattern in class_patterns:
            match = re.search(pattern, query.lower())
            if match:
                filters['class_section'] = match.group(1).upper()
                break
        
        # Extract region information
        regions = ['north', 'south', 'east', 'west', 'central']
        for region in regions:
            if region in query.lower():
                filters['region'] = region.capitalize()
                break
        
        return filters
    
    def extract_time_range(self, query: str) -> Optional[Tuple[str, str]]:
        """Extract time range from query"""
        today = datetime.now()
        
        if any(word in query.lower() for word in ['last week', 'pichhla hafta', 'pichhe week']):
            end_date = today
            start_date = today - timedelta(days=7)
            return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        if any(word in query.lower() for word in ['this week', 'is hafta', 'current week']):
            # Get current week (Monday to Sunday)
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
            end_date = start_date + timedelta(days=6)
            return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        if any(word in query.lower() for word in ['last month', 'pichhla mahina']):
            end_date = today
            start_date = today - timedelta(days=30)
            return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        return None
    
    def classify_query_intent(self, query: str) -> QueryIntent:
        """Classify the intent of the query"""
        translated_query = self.translate_query(query)
        filters = self.extract_grade_class_info(translated_query)
        time_range = self.extract_time_range(translated_query)
        
        # Default intent
        intent = QueryIntent(
            action='find',
            entity='students',
            filters=filters,
            conditions=[],
            time_range=time_range
        )
        
        # Check for specific patterns
        for intent_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, translated_query.lower()):
                    if intent_type == 'students_not_submitted':
                        intent.action = 'find'
                        intent.entity = 'students'
                        intent.conditions = ['homework_not_submitted']
                    
                    elif intent_type == 'students_by_grade':
                        intent.action = 'list'
                        intent.entity = 'students'
                    
                    elif intent_type == 'quiz_performance':
                        intent.action = 'show'
                        intent.entity = 'quiz_performance'
                    
                    elif intent_type == 'upcoming_quizzes':
                        intent.action = 'list'
                        intent.entity = 'upcoming_quizzes'
                    
                    elif intent_type == 'performance_data':
                        intent.action = 'show'
                        intent.entity = 'performance'
                    
                    elif intent_type == 'top_performers':
                        intent.action = 'find'
                        intent.entity = 'students'
                        intent.conditions = ['top_performers']
                        intent.sort_by = 'quiz_score'
                        intent.limit = 10
                    
                    elif intent_type == 'poor_performers':
                        intent.action = 'find'
                        intent.entity = 'students'
                        intent.conditions = ['poor_performers']
                        intent.sort_by = 'quiz_score'
                        intent.limit = 10
                    
                    break
            
            if intent.conditions or intent.entity != 'students':
                break
        
        return intent
    
    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions based on partial input"""
        suggestions = [
            "Which students haven't submitted their homework?",
            "Kaunse students ne homework submit nahi kiya?",
            "Show me Grade 8 performance data",
            "Grade 8 ki performance data dikhao",
            "List all upcoming quizzes",
            "Aane wale quiz ki list dikhao",
            "Who are the top performing students?",
            "Sabse acche students kaun hain?",
            "Show last week performance data",
            "Pichhle week ki performance dikhao",
            "Which students scored less than 60 in quiz?",
            "Quiz mein 60 se kam marks wale students",
            "Show me all students in Grade 9 Class A",
            "Grade 9 Class A ke sabhi students",
            "List students from North region",
            "North region ke students ki list"
        ]
        
        if not partial_query:
            return suggestions[:8]
        
        # Filter suggestions based on partial query
        partial_lower = partial_query.lower()
        filtered = [s for s in suggestions if partial_lower in s.lower()]
        
        if not filtered:
            # Return general suggestions if no match
            return suggestions[:5]
        
        return filtered[:8]

class QueryProcessor:
    """Main class for processing natural language queries"""
    
    def __init__(self):
        self.nlp = NaturalLanguageProcessor()
        self.last_query_results = None
        self.conversation_context = []
    
    def process_query(self, query: str, username: str = None) -> Dict:
        """Process a natural language query and return structured response"""
        try:
            # Parse the query intent
            intent = self.nlp.classify_query_intent(query)
            
            # Store in conversation context
            self.conversation_context.append({
                'query': query,
                'intent': intent,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 5 queries in context
            if len(self.conversation_context) > 5:
                self.conversation_context = self.conversation_context[-5:]
            
            # Generate response
            response = {
                'status': 'success',
                'intent': {
                    'action': intent.action,
                    'entity': intent.entity,
                    'filters': intent.filters,
                    'conditions': intent.conditions,
                    'time_range': intent.time_range,
                    'sort_by': intent.sort_by,
                    'limit': intent.limit
                },
                'query': query,
                'translated_query': self.nlp.translate_query(query),
                'suggested_data_operation': self._get_data_operation_suggestion(intent),
                'follow_up_questions': self._generate_follow_up_questions(intent),
                'timestamp': datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_data_operation_suggestion(self, intent: QueryIntent) -> Dict:
        """Convert intent to data operation suggestion"""
        operation = {
            'table': 'students_data',
            'operation': 'SELECT',
            'columns': ['student_name', 'grade', 'class_section'],
            'where_conditions': [],
            'order_by': None,
            'limit': intent.limit
        }
        
        # Add filters based on intent
        for key, value in intent.filters.items():
            operation['where_conditions'].append(f"{key} = '{value}'")
        
        # Handle special conditions
        if 'homework_not_submitted' in intent.conditions:
            operation['where_conditions'].append("homework_submitted = 'No'")
            operation['columns'].extend(['homework_assignment', 'submission_date'])
        
        elif 'top_performers' in intent.conditions:
            operation['where_conditions'].append("quiz_score != 'Not Taken'")
            operation['columns'].extend(['quiz_score', 'quiz_topic'])
            operation['order_by'] = 'CAST(quiz_score AS INTEGER) DESC'
        
        elif 'poor_performers' in intent.conditions:
            operation['where_conditions'].append("quiz_score != 'Not Taken'")
            operation['where_conditions'].append("CAST(quiz_score AS INTEGER) < 60")
            operation['columns'].extend(['quiz_score', 'quiz_topic'])
            operation['order_by'] = 'CAST(quiz_score AS INTEGER) ASC'
        
        # Handle different entities
        if intent.entity == 'upcoming_quizzes':
            operation['table'] = 'upcoming_quizzes'
            operation['columns'] = ['subject', 'topic', 'scheduled_date', 'grade', 'class_section']
        
        elif intent.entity == 'quiz_performance':
            operation['columns'].extend(['quiz_score', 'quiz_topic', 'quiz_date'])
            operation['where_conditions'].append("quiz_score != 'Not Taken'")
        
        elif intent.entity == 'performance':
            operation['columns'].extend(['quiz_score', 'attendance_percentage', 'subject'])
        
        # Handle time range
        if intent.time_range:
            start_date, end_date = intent.time_range
            if intent.entity == 'upcoming_quizzes':
                operation['where_conditions'].append(f"scheduled_date BETWEEN '{start_date}' AND '{end_date}'")
            else:
                operation['where_conditions'].append(f"quiz_date BETWEEN '{start_date}' AND '{end_date}'")
        
        return operation
    
    def _generate_follow_up_questions(self, intent: QueryIntent) -> List[str]:
        """Generate relevant follow-up questions"""
        follow_ups = []
        
        if intent.entity == 'students' and 'homework_not_submitted' in intent.conditions:
            follow_ups = [
                "Which subject has the most missing homework?",
                "Show me the submission pattern for the last month",
                "Are there any students who consistently miss homework?",
                "What is the overall homework submission rate?"
            ]
        
        elif intent.entity == 'quiz_performance':
            follow_ups = [
                "Which subject has the highest average scores?",
                "Show me the score distribution",
                "Who are the top 5 performers?",
                "Which topics need more attention?"
            ]
        
        elif intent.entity == 'upcoming_quizzes':
            follow_ups = [
                "Which grade has the most upcoming quizzes?",
                "Show me the quiz schedule for this week",
                "Are students prepared for these quizzes?",
                "What subjects are being tested most?"
            ]
        
        else:
            follow_ups = [
                "Can you show me more details?",
                "What about other grades?",
                "How does this compare to last month?",
                "Are there any trends I should know about?"
            ]
        
        return follow_ups[:3]  # Return top 3 follow-ups
    
    def get_conversation_context(self) -> List[Dict]:
        """Get the current conversation context"""
        return self.conversation_context
    
    def clear_context(self):
        """Clear conversation context"""
        self.conversation_context = []
        self.last_query_results = None

# Initialize the query processor
query_processor = QueryProcessor()

if __name__ == "__main__":
    # Test the query processor
    print("=== DUMROO AI QUERY PROCESSOR TEST ===\n")
    
    test_queries = [
        "Which students haven't submitted their homework?",
        "Kaunse students ne homework submit nahi kiya?",
        "Show me Grade 8 performance data",
        "Grade 8 ki performance dikhao",
        "List upcoming quizzes",
        "Aane wale quiz ki list",
        "Who are the top performing students?",
        "Sabse acche students kaun hain?",
        "Show poor performing students in Grade 9",
        "Grade 9 mein kharab performance wale students"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        result = query_processor.process_query(query)
        print(f"Status: {result['status']}")
        
        if result['status'] == 'success':
            intent = result['intent']
            print(f"Action: {intent['action']}")
            print(f"Entity: {intent['entity']}")
            print(f"Filters: {intent['filters']}")
            print(f"Conditions: {intent['conditions']}")
            print(f"Suggested Operation: {result['suggested_data_operation']['operation']}")
            print(f"Follow-up Questions: {result['follow_up_questions'][:2]}")
        else:
            print(f"Error: {result['error']}")
        
        print("-" * 80)
    
    # Test query suggestions
    print("\n=== QUERY SUGGESTIONS ===")
    suggestions = query_processor.nlp.get_query_suggestions("")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")