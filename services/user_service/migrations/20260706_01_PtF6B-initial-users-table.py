"""
initial users table
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE users
        (
            id          VARCHAR(36) PRIMARY KEY,
            username    VARCHAR(32)  NOT NULL UNIQUE,
            password    VARCHAR(256) NOT NULL,
            permissions VARCHAR(20)[] NOT NULL DEFAULT '{}' CHECK (
                permissions <@ ARRAY['read', 'write', 'delete', 'admin']::VARCHAR[]
            )
        );
        """
    ),
]
