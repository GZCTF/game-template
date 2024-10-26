# Game Template

This repository is used to store and build challenge images.

## Challenge Specification

For each challenge, a separate branch should be created, named `<category>/<challenge_name>`, and related operations should be performed in this branch, and finally squash merged into the main branch.

- Challenges should follow the GZCTF challenge specification, and the Dockerfile of the challenge should be placed in the `challenges` directory.
- You should add `chal.<category>.<challenge_name>.yml` to `.github/workflows` to build the challenge image, and put the `Dockerfile` in the `challenges` directory.
- If necessary, an issue or pr can be opened to track the progress of the challenge.
- Do not upload any big binary files to the repository, use other methods to share files.

**To generate the action file, use `python scripts/gen_action.py`. This script will check your challenge directory and generate the action file for you.**

## Challenges

|     | Title | Category | Difficulty | Author |
| :-: | :---- | :------- | :--------- | :----- |

### Statistics

| Category | Count | Ratio |
| :------- | :---- | :---- |

| Difficulty | Count | Ratio |
| :--------- | :---- | :---- |
| Baby       | 0     | 0.00% |
| Trivial    | 0     | 0.00% |
| Easy       | 0     | 0.00% |
| Normal     | 0     | 0.00% |
| Medium     | 0     | 0.00% |
| Hard       | 0     | 0.00% |
| Expert     | 0     | 0.00% |
| Insane     | 0     | 0.00% |
