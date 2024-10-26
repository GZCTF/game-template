import os
import re


def get_challenge_info(path):
    with open(path, 'r') as f:
        content = f.read()
        name = re.search(r'# (.*)', content).group(1)
        author = re.search(r'\*\*Author:\*\* (.*)', content).group(1)
        difficulty = re.search(r'\*\*Difficulty:\*\* (.*)', content).group(1)
        category = re.search(r'\*\*Category:\*\* (.*)', content).group(1)
        flag = re.search(r'\*\*Flag:\*\* `(.*)`', content)
        if flag:
            flag = flag.group(1)
    return name, author, difficulty, category, flag


def get_chall_list():
    challenges = []
    for root, _, files in os.walk('challenges'):
        if "_template" in root:
            continue
        for file in files:
            if file == 'README.md':
                path = os.path.join(root, file)
                name, author, difficulty, category, _ = get_challenge_info(
                    path)
                challenges.append((name, root, category, difficulty, author))
    challenges.sort(key=lambda x: (x[2], x[3]))
    return challenges


difficulties = ['Baby', 'Trivial', 'Easy',
                'Normal', 'Medium', 'Hard', 'Expert', 'Insane']

categories = [
    'Misc', 'Crypto', 'Pwn', 'Web', 'Reverse',
    'Blockchain', 'Forensics', 'Hardware',
    'Mobile', 'PPC', 'AI', 'Pentest', 'OSINT'
]

lower_categories = [cate.lower() for cate in categories]


short_categories = ['misc', 'cr', 'pwn', 'web', 're', 'bc', 'fo', 'hw',
                    'mo', 'ppc', 'ai', 'pt', 'osint']

long_cate = {short: cate for short,
             cate in zip(short_categories, categories)}

short_cate = {cate: short for short,
              cate in zip(short_categories, categories)}
