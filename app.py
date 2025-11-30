import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt

st.set_page_config(page_title="Employee Management", layout="wide")

# --- Full-page Background Image ---
st.markdown(
    """
    <style>
    /* Full-page background image with dark overlay */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                          url("https://images.unsplash.com/photo-1521791136064-7986c2920216");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;  /* Default text color outside containers */
    }

    /* Container for login section */
    .login-container {
        background-color: rgba(255, 255, 255, 0.95);  /* almost opaque for full readability */
        padding: 40px;
        border-radius: 15px;
        max-width: 450px;
        margin: 50px auto;
        color: black;  /* Text inside container is black */
    }

    /* Titles and headings */
    h1, h2, h3, h4 {
        color: white !important;
        text-shadow: 1px 1px 2px black;
    }

    /* Streamlit input labels */
    label {
        color: black !important;
        font-weight: bold;
    }

    /* Buttons style */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5em 1em;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------------
# MySQL connection function
# -------------------------------------
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='arya1998',   # change if needed
        database='employee_db'
    )

# -------------------------------------
# Streamlit App
# -------------------------------------
st.set_page_config(page_title="Employee Management", layout="wide")
st.title("🏢 VIHARA COMPANY - Employee Management System")

# --- LOGIN SECTION ---
st.subheader("🔐 Login Section")
username = st.text_input("Enter username:")
password = st.text_input("Enter password:", type="password")
login_btn = st.button("Login")
st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN SECTION ---
if username == "admin" and password == "1234":
    st.success("✅ Login Successful!")

    # Sidebar menu
    menu = st.sidebar.radio("Menu", ["Show Employees", "Add Employee", "Edit Employee", "Delete Employee", "📊 Visualizations"])

    # Connect to database
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()

    # ---- 1. SHOW EMPLOYEES ----
    if menu == "Show Employees":
        st.subheader("📋 All Employee Details")
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()
        if not data:
            st.warning("No employee records found.")
        else:
            df = pd.DataFrame(data, columns=["ID", "Name", "Department", "Salary", "Phone"])
            st.dataframe(df, use_container_width=True)

    # ---- 2. ADD EMPLOYEE ----
    elif menu == "Add Employee":
        st.subheader("➕ Add Employee")
        with st.form("add_form"):
            emp_id = st.number_input("ID", step=1)
            name = st.text_input("Name")
            dept = st.text_input("Department")
            salary = st.number_input("Salary", step=1000)
            phone = st.text_input("Phone")
            submitted = st.form_submit_button("Add Employee")

            if submitted:
                if not (phone.isdigit() and len(phone) == 10):
                    st.error("❌ Phone number should be 10 digits!")
                else:
                    try:
                        cursor.execute("INSERT INTO employees VALUES (%s, %s, %s, %s, %s)",
                                       (emp_id, name, dept, salary, phone))
                        conn.commit()
                        st.success("✅ Employee added successfully!")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

    # ---- 3. EDIT EMPLOYEE ----
    elif menu == "Edit Employee":
        st.subheader("✏️ Edit Employee")
        cursor.execute("SELECT id FROM employees")
        ids = [row[0] for row in cursor.fetchall()]
        if ids:
            selected_id = st.selectbox("Select Employee ID", ids)
            field = st.selectbox("Field to edit", ["Name", "Department", "Salary", "Phone"])
            new_value = st.text_input(f"Enter new value for {field}")
            if st.button("Update"):
                try:
                    cursor.execute(f"UPDATE employees SET {field}=%s WHERE id=%s", (new_value, selected_id))
                    conn.commit()
                    st.success(f"✅ {field} updated successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("No employees found to edit.")

    # ---- 4. DELETE EMPLOYEE ----
    elif menu == "Delete Employee":
        st.subheader("❌ Delete Employee")
        cursor.execute("SELECT id FROM employees")
        ids = [row[0] for row in cursor.fetchall()]
        if ids:
            delete_id = st.selectbox("Select Employee ID", ids)
            if st.button("Delete"):
                cursor.execute("DELETE FROM employees WHERE id=%s", (delete_id,))
                conn.commit()
                st.success("✅ Employee deleted successfully!")
        else:
            st.warning("No employees found to delete.")

    # ---- 5. VISUALIZATIONS ----
    elif menu == "📊 Visualizations":
        st.subheader("📈 Employee Insights")
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()
        if not data:
            st.warning("No data available for charts.")
        else:
            df = pd.DataFrame(data, columns=["ID", "Name", "Department", "Salary", "Phone"])

            # Bar Chart
            avg_salary = df.groupby("Department")["Salary"].mean()
            fig, ax = plt.subplots()
            avg_salary.plot(kind="bar", color="skyblue", ax=ax)
            ax.set_title("Average Salary by Department")
            ax.set_ylabel("Salary")
            st.pyplot(fig)

            # Pie Chart
            dept_counts = df["Department"].value_counts()
            fig2, ax2 = plt.subplots()
            ax2.pie(dept_counts, labels=dept_counts.index, autopct="%1.1f%%", startangle=90)
            ax2.set_title("Employee Distribution by Department")
            st.pyplot(fig2)

    cursor.close()
    conn.close()

else:
    st.warning("Please login to continue.")