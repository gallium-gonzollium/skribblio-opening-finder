
# Skribbl Opening Finder
This is a program that takes skribbl.io, a word-guessing-via-picture (pictogram) game, and takes all the words from it (in 4 languages) and converts it into a list that has the highest chance of getting a close word.
## What is a close word?
A word is *close* to another word if you can edit, insert, or remove one of it's letters and end up with the other word.

For example:

- `spine` is close to `shine` because the `p` got edited to an `h` and everything else is the same.
- `sine` is close to `shine` because an `h` got inserted and everything else is the same.
- `shibne` is close to `shine` because the `b` got removed from the word and everything else is the same.

Skribbl.io tells you if a word is close\*, to aid players in case they typo it\*\*. However this program takes advantage of that by providing a set of words that maximise the chances of getting a "close word" prompt.

\* 2-letter target words have close words disabled for the simple reason that there's very few of them (none in English, actually) and it would be a letter spam in game.
\*\* Diacritics don't matter except if it's a new letter entirely, like ß.

## How to generate it?
The program uses Python, so make sure you have some form of Python.
If you know how to use `git clone`, then simply clone it and run the python file.
If not, download the `skribblopeningfinder.py` file and a language file of your choice. Make sure to put both files in the same directory. Then run the `.py` file.
> [!NOTE]
If you choose English, an extra prompt will show: `Set difficulty priority first? (y/n)`. Choosing "n" will prioritize number of close words over difficulty, as usual, while choosing "y" will choose the opposite. It is less optimal but will increase chances of close words by probability of people picking it. However the data (graciously provided by [wlauyeung](https://github.com/wlauyeung/Skribblio-Word-Bank/)) is slightly scarce for calculating difficulty and mileage may vary.

