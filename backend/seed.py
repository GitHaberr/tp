from database import Base, engine, SessionLocal
from models import User
from security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(User).count() == 0:
    boss = User(full_name="Иванов Иван", email="boss@firma.ru",
                password_hash=hash_password("1234"), role="boss")
    db.add(boss)
    db.commit()
    db.refresh(boss)

    db.add_all([
        User(full_name="Петров Алексей", email="petrov@firma.ru",
             password_hash=hash_password("1234"), role="employee", manager_id=boss.id),
        User(full_name="Сидорова Мария", email="sidorova@firma.ru",
             password_hash=hash_password("1234"), role="employee", manager_id=boss.id),
    ])
    db.commit()
    print("Тестовые пользователи созданы")
else:
    print("Пользователи уже есть")

db.close()