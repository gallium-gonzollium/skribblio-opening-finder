from collections import defaultdict
import os
import unicodedata

def remove_diacritics(input_str):
    return ''.join(
        c for c in unicodedata.normalize('NFD', input_str)
        if unicodedata.category(c) != 'Mn'
    )

def set_alphabet(name):
    alphabet = {
        "wordbank-en.txt": "abcdefghijklmnopqrstuvwxyz",
        "wordbank-de.txt": "abcdefghijklmnopqrstuvwxyzäöüß123",
        "wordbank-es.txt": "abcdefghijklmnopqrstuvwxyzáéíóúüñ25",
        "wordbank-fr.txt": "abcdefghijklmnopqrstuvwxyzàâæçéèêëîïôœùûüÿ9",
    }
    return alphabet.get(name)

try:
    color_capable = input("Use color? (y/n)\n>>> ").lower() == "y"
except: 
    raise SystemExit(0)

def ansi(color_code):
    return color_code if color_capable else ''

class Colors:
    class fg:
        BLACK = ansi('\033[30m')
        RED = ansi('\033[31m')
        GREEN = ansi('\033[32m')
        YELLOW = ansi('\033[33m')
        BLUE = ansi('\033[34m')
        MAGENTA = ansi('\033[35m')
        CYAN = ansi('\033[36m')
        WHITE = ansi('\033[37m')
        BRIGHT_BLACK = ansi('\033[90m')
        BRIGHT_RED = ansi('\033[91m')
        BRIGHT_GREEN = ansi('\033[92m')
        BRIGHT_YELLOW = ansi('\033[93m')
        BRIGHT_BLUE = ansi('\033[94m')
        BRIGHT_MAGENTA = ansi('\033[95m')
        BRIGHT_CYAN = ansi('\033[96m')
        BRIGHT_WHITE = ansi('\033[97m')

    class bg:
        BLACK = ansi('\033[40m')
        RED = ansi('\033[41m')
        GREEN = ansi('\033[42m')
        YELLOW = ansi('\033[43m')
        BLUE = ansi('\033[44m')
        MAGENTA = ansi('\033[45m')
        CYAN = ansi('\033[46m')
        WHITE = ansi('\033[47m')
        BRIGHT_BLACK = ansi('\033[100m')
        BRIGHT_RED = ansi('\033[101m')
        BRIGHT_GREEN = ansi('\033[102m')
        BRIGHT_YELLOW = ansi('\033[103m')
        BRIGHT_BLUE = ansi('\033[104m')
        BRIGHT_MAGENTA = ansi('\033[105m')
        BRIGHT_CYAN = ansi('\033[106m')
        BRIGHT_WHITE = ansi('\033[107m')

    class fm:
        RESET_ALL = ansi('\033[0m')
        BOLD = ansi('\033[1m')
        ITALIC = ansi('\033[3m')
        UNDERLINE = ansi('\033[4m')
        BLINK = ansi('\033[5m')
        REVERSE = ansi('\033[7m')
        HIDDEN = ansi('\033[8m')
        UNBOLD = ansi('\033[22m')
        UNITALIC = ansi('\033[23m')
        UNUNDERLINE = ansi('\033[24m')

def colorize_output(inp):
    return Colors.fg.BRIGHT_WHITE + inp[0:length] + \
           Colors.fm.BOLD + \
           Colors.fg.BLACK + inp[length:length+2] + \
           Colors.fm.UNBOLD + \
           Colors.fg.YELLOW + inp[length+2:length+5] + \
           Colors.fm.BOLD + \
           Colors.fg.BLACK + inp[length+5] + \
           Colors.fm.UNBOLD + \
           Colors.fg.BRIGHT_GREEN + inp[length+6:length+11] + \
           Colors.fg.GREEN + inp[length+11:length+13] + \
           Colors.fm.BOLD + \
           Colors.fg.BLACK + inp[length+13] + \
           Colors.fm.UNBOLD + \
           Colors.fg.BRIGHT_BLUE + inp[length+14:]


def modify_words(words, command):
    modified_set = set()
    alphabet = set_alphabet(filename)
    for word in words:
        if "replace" == command:
            for index, _ in enumerate(word):
                for replace_letter in alphabet:
                    modified_word = word[:index] + replace_letter + word[index + 1:]
                    modified_set.add(modified_word.lower())
        elif "insert" == command:
            for index in range(len(word) + 1):
                for insert_letter in alphabet:
                    modified_word = word[:index] + insert_letter + word[index:]
                    modified_set.add(modified_word.lower())
        elif "pop" == command:
            for index, _ in enumerate(word):
                modified_word = word[:index] + word[index + 1 :]
                modified_set.add(modified_word.lower())

    return modified_set


