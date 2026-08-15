import sqlite3
import hashlib
from datetime import datetime
import os


# ============================================================
# DATABASE PATH
# ============================================================

DB_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chatbot.db"
)

print("DATABASE FILE:", DB_NAME)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# ============================================================
# CREATE TABLES
# ============================================================

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- USERS ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # ---------------- CONVERSATIONS ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TEXT
        )
    """)

    # ---------------- MESSAGES ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    # ---------------- MEMORY ---------------- #

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# DATABASE MIGRATION
# ============================================================

def migrate_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- CONVERSATIONS ---------------- #

    cursor.execute(
        "PRAGMA table_info(conversations)"
    )

    conversation_columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    print(
        "CONVERSATION COLUMNS:",
        conversation_columns
    )

    if "created_at" not in conversation_columns:

        print("Adding created_at to conversations...")

        cursor.execute(
            """
            ALTER TABLE conversations
            ADD COLUMN created_at TEXT
            """
        )

        print(
            "created_at added to conversations."
        )

    # ---------------- MESSAGES ---------------- #

    cursor.execute(
        "PRAGMA table_info(messages)"
    )

    message_columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    print(
        "MESSAGE COLUMNS:",
        message_columns
    )

    if "created_at" not in message_columns:

        print("Adding created_at to messages...")

        cursor.execute(
            """
            ALTER TABLE messages
            ADD COLUMN created_at TEXT
            """
        )

        print(
            "created_at added to messages."
        )

    conn.commit()
    conn.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_db()
migrate_database()


# ============================================================
# PASSWORD HASH
# ============================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# ============================================================
# REGISTER
# ============================================================

def register(
    name,
    email,
    password
):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password
            )

            VALUES (?, ?, ?)
            """,

            (
                name,
                email,
                hash_password(password)
            )
        )

        conn.commit()
        conn.close()

        return True

    except sqlite3.IntegrityError:

        return False


# ============================================================
# LOGIN
# ============================================================

def login(
    email,
    password
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users

        WHERE email = ?
        AND password = ?
        """,

        (
            email,
            hash_password(password)
        )
    )

    user = cursor.fetchone()

    conn.close()

    return user


# ============================================================
# CREATE CONVERSATION
# ============================================================

def create_conversation(title):

    conn = get_connection()
    cursor = conn.cursor()

    created_at = str(
        datetime.now()
    )

    cursor.execute(
        """
        INSERT INTO conversations
        (
            title,
            created_at
        )

        VALUES (?, ?)
        """,

        (
            title,
            created_at
        )
    )

    conversation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return conversation_id


# ============================================================
# GET CONVERSATIONS
# ============================================================

def get_conversations():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title

        FROM conversations

        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    conn.close()

    return data


# ============================================================
# SAVE MESSAGE
# ============================================================

def save_message(
    conversation_id,
    role,
    message
):

    if conversation_id is None:
        return

    conn = get_connection()
    cursor = conn.cursor()

    created_at = str(
        datetime.now()
    )

    cursor.execute(
        """
        INSERT INTO messages
        (
            conversation_id,
            role,
            message,
            created_at
        )

        VALUES (?, ?, ?, ?)
        """,

        (
            conversation_id,
            role,
            message,
            created_at
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# LOAD MESSAGES
# ============================================================

def load_messages(
    conversation_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            role,
            message

        FROM messages

        WHERE conversation_id = ?

        ORDER BY id
        """,

        (
            conversation_id,
        )
    )

    data = cursor.fetchall()

    conn.close()

    return data


# ============================================================
# RENAME CONVERSATION
# ============================================================

def rename_conversation(
    cid,
    title
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE conversations

        SET title = ?

        WHERE id = ?
        """,

        (
            title,
            cid
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# DELETE CONVERSATION
# ============================================================

def delete_conversation(cid):

    conn = get_connection()
    cursor = conn.cursor()

    # Delete messages

    cursor.execute(
        """
        DELETE FROM messages

        WHERE conversation_id = ?
        """,

        (
            cid,
        )
    )

    # Delete conversation

    cursor.execute(
        """
        DELETE FROM conversations

        WHERE id = ?
        """,

        (
            cid,
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# SAVE MEMORY
# ============================================================

def save_memory(key, value):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM memory
        WHERE key = ?
        """,
        (key,)
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE memory
            SET value = ?
            WHERE key = ?
            """,
            (
                value,
                key
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO memory
            (
                key,
                value
            )

            VALUES (?, ?)
            """,
            (
                key,
                value
            )
        )

    conn.commit()
    conn.close()


# ============================================================
# GET ALL MEMORY
# ============================================================

def get_all_memory():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            key,
            value

        FROM memory
        """
    )

    data = cursor.fetchall()

    conn.close()

    return data


# ============================================================
# DELETE MEMORY
# ============================================================

def delete_memory(key):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM memory
        WHERE key = ?
        """,
        (key,)
    )

    conn.commit()
    conn.close()