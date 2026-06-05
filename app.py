import streamlit as st
import sqlite3

# DATABASE
conn = sqlite3.connect(
    "password_manager.db",
    check_same_thread=False
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    username TEXT,
    password TEXT
)
""")

conn.commit()

# SESSION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# LOGIN / REGISTER
if not st.session_state.logged_in:

    st.title("🔐 Password Manager")

    menu = st.sidebar.selectbox(
        "Menu",
        ["Register", "Login"]
    )

    # REGISTER
    if menu == "Register":

        st.subheader("Register")

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Register"):

            try:
                cursor.execute(
                    """
                    INSERT INTO users(username,password)
                    VALUES(?,?)
                    """,
                    (username, password)
                )

                conn.commit()

                st.success(
                    "Registration Successful!"
                )

            except:
                st.error(
                    "Username already exists!"
                )

    # LOGIN
    else:

        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            cursor.execute(
                """
                SELECT * FROM users
                WHERE username=? AND password=?
                """,
                (username, password)
            )

            user = cursor.fetchone()

            if user:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:

                st.error(
                    "Invalid Username or Password"
                )

# DASHBOARD
else:

    st.title("🔐 Password Dashboard")

    st.success(
        f"Welcome {st.session_state.username}"
    )

    st.subheader("Add New Password")

    website = st.text_input("Website")

    site_username = st.text_input(
        "Website Username"
    )

    site_password = st.text_input(
        "Website Password",
        type="password"
    )

    if st.button("Save Password"):

        if website and site_username and site_password:

            cursor.execute(
                """
                INSERT INTO passwords
                (website,username,password)
                VALUES(?,?,?)
                """,
                (
                    website,
                    site_username,
                    site_password
                )
            )

            conn.commit()

            st.success(
                "Password Saved Successfully!"
            )

            st.rerun()

    st.divider()

    st.subheader("Saved Passwords")

    cursor.execute(
        "SELECT * FROM passwords"
    )

    data = cursor.fetchall()

    if not data:

        st.info(
            "No Passwords Saved Yet"
        )

    else:

        for row in data:

            col1, col2, col3 = st.columns(
                [6,1,1]
            )

            with col1:

                st.write(
                    f"🌐 {row[1]} | "
                    f"👤 {row[2]} | "
                    f"🔑 {row[3]}"
                )

            with col2:

                if st.button(
                    "Edit",
                    key=f"edit_{row[0]}"
                ):

                    st.session_state.edit_id = row[0]

            with col3:

                if st.button(
                    "Delete",
                    key=f"delete_{row[0]}"
                ):

                    cursor.execute(
                        """
                        DELETE FROM passwords
                        WHERE id=?
                        """,
                        (row[0],)
                    )

                    conn.commit()

                    st.rerun()

    # EDIT SECTION
    if "edit_id" in st.session_state:

        cursor.execute(
            """
            SELECT * FROM passwords
            WHERE id=?
            """,
            (st.session_state.edit_id,)
        )

        record = cursor.fetchone()

        if record:

            st.divider()

            st.subheader(
                "Edit Password"
            )

            new_website = st.text_input(
                "Website",
                value=record[1]
            )

            new_username = st.text_input(
                "Username",
                value=record[2]
            )

            new_password = st.text_input(
                "Password",
                value=record[3]
            )

            if st.button(
                "Update Password"
            ):

                cursor.execute(
                    """
                    UPDATE passwords
                    SET website=?,
                        username=?,
                        password=?
                    WHERE id=?
                    """,
                    (
                        new_website,
                        new_username,
                        new_password,
                        st.session_state.edit_id
                    )
                )

                conn.commit()

                del st.session_state.edit_id

                st.success(
                    "Password Updated!"
                )

                st.rerun()

    st.divider()

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()
 
