# python script to test the commit, save the time and the score with the commit
import json
import subprocess
import os.path
from functools import reduce
import uuid
from shutil import move


agent_name = "DC"
other_name = "Agent1"

ITERATIONS = 100


def get_git_commit_hash():
    return str(subprocess.check_output(['git', 'describe', '--always'])).replace("\\n", "").replace("b'", "").replace("'", "")


def clean():
    subprocess.Popen(['rm', '-rf', get_git_commit_hash()],
                     cwd=os.path.abspath(__file__ + "/../"))
    subprocess.Popen(['mkdir', "-p", get_git_commit_hash() + "/traceback"],
                     cwd=os.path.abspath(__file__ + "/../"))
    subprocess.Popen(['mkdir', "-p", get_git_commit_hash() + "/took"],
                     cwd=os.path.abspath(__file__ + "/../"))
    subprocess.Popen(['mkdir', "-p", get_git_commit_hash() + "/lose"],
                     cwd=os.path.abspath(__file__ + "/../"))
    subprocess.Popen(['mkdir', "-p", get_git_commit_hash() + "/else"],
                     cwd=os.path.abspath(__file__ + "/../"))
    subprocess.Popen(['mkdir', "-p", get_git_commit_hash() + "/all_dead"],
                     cwd=os.path.abspath(__file__ + "/../"))


def exit_image(problem, err):
    unique_id = str(uuid.uuid4())

    move("../debug.jpeg", get_git_commit_hash() + "/" + problem + "/" + unique_id + ".jpeg")

    text_file = open(get_git_commit_hash() + "/" + problem + "/" + unique_id + ".txt", "w")
    text_file.write(str(err))
    text_file.close()


def main():
    entries = []
    i = 0

    while i < ITERATIONS:
        process = subprocess.Popen(['python3', 'start.py'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=os.path.abspath(__file__ + "/../../"))
        out, err = process.communicate()

        if "All dead" in str(err):
            exit_image("all_dead", err)

        elif "Traceback" in str(err):
            exit_image("traceback", err)

        elif agent_name + "> took" in str(err):
            exit_image("took", err)

        elif agent_name + " is the Winner" in str(err):
            try:
                score = int(str(err).split(" " + agent_name + "\\n")[-2].split(" ")[-1])
            except Exception:
                try:
                    score = int(str(err).split("INFO:Player <" + agent_name + "> points: ")[-1])
                except Exception:
                    score = 0  # error of parsing

            entry = {
                "score": score,
                "win": True
            }
            entries.append(entry)
        elif other_name + " is the Winner" in str(err):
            try:
                score = int(str(err).split("INFO:" + other_name + " ")[-1].split(" ")[0])
            except Exception:
                score = 0

            entry = {
                "score": score,
                "win": False
            }
            entries.append(entry)

            # debug only! remove to test
            exit_image("lose", err)
        else:
            exit_image("else", err)

        i += 1
        print(i)

    return entries


def store(entries):
    with open('data.json') as data_file:
        data = json.load(data_file)

    stats = {
      "score": {
        "mean": reduce(lambda r, h: r + h["score"], entries, 0)/len(entries),
        "max": reduce(lambda r, h: h["score"] if h["score"] > r else r, entries, 0),
        "min": reduce(lambda r, h: h["score"] if h["score"] < r else r, entries, 0)
      },
      "win": reduce(lambda r, h: r + int(h["win"]), entries, 0)/len(entries)*100
    }

    commit = get_git_commit_hash()

    for row in data:
        if row["commit"] == commit:
            data.remove(row)
            break

    data.append({
        "commit": commit,
        "stats": stats
    })

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


if __name__ == '__main__':
    clean()
    entries = main()
    store(entries)