def find_similar_words(wordbank, size):
    words = {word[0].lower() for word in wordbank if word[1] == size}
    wordbank_map = {entry[0].lower(): entry[2] * (1 - entry[3]) for entry in wordbank}
    global length
    length = sum(size) + len(size) - 1

    print(f"{Colors.fg.RED}Generating all possible words of length {Colors.fg.YELLOW}{str(size)[1:-1]}{Colors.fg.RED}...")
    potential_pop_words = modify_words(words, "pop")
    potential_replace_words = modify_words(words, "replace")

    similar_words_dict = defaultdict(list)
    processed_words = set()
    total_words = len(potential_pop_words) + len(potential_replace_words)

    for words_list in [potential_pop_words, potential_replace_words]:
        for count, word in enumerate(words_list, 1):
            processed_words.add(word)
            action_type = "insert" if words_list is potential_pop_words else "replace"
            potential_similar = modify_words([word], action_type)
            for _word in potential_similar:
                if _word in words:
                    similar_words_dict[word].append(_word)
            if count % (100000 // length) == 0:
                print(
                    f"{Colors.fg.YELLOW}{count//1000*length}k{Colors.fg.BRIGHT_WHITE}/\
{                     Colors.fg.BRIGHT_YELLOW}{total_words//1000*length}k{Colors.fg.BRIGHT_WHITE}, \
{                     Colors.fg.BRIGHT_CYAN}{int(count/total_words//0.01)}%")

    print(f"{Colors.fg.BRIGHT_RED}Starting optimal word search of length {Colors.fg.YELLOW}{str(size)[1:-1]}{Colors.fg.BRIGHT_RED}...")
    compute_optimal_words(similar_words_dict, wordbank_map, words)


def compute_optimal_words(sorted_similar_words, wordbank_map, words):
    top = 0
    cumulative = 0
    passes = [0, 0]
    end = False
    while sorted_similar_words:
        processed_values = set()
        keys_to_delete = []
        for key, value in sorted_similar_words.items():
            if any(v in processed_values for v in value) and len(value) == 1:
                keys_to_delete.append(key)
            else:
                processed_values.update(value)

        for key in keys_to_delete:
            del sorted_similar_words[key]

        if top == 1 and not difficulty_priority and end == False:
            sorted_results = sorted(
                sorted_similar_words.items(),
                key=lambda item: (add_difficulty(item[1], wordbank_map), -len(item[0])),
                reverse=True,
            )
        else:
            if difficulty_priority and end == False:
                sorted_results = sorted(
                    sorted_similar_words.items(),
                    key=lambda item: (
                        add_difficulty(item[1], wordbank_map),
                        len(item[1]),
                        -len(item[0]),
                    ),
                    reverse=True,
                )
            elif end == False:
                sorted_results = sorted(
                    sorted_similar_words.items(),
                    key=lambda item: (
                        len(item[1]),
                        add_difficulty(item[1], wordbank_map),
                        -len(item[0]),
                    ),
                    reverse=True,
                )
            elif sorted_results != sorted_similar_words.items():
                sorted_results = sorted(sorted_similar_words.items(), key=None)
            if not sorted_results:
                break
        
        first_item, similar_list = sorted_results[0]
        top = len(similar_list)
        if top != 1:
            passes[1] += 1
        elif passes[1] == passes[0] and cumulative / len(words) < 0.95 and difficulty_priority == False:
            if (input(f"{Colors.fg.BRIGHT_CYAN}The rest {Colors.fg.BRIGHT_YELLOW}{format(100-cumulative/len(words)//0.001/10,4)}% {Colors.fg.BRIGHT_CYAN}are now 1 letter.\
    \n{Colors.fg.BRIGHT_MAGENTA}Press enter to continue, or type 'end' to end the program.\n{Colors.fg.BRIGHT_WHITE}>>> {Colors.fg.BRIGHT_YELLOW}").lower()
                in ["end","edn","den","dne","ned","ned"]):
                end = True
                print(Colors.fg.BLUE+"Ending...")
        passes[0] += 1
        cumulative += top

        if not end:
            if cumulative == len(words):
                print(colorize_output(
                    f"{remove_diacritics(similar_list[0])} | {top} | 100.% | {', '.join(i for i in similar_list)}"))
            elif top > 9:
                print(colorize_output(
                    f"{remove_diacritics(format(first_item, length))} |{ top} | {format(cumulative/len(words)*100,4)}% | {', '.join(i for i in similar_list)}"))
            elif top == 1:
                print(colorize_output(
                    f"{remove_diacritics(similar_list[0])} | 1 | {format(cumulative/len(words)*10000//1/100,4)}% | {similar_list[0]}"))
            else:
                print(colorize_output(
                    f"{remove_diacritics(format(first_item, length))} | {top} | {format(cumulative/len(words)*100,4)}% | {', '.join(i for i in similar_list)}"))

        for _ in range(top):  # for SOME reason doing 1 pass of this isn't enough...
            for word in similar_list:
                for key, value in list(sorted_similar_words.items()):
                    if word in value:
                        value.remove(word)
                        if not value:
                            del sorted_similar_words[key]

    print(f"{Colors.fg.BRIGHT_MAGENTA}All {Colors.fg.BRIGHT_YELLOW}{len(words)}{Colors.fg.BRIGHT_MAGENTA} \
words have been covered in {Colors.fg.BRIGHT_YELLOW}{passes[0]}{Colors.fg.BRIGHT_MAGENTA} words.")
    try:
        print(f"{Colors.fg.BRIGHT_GREEN}number of list words (>1 close)         {Colors.fg.BLACK} = {Colors.fg.BRIGHT_YELLOW}\
{format(str(passes[1])+' words',10) } {Colors.fm.BOLD+Colors.fg.BLACK}|{Colors.fm.UNBOLD+Colors.fg.BLUE} higher is better")
        print(f"{Colors.fg.BRIGHT_GREEN}avg. efficiency per list word           {Colors.fg.BLACK} = {Colors.fg.BRIGHT_YELLOW}\
{format(len(words)/passes[0],5)}      {Colors.fm.BOLD+Colors.fg.BLACK}|{Colors.fm.UNBOLD+Colors.fg.BLUE} higher is better")
    except ZeroDivisionError:
        0
    try:
        input(Colors.fg.RED + Colors.bg.BLACK + Colors.fm.BOLD + "Press enter to restart, or press CTRL-C to close.\n" + Colors.fm.RESET_ALL)
    except KeyboardInterrupt:
        raise SystemExit


def add_difficulty(word_list, wordbank_map):
    if filename == "wordbank-en.txt" or use_difficulty:
        common_words_scores = {
            word: wordbank_map[word]
            for word in set(word_list).intersection(wordbank_map.keys())
        }
        total_difficulty = sum(
            common_words_scores[word]
            for word in word_list
            if word in common_words_scores
        )
        return total_difficulty
    else:
        return 0


def format(x, length):
    x = str(x)
    while len(x) < length:
        x += " "
    while len(x) > length:
        x = x[:-1]
    return x


def intput(x, threshold=100):
    while True:
        try:
            out = int(input(x))
            if out < threshold:
                return out
            else:
                raise ValueError
        except ValueError:
            print(Colors.fg.RED + "Invalid number :p")
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print(Colors.fm.RESET_ALL)


def wordbank_init(name):
    wordbank = []
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

    with open(file_path, mode="r", encoding="utf-8") as file:
        lines = file.readlines()

    for i in range(0, len(lines), 4):
        sublist = lines[i : i + 4]

        # Extract and parse data for the sublist
        word = sublist[0].strip()
        indices_str = sublist[1].strip()[1:-1]  # Remove square brackets
        indices = [int(idx) for idx in indices_str.split(",")]
        value1 = int(sublist[2].strip())
        value2 = float(sublist[3].strip())

        # Create the sublist and append to wordbank
        sublist_data = [word, indices, value1, value2]
        wordbank.append(sublist_data)
    return wordbank

def start():
    global difficulty_priority, difficulty_dict, filename, use_difficulty

    use_difficulty = False

    filename = [
        "wordbank-en.txt",
        "wordbank-de.txt",
        "wordbank-es.txt",
        "wordbank-fr.txt",
        0][intput(
f"""{Colors.fm.RESET_ALL + Colors.fg.BRIGHT_WHITE}Language file to use?
0 - English
1 - German
2 - Spanish
3 - French
4 - Custom File
>>> {Colors.fg.BRIGHT_YELLOW}""",5)]
    
    if filename == 0:
        while True:
            try:
                filename = input(Colors.fg.BRIGHT_CYAN + f"Enter the file name of your wordbank.\n{Colors.fg.BRIGHT_WHITE}>>> ")
                wordbank = wordbank_init(filename)
                break
            except FileNotFoundError:
                print(Colors.fg.BRIGHT_RED + "#@# That file doesn't exist. Try again. #@#")
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                print(f"""
{Colors.fm.UNDERLINE+Colors.fg.RED}In case you don't know how the wordbank works:{Colors.fm.UNUNDERLINE}

{Colors.fg.BRIGHT_GREEN}Every 4 lines is one entry for a word. The format is like this:
    
{Colors.fg.BRIGHT_YELLOW}    Line 1: {Colors.fg.CYAN}the word itself.
{Colors.fg.BRIGHT_YELLOW}    Line 2: {Colors.fg.BRIGHT_CYAN}the length of each word, e.g. "cat" is [3], and "sussy baka" is [5,4]. There must not be any whitespace.
{Colors.fg.BRIGHT_YELLOW}    Line 3: {Colors.fg.CYAN}frequency, measured as a whole number.
{Colors.fg.BRIGHT_YELLOW}    Line 4: {Colors.fg.CYAN}difficulty, a decimal from 0 to 1, where lower is easier.

{Colors.fg.RED}There should not be anything else in the file, because that will cause an error.
{Colors.fg.MAGENTA}If you have not measured frequency and difficulty, set lines 3 and 4 to 0.
""")
                input(Colors.fg.BRIGHT_RED+Colors.fm.UNDERLINE+ f"#@# The wordbank '{filename[:20]}{'...' if len(filename) >= 20 else ''}' has a problem. Press enter to see the error. #@#" + Colors.fm.RESET_ALL)
                wordbank_init(filename)
        use_difficulty = not input(
            f"{Colors.fg.BRIGHT_MAGENTA}Does the file have difficulty and frequency? (y/n)\n{Colors.fg.BRIGHT_WHITE}>>> {Colors.fg.BRIGHT_YELLOW}").lower() == 'n'
    use_difficulty |= filename == "wordbank-en.txt"
    
    print(Colors.fg.BRIGHT_GREEN + "Using: " +filename)
    wordbank = wordbank_init(filename)
    size = [
        intput(f"{Colors.fg.BRIGHT_CYAN}Enter length for word #{i+1}:\n{Colors.fg.BRIGHT_WHITE}>>> {Colors.fg.BRIGHT_YELLOW}")
        for i in range(intput(Colors.fg.BRIGHT_BLUE + f"How many words?\n{Colors.fg.BRIGHT_WHITE}>>> {Colors.fg.BRIGHT_YELLOW}", 10))
    ]
    if filename == "wordbank-en.txt" or use_difficulty:
        i = None
        while i not in ["y","n"]:
            i = input(f"{Colors.fg.BRIGHT_MAGENTA}Set difficulty priority first? (y/n)\n{Colors.fg.BRIGHT_WHITE}>>> {Colors.fg.BRIGHT_YELLOW}").lower()
            if i == "y":
                difficulty_priority = True
            elif i == "n":
                difficulty_priority = False
    else:
        difficulty_priority = False
    difficulty_dict = {entry[0].lower(): entry[2] * (1 - entry[3]) for entry in wordbank}
    find_similar_words(wordbank, size)

def main():
    global restart
    restart = True
    while restart: 
        try:
            start()
        except KeyboardInterrupt: # This stupid mess is me trying to stop stinking EOFError leaking through while doing KeyboardInterrupt...
            try:
                if input(Colors.fg.RED + f"Would you like to exit? (y/n)\n{Colors.fg.BRIGHT_WHITE}>>> " + Colors.fg.BRIGHT_YELLOW).lower() in ['y','','yes']:
                    restart = False
            except KeyboardInterrupt:
                restart = False
            except EOFError:
                try:
                    print(Colors.fg.BRIGHT_RED + "#@# Hit an EOFError, exiting... #@#" + Colors.fm.RESET_ALL)
                    raise SystemExit(1)
                except:
                    raise SystemExit(1)
    try:
        print(Colors.fm.RESET_ALL, end='')
        raise SystemExit(0)
    except KeyboardInterrupt:
        raise SystemExit(0)

main()