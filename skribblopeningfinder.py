from collections import defaultdict
import os

def set_alphabet(name):
    alphabet = ["abcdefghijklmnopqrstuvwxyz","abcdefghijklmnopqrstuvwxyzäöüß123","abcdefghijklmnopqrstuvwxyzáéíóúüñ","abcdefghijklmnopqrstuvwxyzàâæçéèêëîïôœùûüÿ"]
    langs = ["en","de","es","fr"]
    return alphabet[langs.index(filename[9:11])]

def modify_words(words, commands):
    modified_set = set()
    alphabet = set_alphabet(filename)
    for word in words:
        for command in commands:
            if 'replace' in command:
                for index, letter in enumerate(word):
                    for replace_letter in alphabet:
                        modified_word = word[:index] + replace_letter + word[index+1:]
                        modified_set.add(modified_word.lower())
            elif 'insert' in command:
                for index in range(len(word) + 1):
                    for insert_letter in alphabet:
                        modified_word = word[:index] + insert_letter + word[index:]
                        modified_set.add(modified_word.lower())
            elif 'pop' in command:
                for index, _ in enumerate(word):
                    modified_word = word[:index] + word[index+1:]
                    modified_set.add(modified_word.lower())

    return modified_set

def find_similar_words(wordbank, size):
    words = {word[0].lower() for word in wordbank if word[1] == size}
    wordbank_map = {entry[0].lower(): entry[2] * (1 - entry[3]) for entry in wordbank}
    length = sum(size)+len(size)-1

    print(f"Generating all possible words of length {size}...")
    potential_words = modify_words(words, ['pop','replace'])
    similar_words_dict = defaultdict(list)
    processed_words = set()

    total_words = len(potential_words)
    for count, word in enumerate(potential_words, 1):
        if word in processed_words:
            continue
        processed_words.add(word)
        potential_similar = modify_words([word], ['insert', 'replace'])
        for _word in potential_similar:
            if _word in words:
                similar_words_dict[word].append(_word)
        if count % (50000//length) == 0:
            print(f"{count//1000*length}k/{total_words//1000*length}k, {int(count/total_words//0.01)}%")

    print("Sorting...")
    
    if difficulty_priority:
        sorted_similar_words = dict(sorted(similar_words_dict.items(),key=lambda item: (add_difficulty(item[1], wordbank_map), len(item[1]), -len(item[0])),reverse=True))
    else:
        sorted_similar_words = dict(sorted(similar_words_dict.items(),key=lambda item: (len(item[1]), add_difficulty(item[1], wordbank_map), -len(item[0])),reverse=True))

    print(f"Starting optimal word search of length {size}...")
    top = []
    cumulative_frequency = 0
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
        
        if top == 1 and not difficulty_priority:
            sorted_results = sorted(sorted_similar_words.items(), key=lambda item: (add_difficulty(item[1], wordbank_map), -len(item[0])), reverse=True)
        else:
            if difficulty_priority:
                sorted_results = sorted(sorted_similar_words.items(), key=lambda item: (add_difficulty(item[1], wordbank_map), len(item[1]), -len(item[0])), reverse=True)
            else:
                sorted_results = sorted(sorted_similar_words.items(), key=lambda item: (len(item[1]), add_difficulty(item[1], wordbank_map), -len(item[0])), reverse=True)
            if not sorted_results:
                break
        first_item, similar_list = sorted_results[0]
        top = len(similar_list)
        cumulative_frequency += top
        if cumulative_frequency/len(words) == 1.0:
            print(f"{format(first_item, length)} | {top} | 100.% | {', '.join(i for i in similar_list)}")
        elif top > 9:
            print(f"{format(first_item, length)} |{ top} | {format(cumulative_frequency/len(words)*1000//1/10,4)}% | {', '.join(i for i in similar_list)}")
        elif top == 1:
            print(f"{similar_list[0]} | 1 | {cumulative_frequency/len(words)*1000//1/10}% | {similar_list[0]}")
        else:
            print(f"{format(first_item, length)} | {top} | {format(cumulative_frequency/len(words)*1000//1/10,4)}% | {', '.join(i for i in similar_list)}")
    
        for _ in range(top): # for SOME reason doing 1 pass of this isn't enough...
            for word in similar_list:
                for key, value in list(sorted_similar_words.items()):
                    if word in value:
                        value.remove(word)
                        if not value:
                            del sorted_similar_words[key] 

    print("All words have been covered.")

def add_difficulty(word_list, wordbank_map):
    if filename == "wordbank-en.txt":
        common_words_scores = {word: wordbank_map[word] for word in set(word_list).intersection(wordbank_map.keys())}
        total_difficulty = sum(common_words_scores[word] for word in word_list if word in common_words_scores)
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
            print("Invalid number :p")

def wordbank_init(name):
    wordbank = []
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    unique_chars = set()

    with open(file_path, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
    
    for i in range(0, len(lines), 4):
        sublist = lines[i:i+4]

        # Extract and parse data for the sublist
        word = sublist[0].strip()
        indices_str = sublist[1].strip()[1:-1]  # Remove square brackets
        indices = [int(idx) for idx in indices_str.split(',')]
        value1 = int(sublist[2].strip())
        value2 = float(sublist[3].strip())

        # Create the sublist and append to wordbank
        sublist_data = [word, indices, value1, value2]
        wordbank.append(sublist_data)
    return wordbank
    
def main():
    global difficulty_priority, difficulty_dict, filename

    filename = ["wordbank-en.txt","wordbank-de.txt","wordbank-es.txt","wordbank-fr.txt"]\
        [intput("Language file to use?\n0 - English\n1 - German\n2 - Spanish\n3 - French\n>>> ",4)]
    
    print("Using: " + filename)
    wordbank = wordbank_init(filename)
    size = [intput(f"Enter length for word #{i+1}:\n>>> ") for i in range(intput("How many words?\n>>> ",10))]
    if filename == "wordbank-en.txt":
        if input("Set difficulty priority first? (y/n)\n>>> ").lower() == "y":
            difficulty_priority = True
        else:
            difficulty_priority = False
    else:
        difficulty_priority = False
    difficulty_dict = {entry[0].lower(): entry[2] * (1 - entry[3]) for entry in wordbank}
    find_similar_words(wordbank, size)

try:
    main()
except KeyboardInterrupt:
    print(f"Exiting...")
    exit()