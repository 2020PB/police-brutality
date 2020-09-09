# Put files in a temporary folder
# checkout target branch
# cp files in dir to target branch
# add and commit with user config
# Have generic message that uses the git sha

tmp_dir=$(mktemp -d -t ci-XXXXXXXXXX)

email=$(git show --pretty=%ae HEAD)
name=$(git show --pretty=%an HEAD)

git config --global user.name $email
git config --global user.email $name

cp -rT $ tools/data_build $tmp_dir
git checkout data_build
cp -rT $tmp_dir ./
rm -rf $tmp_dir
git add .
git commit -m "Update data_build to output generated at $TRAVIS_COMMIT"
git push

