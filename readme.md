# Fetch! A CI Repo Updater

Connect your Bitbucket Repo with Gitlab-CE and run a CI Pipeline.

This script checks for the latest commit in master, development branch and branches with the name as declared in  `target_branch_word`.

Copy this entire folder(repo-updater) to the machine that wants to check for the branch updates.

A log file will be created in order to debug or check for possible errors.

## Dependencies :
You need to install gitpython module

```
sudo pip3 install gitpython

```

See [gitpython documentation](http://gitpython.readthedocs.io/en/stable/intro.html) , for more information about this module.

## Execution :

```
python3.4 repo-updater.py
```
