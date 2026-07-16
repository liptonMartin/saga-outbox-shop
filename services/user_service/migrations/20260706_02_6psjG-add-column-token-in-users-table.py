"""
add column token in users table
"""

from yoyo import step

__depends__ = {'20260706_01_PtF6B-initial-users-table'}

steps = [
    step(
        "ALTER TABLE users ADD refresh_token VARCHAR(256);",
        "ALTER TABLE users DROP COLUMN refresh_token"
    )
]
