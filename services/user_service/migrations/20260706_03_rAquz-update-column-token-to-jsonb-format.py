"""
update column token to jsonb format
"""

from yoyo import step

__depends__ = {'20260706_02_6psjG-add-column-token-in-users-table'}

steps = [
    step("ALTER TABLE users ALTER COLUMN refresh_token TYPE JSONB USING refresh_token::JSONB;")
]
