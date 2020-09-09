set -x

pytest ./tools

echo "Tests passed passed!!!!"

python tools/data_builder.py

echo "Data built"

scripts/publish

