import os
from pathlib import Path
import mysql.connector
from mysql.connector import Error

# Marker file to indicate installation completed
INSTALL_MARKER = Path("/app/data/.installed")

def is_already_installed(cnx):
    """Check if product_database table exists → if yes, assume installed."""
    try:
        cursor = cnx.cursor()
        cursor.execute("SHOW TABLES LIKE 'product_database';")
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists
    except Exception as e:
        print("Error checking installation:", e)
        return False

def mark_installed():
    INSTALL_MARKER.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_MARKER.touch()

def is_marked_installed():
    return INSTALL_MARKER.exists()
