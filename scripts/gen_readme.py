from utils import *


def gen_chall_table(challenges):
    table = "\n## Challenges\n\n"
    table += "| | Title | Category  | Difficulty | Author |\n"
    table += "| :-: | :- | :- | :- | :- |\n"
    count = {}
    count_diff = {}

    # challenges sorted by difficulty then category then title
    challenges.sort(key=lambda x: (difficulties.index(x[3]), x[2], x[1]))

    for i, (name, path, category, difficulty, author) in enumerate(challenges):
        table += f'| {i+1} | [{name}](challenges/{path.split("/", 1)[1]}) | {category} | {difficulty} | {author} |\n'
        count[category] = count.get(category, 0) + 1
        count_diff[difficulty] = count_diff.get(difficulty, 0) + 1

    challenge_count = max(1, len(challenges))

    table += "\n"

    table += "### Statistics\n\n"

    table += "| Category | Count | Ratio |\n"
    table += "| :- | :- | :- |\n"
    for category, num in count.items():
        table += f"| {category} | {num} | {num/challenge_count:.2%} |\n"

    table += "\n"

    table += "| Difficulty | Count | Ratio |\n"
    table += "| :- | :- | :- |\n"
    for diff in difficulties:
        num = count_diff.get(diff, 0)
        table += f"| {diff} | {num} | {num/challenge_count:.2%} |\n"

    return table


def main():
    challenges = get_chall_list()
    table = gen_chall_table(challenges)

    with open("scripts/note.md", "r") as f:
        base = f.read()

    with open("README.md", "w") as f:
        f.write(base + table)


if __name__ == "__main__":
    if not os.path.exists("challenges"):
        print(
            "[!] Please run this script from the root directory with `python scripts/gen_action.py`"
        )
        exit(1)

    main()
