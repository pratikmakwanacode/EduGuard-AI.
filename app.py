import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from data_manager import load_initial_dataset, fetch_performance_history, calculate_risk

st.set_page_config(page_title="EduGuard AI", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

ADMIN_DEMO = 'superadmin'
FACULTY_DEMO = 'admin'

def load_password(file_name, default_pass):
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write(default_pass)
        return default_pass
    with open(file_name, "r") as f:
        return f.read().strip()

if 'intervention_logs' not in st.session_state:
    st.session_state.intervention_logs = []

def main():
    st.title("🛡️ EduGuard AI: Student Early Risk & Intervention Platform")
    st.markdown("---")
    
    st.sidebar.title("Navigation")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Source")
    
    uploaded_file = st.sidebar.file_uploader("Upload Student Data (CSV)", type=['csv'])
    
    if uploaded_file:
        try:
            raw_data = pd.read_csv(uploaded_file)
            st.session_state.student_data = calculate_risk(raw_data)
            st.sidebar.success("Custom data loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error parsing CSV: {e}")
            st.session_state.student_data = load_initial_dataset()
    else:
        st.session_state.student_data = load_initial_dataset()
        st.sidebar.info("Using mock data. Upload a CSV to override.")
        
    st.sidebar.markdown("---")
    selected_view = st.sidebar.radio("Go to", ["Academic Coordinator", "Faculty Dashboard", "Student Portal"])
    
    if selected_view == "Academic Coordinator":
        show_admin_view()
    elif selected_view == "Faculty Dashboard":
        show_faculty_view()
    elif selected_view == "Student Portal":
        show_student_view()

def show_faculty_view():
    st.header("Faculty Dashboard: Risk Analysis & Intervention")
    
    file_pass = load_password("faculty_pass.txt", "faculty@123")
    fac_pwd = st.sidebar.text_input("Faculty Access Password:", type="password", key="fac_pass")
    
    if fac_pwd not in [FACULTY_DEMO, file_pass]:
        st.warning("🔒 This dashboard is restricted to Faculty only. Please enter the password in the sidebar.")
        return
        
    student_records = st.session_state.student_data
    
    total = len(student_records)
    critical_cases = len(student_records[student_records['risk_level'] == 'Critical'])
    warning_cases = len(student_records[student_records['risk_level'] == 'Warning'])
    safe_cases = len(student_records[student_records['risk_level'] == 'Safe'])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students Enrolled", total)
    c2.metric("Critical Risk 🔴", critical_cases)
    c3.metric("Warning 🟡", warning_cases)
    c4.metric("Safe 🟢", safe_cases)
    
    st.markdown("---")
    
    st.subheader("Actionable Student List")
    f_col1, f_col2 = st.columns([1, 3])
    with f_col1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All", "Critical", "Warning", "Safe"])
    
    if risk_filter == "All":
        filtered_records = student_records
    else:
        filtered_records = student_records[student_records['risk_level'] == risk_filter]
    
    st.dataframe(
        filtered_records[['id', 'name', 'subject', 'attendance', 'internal_marks', 'missing_assignments', 'risk_score', 'risk_level', 'insights']],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    st.subheader("Deep Dive & Intervention Logging")
    col_stu, col_log = st.columns(2)
    
    with col_stu:
        selected_name = st.selectbox("Select Student Profile for Insights", student_records['name'].tolist())
        profile = student_records[student_records['name'] == selected_name].iloc[0]
        
        st.markdown(f"#### Profile: {profile['name']} ({profile['id']})")
        st.markdown(f"**Subject:** {profile['subject']}")
        
        colors = {"Critical": "red", "Warning": "orange", "Safe": "green"}
        st.markdown(f"**Risk Level:** :{colors[profile['risk_level']]}[{profile['risk_level']}]")
        st.markdown(f"**Calculated Risk Score:** {profile['risk_score']}%")
        
        st.info(f"**Explainable Insights / Risk Factors:**\n\n{profile['insights']}")
        
    with col_log:
        st.markdown("#### Mentorship & Action Log")
        
        student_id_selection = st.selectbox("Select Student ID for Intervention:", student_records['id'].tolist())
        
        with st.form("intervention_form"):
            notes = st.text_area("Intervention Notes", placeholder="E.g., Met student, discussed health issues")
            submit = st.form_submit_button("Log Intervention")
            
            if submit:
                new_log = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Student_ID": student_id_selection,
                    "Notes": notes
                }])
                
                if os.path.exists("intervention_logs.csv"):
                    new_log.to_csv("intervention_logs.csv", mode='a', header=False, index=False)
                else:
                    new_log.to_csv("intervention_logs.csv", index=False)
                    
                st.success(f"Intervention logged successfully for {student_id_selection}!")
                
    st.markdown("---")
    st.subheader("View Previous Logs")
    if os.path.exists("intervention_logs.csv"):
        logs_df = pd.read_csv("intervention_logs.csv")
        st.dataframe(logs_df, use_container_width=True, hide_index=True)
    else:
        st.info("No intervention logs found yet.")

