from faker import Faker
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.database.database import engine
fake = Faker()

# Create a base class for our table
Base = declarative_base()

# Define our table
class User(Base):
    __tablename__ = "profile"
    username = Column(Text, primary_key=True, unique=True)
    email = Column(Text, unique=True)
    password = Column(Text)
    age = Column(Integer)
    gender = Column(Text)
    name = Column(Text)
    location = Column(Text)
    avatar = Column(Text)

# Create the table in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Initialize sets to keep track of unique usernames and emails
usernames = set()
emails = set()

# Generate fake data for 10 users
def create_fake():
    for _ in range(100):
        username = fake.user_name()
        while username in usernames:
            username = fake.user_name()
        usernames.add(username)

        email = fake.email()
        while email in emails:
            email = fake.email()
        emails.add(email)

        # Create a new user object
        user = User(
            username=username,
            email=email,
            password=fake.password(),
            age=fake.random_int(min=18, max=100),
            gender=fake.random_element(elements=("male", "female")),
            name=fake.name(),
            location='Moscow',
            avatar=fake.image_url()
        )
        print(user.name, user.password)

        # Add the user to the session
        session.add(user)

    # Commit the changes to the database
    session.commit()