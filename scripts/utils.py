import os
import re

DEFAULT_DEPLOY_CONFIG = {
    "port": 70,
    "cpu": 1,
    "memory": 32,
    "disk": 64,
}


def warn(msg):
    # with red symbol `[!]`, red content
    print(f"\033[1;31m[!] {msg}\033[0m")


def format_deploy_config(deploy):
    return f"port: {deploy['port']}, cpu: {deploy['cpu'] / 10}c, mem: {deploy['memory']}M, disk: {deploy['disk']}M"


def get_challenge_info(path):
    with open(path, "r") as f:
        content = f.read()
        name = re.search(r"# (.*)", content).group(1)
        author = re.search(r"\*\*Author:\*\* (.*)", content).group(1)
        difficulty = re.search(r"\*\*Difficulty:\*\* (.*)", content).group(1)
        category = re.search(r"\*\*Category:\*\* (.*)", content).group(1)
        flag = re.search(r"\*\*Flag:\*\* `(.*)`", content)
        if flag:
            flag = flag.group(1)

        deploy = re.search(r"## Deployment\n\n(.*?)\n\n", content, re.S)

        if deploy is not None:
            deploy = re.sub(r"\n\n|Port.*\n", "", deploy.group(1))
            deploy = deploy.split("\n")[-1].split("|")[1:-1]
            deploy = [x.strip() for x in deploy if x.strip()]
            assert len(deploy) == 4, "Invalid deployment config"
            deploy = {k: v for k, v in zip(["port", "cpu", "memory", "disk"], deploy)}

            errors = []
            for k, v in deploy.items():
                try:
                    deploy[k] = int(v)
                except ValueError:
                    errors.append(f"Invalid deployment config value: {v}")
                    deploy[k] = DEFAULT_DEPLOY_CONFIG[k]

            if errors:
                raise Exception("\n    ".join(errors))

    return name, author, difficulty, category, flag, deploy


def get_chall_list():
    challenges = []
    for root, _, files in os.walk("challenges"):
        if "_template" in root:
            continue
        for file in files:
            if file == "README.md":
                path = os.path.join(root, file)
                name, author, difficulty, category, _, _ = get_challenge_info(path)
                challenges.append((name, root, category, difficulty, author))
    challenges.sort(key=lambda x: (x[2], x[3]))
    return challenges


difficulties = [
    "Baby",
    "Trivial",
    "Easy",
    "Normal",
    "Medium",
    "Hard",
    "Expert",
    "Insane",
]

categories = [
    "Misc",
    "Crypto",
    "Pwn",
    "Web",
    "Reverse",
    "Blockchain",
    "Forensics",
    "Hardware",
    "Mobile",
    "PPC",
    "AI",
    "Pentest",
    "OSINT",
]

lower_categories = [cate.lower() for cate in categories]


short_categories = [
    "misc",
    "cr",
    "pwn",
    "web",
    "re",
    "bc",
    "fo",
    "hw",
    "mo",
    "ppc",
    "ai",
    "pt",
    "osint",
]

long_cate = {short: cate for short, cate in zip(short_categories, categories)}

short_cate = {cate: short for short, cate in zip(short_categories, categories)}
