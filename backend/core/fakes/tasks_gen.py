# from core.core.database import SessionLocal
# from sqlalchemy.orm import Session
# from tasks.models import TaskModel
# from users.models import UserModel
# from faker import Faker

import 

fake = Faker()

def seed_users(db):
    user = UserModel(
        username=fake.user_name(),
        password=fake.password()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User created with Username: {user.username} and ID: {user.id}")
    return user

def seed_tasks(db: Session,user, num_tasks: int = 10):
    tasks_list = []
    for _ in range(num_tasks):
        task = TaskModel(
            user_id=user.id,
            title=fake.sentence(nb_words=5),
            description=fake.paragraph(nb_sentences=3),
            is_completed=fake.boolean(),
        )
        tasks_list.append(task)
    
    db.add_all(tasks_list)
    db.commit()
    print(f"✅ {num_tasks} tasks added successfully!")

def main():
    db = SessionLocal()
    try:
        user = seed_users(db)
        seed_tasks(db,user)
    finally:
        db.close()

if __name__ == "__main__":
    main()
    