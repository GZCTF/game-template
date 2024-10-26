import argparse
from utils import *

if not os.path.exists("challenges"):
    print(
        "[!] Please run this script from the root directory with `python scripts/gen_action.py`"
    )
    exit(1)

parser = argparse.ArgumentParser(description="Generate a GitHub action for a challenge")

parser.add_argument(
    "-c", "--category", type=str, choices=lower_categories, help="Challenge category"
)
parser.add_argument(
    "-d",
    "--chall_dir_name",
    type=str,
    help="Challenge directory name, like 'this-is-a-name'",
)
parser.add_argument(
    "-a",
    "--all",
    action="store_true",
    help="Generate actions for all challenges",
    default=False,
)
parser.add_argument(
    "-s",
    "--strict",
    action="store_true",
    help="Exit if an error is encountered",
    default=False,
)

args = parser.parse_args()

# if scope is all, generate actions for all challenges, ignore other args
# if scope is single, generate action for a single challenge, require all args
if not args.all:
    if not all([args.category, args.chall_dir_name]):
        parser.error("please specify a challenge to generate action for")

with open("scripts/chal.template.yml", "r") as f:
    ACTION_TEMPLATE = f.read()


def info(content):
    leading = "\033[1;32m[+] \033[0m"
    bold_content = f"\033[1m{content}\033[0m"
    print(f"{leading}{bold_content}")


def heading(content):
    leading = f"\033[1;33m[*] {content}\033[0m"
    print(leading)


def error(content):
    leading = f"\033[1;31m[!] {content}\033[0m"
    print(leading)
    if args.strict:
        exit(1)


def check_info(chall_dir):
    # check challenge directory name is kebab-case
    chall_dir_name = chall_dir.split("/")[-1]

    if len(chall_dir_name) > 24:
        raise Exception(f"Please use a shorter directory name for {chall_dir_name}")

    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", chall_dir_name):
        raise Exception("Challenge directory name must be kebab-case")

    # check if README.md exists
    if not os.path.exists(f"{chall_dir}/README.md"):
        raise Exception(f"README.md does not exist in {chall_dir}")

    name, author, difficulty, category, flag = get_challenge_info(
        f"{chall_dir}/README.md"
    )

    info(f"{'Name'.ljust(12)}: {name}")
    info(f"{'Author'.ljust(12)}: {author}")

    if difficulty not in difficulties:
        raise Exception(f"Invalid difficulty: {difficulty}")

    info(f"{'Difficulty'.ljust(12)}: {difficulty}")

    chall_cate_dir = chall_dir.split("/")[-2]

    if category not in categories:
        raise Exception(f"Invalid category: {category}")

    if chall_cate_dir != category.lower():
        raise Exception(
            f"Category directory mismatch: {chall_cate_dir} != {category.lower()}"
        )

    info(f"{'Category'.ljust(12)}: {category}({short_cate[category]})")

    if flag:
        info(f"{'Flag'.ljust(12)}: {flag}")
    else:
        error("Flag or flag template not found in README.md")

    # check challenge directory
    allow_list = ["README.md", "assets", "build", "attachments"]
    rest = set(os.listdir(chall_dir)) - set(allow_list)
    if rest:
        raise Exception(
            "Invalid entry found in root dir\n"
            + f"     allow: {', '.join(allow_list)}\n"
            + f"     found: {', '.join(rest)}"
        )

    # check build directory
    if not os.path.exists(f"{chall_dir}/build"):
        return

    allow_list = ["Dockerfile", "custom.yml", "pre-build.sh", "post-build.sh", "src"]
    rest = set(os.listdir(f"{chall_dir}/build")) - set(allow_list)
    rest = [x for x in rest if not x.startswith(".git")]

    if len(rest) > 0:
        raise Exception(
            "Invalid entry found in build dir\n"
            + f"    allow: {', '.join(allow_list)}\n"
            + f"    found: {', '.join(rest)}"
        )


def gen_chall_action(chall_dir):
    global ACTION_TEMPLATE

    name, _, _, category, _ = get_challenge_info(f"{chall_dir}/README.md")

    info("Generating action...")

    chall_dir_name = chall_dir.split("/")[-1]
    chall_cate_dir = chall_dir.split("/")[-2]

    # replace placeholders with actual values
    template = ACTION_TEMPLATE.replace("<CHALL_DIR_NAME>", chall_dir_name)
    template = template.replace("<CATE_DIR>", chall_cate_dir)
    template = template.replace("<CHALL_NAME>", name)

    if os.path.exists(f"{chall_dir}/build/custom.yml"):
        info("Custom steps found, adding to action...")
        intended_steps = "\n"

        with open(f"{chall_dir}/build/custom.yml", "r") as f:
            for line in f.readlines():
                if line.startswith("#") or line == "\n":
                    break
                intended_steps += f"      {line}"

        template = template.replace("      #<CUSTOM_STEPS>\n", intended_steps)
    else:
        template = template.replace("      #<CUSTOM_STEPS>\n", "")

    # write to file
    action_file_name = f"chall.{short_cate[category]}.{chall_dir_name}.yml"
    action_file_path = f".github/workflows/{action_file_name}"
    info(f"Writing action to {action_file_name}")
    with open(action_file_path, "w") as f:
        f.write(template)


def single_chall():
    # check if challenge directory name is kebab-case
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", args.chall_dir_name):
        parser.error("Challenge directory name must be kebab-case")

    chall_dir = f"challenges/{args.category}/{args.chall_dir_name}"

    # check if challenge directory exists
    if not os.path.exists(chall_dir):
        parser.error(f"Challenge directory does not exist: {chall_dir}")

    # check if README.md exists
    if not os.path.exists(f"{chall_dir}/README.md"):
        parser.error(f"README.md does not exist in {chall_dir}")

    # check if `build/Dockerfile` exists if `build` directory exists
    if os.path.exists(f"{chall_dir}/build") and not os.path.exists(
        f"{chall_dir}/build/Dockerfile"
    ):
        parser.error(f"Dockerfile does not exist in {chall_dir}/build")

    try:
        check_info(chall_dir)
        if os.path.exists(f"{chall_dir}/build/Dockerfile"):
            gen_chall_action(chall_dir)
        else:
            info("Skipping action generation, no Dockerfile found")
    except Exception as e:
        error(e)


def all_challs():
    for root, _, files in os.walk("challenges"):
        if "_template" in root:
            continue
        if "README.md" in files:
            name = root.split("/")[-1]
            heading(f"{f' {name} '.center(60, '=')}")
            try:
                check_info(root)
                if os.path.exists(f"{root}/build/Dockerfile"):
                    gen_chall_action(root)
                else:
                    info("Skipping action generation, no Dockerfile found")
            except Exception as e:
                error(e)


if __name__ == "__main__":
    info("Generating GitHub actions...")

    if args.all:
        all_challs()
    else:
        single_chall()
