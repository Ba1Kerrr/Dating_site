#!/bin/bash

echo "Updating dependencies..."

# Сохраняем текущие зависимости из контейнера
docker exec dating-api pip freeze > /tmp/current_deps.txt

# Сравниваем с базовыми
echo "Differences from base requirements:"
diff --side-by-side --suppress-common-lines /tmp/current_deps.txt app/settings/requirements.base.txt

echo ""
echo " Done. To update base requirements run:"
echo "docker exec dating-api pip freeze > app/settings/requirements.base.txt"