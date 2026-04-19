import pandas as pd
import random

def calculate_risk(df):
    col_mapping = {
        'Name': 'name', 'Attendance': 'attendance', 'Internal_Marks': 'internal_marks',
        'Assignments_Pending': 'missing_assignments', 'ID': 'id', 'Subject': 'subject',
        'Department': 'department'
    }
    df = df.rename(columns=col_mapping)
    
    if 'id' not in df.columns:
        df['id'] = [f"U{i:03d}" for i in range(1, len(df)+1)]
    if 'subject' not in df.columns:
        df['subject'] = 'General'
    if 'department' not in df.columns:
        df['department'] = [random.choice(['Computer', 'Civil', 'Mechanical', 'Electrical']) for _ in range(len(df))]
        
    student_records = []
    
    for _, row in df.iterrows():
        record = row.to_dict()
        
        # Need to optimize this part later - parsing might fail on weird inputs
        try: 
            att = float(record.get('attendance', 100))
        except: 
            att = 100
        try: 
            marks = float(record.get('internal_marks', 100))
        except: 
            marks = 100
        try: 
            miss_assign = float(record.get('missing_assignments', 0))
        except: 
            miss_assign = 0
            
        norm_att = max(0, min(100, (100 - att) / 100))
        norm_marks = max(0, min(100, (100 - marks) / 100))
        norm_assign = max(0, min(10, miss_assign / 10))
        
        score = (norm_att * 0.5) + (norm_marks * 0.4) + (norm_assign * 0.1)
        
        if score > 0.5:
            level = "Critical"
        elif score > 0.25:
            level = "Warning"
        else:
            level = "Safe"
            
        reasons = []
        if att < 75: 
            reasons.append("Low Attendance")
        if marks < 60: 
            reasons.append("Low Internal Marks")
        if miss_assign > 3: 
            reasons.append("High Missing Assignments")
        
        if not reasons:
            reasons.append("On Track - Keep it up!")
            
        record.update({
            "risk_score": round(score * 100, 2),
            "risk_level": level,
            "insights": ", ".join(reasons)
        })
        student_records.append(record)
        
    final_data = pd.DataFrame(student_records)
    return final_data

def load_initial_dataset():
    random.seed(42)
    
    base_students = [
        {"id": "S001", "name": "Rahul", "subject": "Maths", "department": "Computer"},
        {"id": "S002", "name": "Priya", "subject": "Physics", "department": "Civil"},
        {"id": "S003", "name": "Amit", "subject": "Maths", "department": "Mechanical"},
        {"id": "S004", "name": "Sneha", "subject": "Physics", "department": "Computer"},
        {"id": "S005", "name": "Vikram", "subject": "Maths", "department": "Electrical"}
    ]
    
    raw_data = []
    
    for s in base_students:
        # Handling edge case for specific demo data requirements
        if s["name"] == "Rahul":
            s["attendance"] = random.randint(40, 60)
            s["internal_marks"] = random.randint(30, 45)
            s["missing_assignments"] = random.randint(5, 10)
        elif s["name"] in ["Amit", "Sneha"]:
            s["attendance"] = random.randint(85, 100)
            s["internal_marks"] = random.randint(75, 95)
            s["missing_assignments"] = random.randint(0, 1)
        else:
            s["attendance"] = random.randint(65, 80)
            s["internal_marks"] = random.randint(55, 70)
            s["missing_assignments"] = random.randint(2, 4)
            
        raw_data.append(s)
        
    df = pd.DataFrame(raw_data)
    return calculate_risk(df)

def fetch_performance_history(student_id):
    weeks = ['Week 1', 'Week 2', 'Week 3 (Intervention)', 'Week 4', 'Week 5']
    
    pre_m = [random.randint(30, 50), random.randint(35, 55), random.randint(40, 60)]
    post_m = [random.randint(65, 80), random.randint(75, 95)]
    
    pre_a = [random.randint(40, 60), random.randint(45, 65), random.randint(50, 70)]
    post_a = [random.randint(75, 90), random.randint(85, 100)]
    
    return pd.DataFrame({
        'Week': weeks,
        'Marks (%)': pre_m + post_m,
        'Attendance (%)': pre_a + post_a
    })
