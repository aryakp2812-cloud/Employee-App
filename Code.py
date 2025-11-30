import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt

# ------------------------------
# DATABASE CONNECTION
# ------------------------------
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='arya1998',
        database='employee_db'
    )

# ------------------------------
# STREAMLIT APP
# ------------------------------
st.title("🏢 VIHARA COMPANY - Employee Management System")

# LOGIN
with st.expander("🔐 Login", expanded=True):
    username = st.text_input("Enter username:")
    password = st.text_input("Enter password:", type="password")

if username.strip() and password.strip():
    st.success("✅ Login Successfully")

    menu = st.sidebar.radio(
        "Menu",
        ["Show Employees", "Add Employee", "Edit Employee", "Delete Employee", "📊 Visualizations"]
    )

    conn = get_connection()
    cursor = conn.cursor()

    # 1. SHOW EMPLOYEES
    if menu == "Show Employees":
        st.subheader("📋 All Employee Details")
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()

        if not data:
            st.warning("No employee records found.")
        else:
            df = pd.DataFrame(data, columns=["ID", "Name", "Department", "Salary", "Phone"])
            st.dataframe(df, use_container_width=True)

    # 2. ADD EMPLOYEE
    elif menu == "Add Employee":
        st.subheader("➕ Add New Employee")
        with st.form("add_form"):
            emp_id = st.number_input("ID", step=1)
            name = st.text_input("Name")
            dept = st.text_input("Department")
            salary = st.number_input("Salary", step=1000)
            phone = st.text_input("Phone")
            submitted = st.form_submit_button("Add Employee")

            if submitted:
                cursor.execute("SELECT id FROM employees WHERE id=%s", (emp_id,))
                if cursor.fetchone():
                    st.error("❌ Employee ID already exists!")
                elif not phone.isdigit() or len(phone) != 10:
                    st.error("❌ Phone number should be 10 digits!")
                else:
                    cursor.execute(
                        "INSERT INTO employees (id, Name, Department, Salary, Phone) VALUES (%s, %s, %s, %s, %s)",
                        (emp_id, name, dept, salary, phone)
                    )
                    conn.commit()
                    st.success("✅ Employee added successfully!")

    # 3. EDIT EMPLOYEE
    elif menu == "Edit Employee":
        st.subheader("✏️ Edit Employee")
        cursor.execute("SELECT id FROM employees")
        ids = [row[0] for row in cursor.fetchall()]

        if ids:
            selected_id = st.selectbox("Select Employee ID", ids)
            cursor.execute("SELECT * FROM employees WHERE id=%s", (selected_id,))
            emp_data = cursor.fetchone()

            if emp_data:
                with st.form("edit_form"):
                    field = st.selectbox("Field to edit", ["Name", "Department", "Salary", "Phone"])
                    new_value = st.text_input(f"Enter new value for {field}")
                    submit_edit = st.form_submit_button("Update")

                    if submit_edit:
                        if not new_value.strip():
                            st.error("❌ New value cannot be empty.")
                        else:
                            if field == "Phone" and (not new_value.isdigit() or len(new_value) != 10):
                                st.error("❌ Invalid phone number.")
                            elif field == "Salary":
                                try:
                                    new_value = int(new_value)
                                except ValueError:
                                    st.error("❌ Salary must be a number.")
                                    st.stop()

                            cursor.execute(f"UPDATE employees SET {field}=%s WHERE id=%s", (new_value, selected_id))
                            conn.commit()
                            st.success(f"✅ {field} updated successfully!")
        else:
            st.warning("No employees found to edit.")

    # 4. DELETE EMPLOYEE
    elif menu == "Delete Employee":
        st.subheader("❌ Delete Employee")
        cursor.execute("SELECT id FROM employees")
        ids = [row[0] for row in cursor.fetchall()]

        if ids:
            delete_id = st.selectbox("Select Employee ID to Delete", ids)
            if st.button("Delete"):
                cursor.execute("DELETE FROM employees WHERE id=%s", (delete_id,))
                conn.commit()
                st.success("✅ Employee deleted successfully!")
        else:
            st.warning("No employees found to delete.")

    # 5. VISUALIZATIONS
    elif menu == "📊 Visualizations":
        st.subheader("📈 Employee Data Insights")
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()

        if not data:
            st.warning("No employee records found for visualization.")
        else:
            df = pd.DataFrame(data, columns=["ID", "Name", "Department", "Salary", "Phone"])

            # Bar Chart - Salary by Department
            st.markdown("### 💼 Average Salary by Department")
            avg_salary = df.groupby("Department")["Salary"].mean()
            fig, ax = plt.subplots()
            ax.bar(avg_salary.index, avg_salary.values)
            ax.set_xlabel("Department")
            ax.set_ylabel("Average Salary")
            ax.set_title("Average Salary by Department")
            st.pyplot(fig)

            # Pie Chart - Employee count by Department
            st.markdown("### 👥 Employee Distribution by Department")
            dept_count = df["Department"].value_counts()
            fig2, ax2 = plt.subplots()
            ax2.pie(dept_count.values, labels=dept_count.index, autopct='%1.1f%%', startangle=90)
            ax2.set_title("Employees per Department")
            ax2.axis('equal')
            st.pyplot(fig2)

    # Close connection
    cursor.close()
    conn.close()

else:
    st.warning("Please login to continue.")