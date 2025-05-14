from sqlalchemy.orm import Session
from faker import Faker
import random
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from backend.models.model import (
    User,
    TodoItemChannel,
    TodoItem,
    TodoItemUserSubscription,
    TodoChannelUserSubscription,
)

fake = Faker()

def create_mock_data(session: Session, user_count=5, channels_per_user=2, todos_per_channel=3):
    users = []
    channels = []
    todos = []
    
    # Create users
    for _ in range(user_count):
        user = User(
            name=fake.user_name(),
            email=fake.unique.email(),
            hashed_password=bcrypt.hash("password123"),
            disabled=False,
            email_verified=random.choice([True, False])
        )
        session.add(user)
        users.append(user)
    session.flush()

    # Create channels
    for user in users:
        for _ in range(channels_per_user):
            channel = TodoItemChannel(
                name=fake.unique.word(),
                description=fake.text(),
                creator_id=user.id
            )
            session.add(channel)
            channels.append(channel)
    session.flush()

    # Create todo items
    for channel in channels:
        for _ in range(todos_per_channel):
            creator = random.choice(users)
            todo = TodoItem(
                name=fake.unique.word(),
                description=fake.sentence(),
                creator_id=creator.id,
                channel_id=channel.id,
                due_date=fake.future_datetime(end_date="+30d"),
                done=random.choice([True, False])
            )
            session.add(todo)
            todos.append(todo)
    session.flush()

    # Create item subscriptions
    for todo in todos:
        subscribers = random.sample(users, k=random.randint(1, len(users)))
        for user in subscribers:
            sub = TodoItemUserSubscription(
                user_id=user.id,
                todo_item_id=todo.id
            )
            session.add(sub)

    # Create channel subscriptions
    for channel in channels:
        subscribers = random.sample(users, k=random.randint(1, len(users)))
        for user in subscribers:
            sub = TodoChannelUserSubscription(
                user_id=user.id,
                todo_item_channel_id=channel.id
            )
            session.add(sub)

    session.commit()
    print("Mock data created.")


if __name__ == "__main__":
    from backend.database import sync_session
    with sync_session() as session:
        create_mock_data(session)
