get_roles = """
SELECT * FROM roles;
"""

get_role_by_name = """
SELECT * FROM roles WHERE role_name = :role_name;
"""


update_role_desc = """
UPDATE roles
SET role_desc = :role_desc
WHERE role_name = :role_name;
"""

insert_session = """
INSERT INTO sessions (user_id, session_uuid, mode_id)
VALUES
    (:user_id, :uuid, :mode_id)
"""