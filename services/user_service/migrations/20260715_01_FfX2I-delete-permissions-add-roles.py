"""
delete permissions, add roles
"""

from yoyo import step

__depends__ = {'20260706_02_6psjG-add-column-token-in-users-table'}

steps = [
    step(
        """
        ALTER TABLE users
            DROP COLUMN permissions,
            ADD COLUMN roles
                VARCHAR(20)[]
                NOT NULL
                DEFAULT '{}'
                CHECK ( roles <@ ARRAY ['staff']::VARCHAR[] )
        """,
        """
        ALTER TABLE users
            DROP COLUMN roles,
            ADD COLUMN permissions
                VARCHAR(20)[]
                NOT NULL
                DEFAULT '{}'
                CHECK ( permissions <@ ARRAY['read', 'write', 'delete', 'admin']::VARCHAR[] );
        """
    )
]
