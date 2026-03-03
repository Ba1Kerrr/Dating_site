case "$1" in
    "new")
        shift
        docker exec dating-api alembic revision --autogenerate -m "$*"
        ;;
    "up")
        docker exec dating-api alembic upgrade head
        ;;
    "down")
        docker exec dating-api alembic downgrade -1
        ;;
    "history")
        docker exec dating-api alembic history
        ;;
    "current")
        docker exec dating-api alembic current
        ;;
    *)
        echo "Usage: ./scripts/db-migrate.sh [new|up|down|history|current]"
        ;;
esac