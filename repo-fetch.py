import os, shutil, sys, time
import git
from git import *

class RepoHandler:

    # set the name of repo , the link to it , and the word that the test branch should have
    DIR_NAME_uav = "repo_name"
    REMOTE_URL_uav = "git@bitbucket.org:your_project_name.git"
    target_branch_word = "test-branch"
    branch_to_checkout=[]

    # constructor of the repo object
    def __init__(self):
		# check for the folder path , if it exists
        if os.path.isdir(RepoHandler.DIR_NAME_uav):
            shutil.rmtree(RepoHandler.DIR_NAME_uav)

        # clone the repo
        self.git = git.Repo.clone_from(RepoHandler.REMOTE_URL_uav, RepoHandler.DIR_NAME_uav)
        # set the remote for origin
        self.origin_uav = self.git.remotes.origin
        # create a remote for the project on gitlab server
        self.git.create_remote("gitlab_remote", url="git@xxx.xxx.xxx.xxx:root/gitlab_project.git")
        FileHandler.add_to_log("--     Execution started     --")

    # function to find the branches with the target word
    def get_test_branch(self):
        RepoHandler.branch_to_checkout=[]
        for branch in self.origin_uav.refs:
            # if the requested branch contains that word , add it to the list of the branches to check for
            # the latest commit
            if RepoHandler.target_branch_word in str(branch):
                RepoHandler.branch_to_checkout.append(str(branch).replace('origin/',''))
        FileHandler.add_to_log("- Branches to check -")
        FileHandler.add_to_log(RepoHandler.branch_to_checkout)
        return RepoHandler.branch_to_checkout


class FileHandler:

    # function that checks if the requested branch is up-to-date with the latest commit ,
    # and if so update the commit in the file
    def is_branch_updated(self,commit, branches):
        update_repo = False
        # open the file that stores the latest commits
        with open('latest_commit.txt', 'r+') as commit_file:
            # for each line in the file
            for line in commit_file:
                line_to_replace = line
                # check for correct line input
                FileHandler.line_error_check(line)
                line = line.strip('\n')
                line = line.split(",")
                # if the second argument on the line is in the list
                if line[1] == branches:
					# if the first argument on the line is not the latest commit
                    if line[0] != str(commit):
                        update_repo = True
                        # create a temporary list
                        output = FileHandler.create_temp_file(line_to_replace)
                        # add the line to the list
                        output.append(str(commit) + "," + branches +"\n" )
                        # open the file and append that list with the updated commit
                        FileHandler.create_updated_file(output)
                        FileHandler.add_to_log("---   UPDATING: "+str(branches))
                    break
            else:
				# if the branch does not exist, add it to the list to be updated
                commit_file.write(commit + "," + branches+"\n")
                update_repo = True
                FileHandler.add_to_log("---   UPDATING: "+str(branches))
        return update_repo

    # create a temporary list from the file, without a specific line, defined as input argument
    def create_temp_file(to_replace):
        output = []
        with open('latest_commit.txt', 'r+') as file_clone:
            for commit_line in file_clone:
                if commit_line != to_replace:
                    output.append(commit_line)
        return output

    # create the updated file with the latest commits
    def create_updated_file(tmp_file):
        f = open('latest_commit.txt', 'w')
        f.writelines(tmp_file)
        f.close()

    # check for line wrong format
    def line_error_check(line):
        if line.count(",") != 1:
            raise Exception("More than one comma")

    # function to print output to the logfile
    def add_to_log(to_add):
        with open('log.txt', 'a') as f:
            print(to_add, file=f)


def main():
    try:
        repo = RepoHandler()
        f_handler = FileHandler()
        branches_to_checkout = repo.get_test_branch()
        # for all the branches in the list to check
        for branch in branches_to_checkout:
			# checkout to that branch
            repo.git.git.checkout(branch)
            # find the latest commit
            latest_commit_uav = repo.git.head.reference.commit.hexsha
            # return true if the branch has to be updated
            update = f_handler.is_branch_updated(latest_commit_uav, branch)
            if update:
                # pull the latest version of the branch from origin ,rebase=True to solve the push error
                repo.git.remotes.origin.pull(rebase=True)
                # push to gitlab server project at branch name same as the branch we worked
                repo.git.remotes.workstation.push(refspec=str(branch)+':'+str(branch),force=True)
                print("Updating")
            else:
                print("Nothing to update")
    except Exception as e:
        print("EXCEPTION : "+str(e))

if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)
