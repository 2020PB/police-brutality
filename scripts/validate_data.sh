set -x

python -c "import nltk; nltk.download('wordnet')"
pytest ./tools

echo "Tests passed passed!!!!"

echo github_ref: $TRAVIS_COMMIT
python tools/data_rewriter.py
git add reports
git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"
# git remote set-url origin https://x-access-token:${{ secrets.UBERSHMEKEL_ALT_TOKEN }}@github.com/${{ github.repository }}
git commit -m "Automated data fixes" -a | exit 0
git push
