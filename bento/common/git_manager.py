import git

from bento.common import logger, logutil, util

# TODO add in structure to class somehow?
from bento.common.structure import PathConf

logging = logger.fancy_logger("git")


class GitManager:
    def __init__(self):
        self.repo = None
        self.cp_cmd = (
            "mkdir -p ~/.ssh/ && cp /run/secrets/github_ssh_privatekey_rw ~/.ssh/id_rsa"
        )
        self.host_cmd = "ssh-keyscan -H github.com >> ~/.ssh/known_hosts"
        self.cache_to_repo = "cp -r cache/{folder} repositories/{org}"

    @logutil.loginfo(level="debug")
    def clone_repo(self, repository, local_path=".", read_only=False):
        full_path = f"{PathConf.git.path}/{local_path}"
        logging.warning(f"Cloning {repository} to {full_path}")
        if read_only:
            git.Repo.clone_from(f"https://github.com/{repository}", full_path)
        else:
            logging.warning("Attempting to add private key to .ssh")
            util.logged_command(self.cp_cmd, shell=True)
            logging.warning("Adding public key of github to ssh known_hosts")
            util.logged_command(self.host_cmd, shell=True)
            git.Repo.clone_from(f"git@github.com:{repository}", full_path)

    @logutil.loginfo(level="debug")
    def check_repo(self, local_path="."):
        full_path = f"{PathConf.git.path}/{local_path}"
        try:
            self.repo = git.Repo(full_path)
            assert not self.repo.bare
            if self.repo.is_dirty():
                print(self.repo.untracked_files)
                self.repo.index.diff(None)
        except Exception as exc:
            # Flesh this out more
            logging.warning("failed check_repo")
            logging.warning(exc)

    @logutil.loginfo(level="debug")
    def push_changes(self, branch="autocommit", commit_msg="automated_msg"):
        copy_library = self.cache_to_repo.format(
            folder="library", org="sample_business"
        )
        util.logged_command(copy_library, shell=True)
        copy_diagrams = self.cache_to_repo.format(
            folder="diagrams", org="sample_business"
        )
        util.logged_command(copy_diagrams, shell=True)
        repo = self.repo
        repo.git.checkout("HEAD", b=branch)
        repo.git.add(".")
        repo.index.commit(commit_msg)
        repo.remote(name="origin").push(["--set-upstream", branch])

    def load_org(self):
        logging.warning("TODO: put in org loading")
        return "library"
