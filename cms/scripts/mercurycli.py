# Command-line interface to Mercury.
# Right now this is just the job runner.

commands = {
    "queue-post": {
        "help": "Add one or more post IDs to the queue to be published.",
        "metavar": "post",
        "nargs": "+",
    },
    "queue-blog": {
        "help": "Add one or more blog IDs to the queue to be published.",
        "metavar": "blog",
        "nargs": "+",
    },
    "run-queue": {"help": "Run any queued jobs. Default is for all blogs."},
    "run-queue-blog": {
        "help": "Run any queued jobs for one or more specified blogs.",
        "metavar": "blog",
        "nargs": "+",
    },
    "clear-queue": {"help": "Remove all jobs from the queue."},
    "clear-queue-blog": {
        "help": "Remove all jobs from the queue for a given blog.",
        "metavar": "blog",
        "nargs": "+",
    },
    "defrag": {
        "help": "Defragment the database. This locks the database while in progress."
    },
}

import argparse

parser = argparse.ArgumentParser(description="Command-line interface for Mercury.")
for arg, mods in commands.items():
    parser.add_argument(f"--{arg}", **mods)

args = parser.parse_args()
