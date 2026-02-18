from app.db.session import SessionLocal
from app.services.auth import ensure_seed_user


def main() -> None:
    with SessionLocal() as db:
        user = ensure_seed_user(db)
        print(f"Seeded user: {user.email}")


if __name__ == "__main__":
    main()
