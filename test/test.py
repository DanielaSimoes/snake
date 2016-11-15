# python script to test the commit, save the time and the score with the commit
import json
import subprocess


def get_git_commit_hash():
    return subprocess.check_output(['git', 'describe', '--always'])


def main():
    pass


def store(stats, entries):
    with open('data.json') as data_file:
        data = json.load(data_file)

    commit = get_git_commit_hash()

    for row in data:
        if row["commit"] == commit:
            data.remove(row)
            data.append({
                "commit": commit,
                "stats": stats,
                "entries": entries
            })
            break

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


if __name__ == '__main__':
    main()