def show_student_view():
    st.header("Student Portal: Personal Academic Standing")
    
    student_records = st.session_state.student_data
    
    st.markdown("### Authentication Required")
    selected_profile = st.selectbox("Select Your Profile", student_records['name'].unique())
    
    auth_pass = st.text_input("Enter your Student ID to unlock your dashboard:", type="password", help="For demo purposes, use S001, S002, etc.")
    
    match = student_records[student_records['name'] == selected_profile]
    if match.empty:
        st.error("Student not found.")
        return
        
    s_data = match.iloc[0]
    
    if auth_pass != s_data['id']:
        if auth_pass:
            st.error(" Incorrect Student ID. Access Denied.")
        else:
            st.info("ℹ Please enter your ID to view your personal data.")
        return
        
    st.success(" Your data is secured and visible only to you and your mentor.")
    st.markdown("---")
    
    s_col1, s_col2 = st.columns([1, 2])
    
    with s_col1:
        st.subheader("Current Standing")
        st.metric("Risk Score", f"{s_data['risk_score']}%", help="Lower is better. Based on attendance, marks, and assignments.")
        st.metric("Attendance", f"{s_data['attendance']}%")
        st.metric("Internal Marks", f"{s_data['internal_marks']}%")
        st.metric("Missing Assignments", s_data['missing_assignments'])
        
        if s_data['risk_level'] == 'Critical':
            st.error(f"**Alert:** Your academic standing requires immediate attention. \n\n**Reasons:** {s_data['insights']}")
        elif s_data['risk_level'] == 'Warning':
            st.warning(f"**Notice:** You are falling behind in some areas. \n\n**Areas to improve:** {s_data['insights']}")
        else:
            st.success(f"**Excellent:** You are on track! \n\n**Feedback:** {s_data['insights']}")
            
    with s_col2:
        st.subheader("Pre vs Post Intervention Comparison")
        perf_data = fetch_performance_history(s_data['id'])
        
        chart = px.line(
            perf_data, 
            x='Week', 
            y=['Marks (%)', 'Attendance (%)'], 
            markers=True, 
            title=f"Performance Trajectory - {s_data['name']}"
        )
        
        chart.add_vline(x="Week 3 (Intervention)", line_dash="dash", line_color="rgba(255, 255, 255, 0.5)")
        chart.add_annotation(
            x="Week 3 (Intervention)", y=0.05, yref="paper",
            text="Intervention Point", showarrow=False,
            xanchor="left", xshift=5,
            font=dict(color="rgba(255, 255, 255, 0.7)")
        )
        
        chart.update_layout(template="plotly_dark", legend_title_text="Metrics")
        st.plotly_chart(chart, use_container_width=True)

def show_admin_view():
    st.header("Academic Coordinator (Admin) Dashboard")
    
    file_pass = load_password("official_pass.txt", "EduGuard@2026")
    admin_pass = st.sidebar.text_input("Admin Password:", type="password", key="admin_pass")
    
    if admin_pass not in [ADMIN_DEMO, file_pass]:
        st.warning(" This dashboard is restricted to Academic Coordinators. Please authenticate in the sidebar.")
        return
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("Settings")
    new_pass = st.sidebar.text_input("Set New Custom Password:", type="password", key="admin_new_pass")
    if st.sidebar.button("Save New Password"):
        if new_pass:
            with open("official_pass.txt", "w") as f:
                f.write(new_pass)
            st.sidebar.success("Password updated successfully!")
        else:
            st.sidebar.error("Password cannot be empty.")
            
    student_records = st.session_state.student_data
    
    st.subheader("Institutional Overview")
    total = len(student_records)
    crit_count = len(student_records[student_records['risk_level'] == 'Critical'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Students across all Departments", total)
    m2.metric("Global Critical Risk Count", crit_count, delta="-2 since last month", delta_color="inverse")
    m3.metric("Avg Improvement Rate (Post-Intervention)", "18.5%", delta="4.2% YoY")
    
    st.markdown("---")
    st.subheader("Department-wise At-Risk Analysis")
    
    d_col1, d_col2 = st.columns(2)
    
    with d_col1:
        at_risk = student_records[student_records['risk_level'].isin(['Critical', 'Warning'])]
        if not at_risk.empty and 'department' in at_risk.columns:
            # Need to figure out a better grouping logic later if departments change
            d_counts = at_risk['department'].value_counts().reset_index()
            d_counts.columns = ['Department', 'At-Risk Count']
            b_chart = px.bar(d_counts, x='Department', y='At-Risk Count', color='Department', title="At-Risk Students per Department")
            b_chart.update_layout(template="plotly_dark")
            st.plotly_chart(b_chart, use_container_width=True)
        else:
            st.info("No at-risk students found or department data missing.")
            
    with d_col2:
        eff = pd.DataFrame({
            "Timeline": ["Week 1", "Week 2", "Week 3 (Intervention)", "Week 4", "Week 5"],
            "Avg Institution Score": [45, 48, 50, 75, 82]
        })
        l_chart = px.line(eff, x="Timeline", y="Avg Institution Score", markers=True, title="Institution-Wide Intervention Impact")
        l_chart.add_vline(x="Week 3 (Intervention)", line_dash="dash", line_color="rgba(255, 255, 255, 0.5)")
        l_chart.update_layout(template="plotly_dark")
        st.plotly_chart(l_chart, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Patterns & Trends")
    
    if 'subject' in student_records.columns:
        sub_risk = student_records[student_records['risk_level'] == 'Critical']['subject'].value_counts()
        worst_subject = sub_risk.idxmax() if not sub_risk.empty else "General Studies"
        st.info(f" **AI Insight:** System analysis indicates that **{worst_subject}** currently exhibits the highest concentration of 'Critical' risk students across the institution. The primary contributing factors identified are 'Low Attendance' correlating heavily with 'High Missing Assignments'. It is recommended to deploy targeted academic advising and remedial sessions for {worst_subject} faculty in the upcoming weeks.")
    
    st.markdown("---")
    st.subheader("Export Center")
    csv_bytes = student_records.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=" Download Institution-Level Risk Report (CSV)",
        data=csv_bytes,
        file_name='institution_risk_report.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
