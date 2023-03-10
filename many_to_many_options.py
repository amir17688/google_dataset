from quick_orm.core import Database
from sqlalchemy import Column, String

__metaclass__ = Database.DefaultMeta

class User:
    name = Column(String(30))

@Database.many_to_many(User, ref_name = 'users', backref_name = 'roles', middle_table_name = 'user_role')
class Role:
    name = Column(String(30))

Database.register()

if __name__ == '__main__':
    db = Database('sqlite://')
    db.create_tables()

    user1 = User(name = 'Tyler Long')
    user2 = User(name = 'Peter Lau')
    role = Role(name = 'Administrator', users = [user1, user2])
    db.session.add_then_commit(role)

    admin_role = db.session.query(Role).filter_by(name = 'Administrator').one()
    print ', '.join([user.name for user in admin_role.users]), 'are administrators'