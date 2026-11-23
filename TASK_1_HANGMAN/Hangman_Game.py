import os
import random

# Define the ASCII gallows stages (0 to 6 errors)
HANGMAN_STAGES = [
    """
     +---+
         |
         |
         |
        ===
    """,
    """
     +---+
     O   |
         |
         |
        ===
    """,
    """
     +---+
     O   |
     |   |
         |
        ===
    """,
    """
     +---+
     O   |
    /|   |
         |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
         |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
    /    |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
    / \\  |
        ===
    """
]

WORDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")


def load_words(file_path=WORDS_FILE):
    """Loads words from a file, keeping only alphabetical words with 5+ letters."""
    with open(file_path, 'r', encoding='utf-8') as f:
        words = [
            line.strip().lower()
            for line in f
            if len(line.strip()) >= 5 and line.strip().isalpha()
        ]
    if not words:
        raise SystemExit(f"No usable words found in {file_path}")
    return words


def play_hangman(word_list):
    """Starts and runs an interactive game of Hangman."""
    secret_word = random.choice(word_list)
    guessed_letters = set()
    incorrect_guesses = 0
    max_attempts = 6

    print("=========================================")
    print("       WELCOME TO TERMINAL HANGMAN       ")
    print("=========================================")
    print(f"I have chosen a secret word with {len(secret_word)} letters.")

    while incorrect_guesses < max_attempts:
        # 1. Print current visual stage
        print(HANGMAN_STAGES[incorrect_guesses])

        # 2. Build and display the masked word
        displayed_word = " ".join(
            char.upper() if char in guessed_letters else "_" for char in secret_word
        )
        print(f"Word: {displayed_word}")

        # 3. Display history of guessed letters
        if guessed_letters:
            print(f"Guessed letters: {', '.join(sorted(guessed_letters)).upper()}")
        print(f"Remaining mistakes allowed: {max_attempts - incorrect_guesses}")
        print("-" * 40)

        # 4. Prompt user input
        guess = input("Guess a letter: ").strip().lower()

        # 5. Validate input
        if len(guess) != 1 or not guess.isalpha():
            print("\n[!] Invalid input. Please enter a single alphabetical character.")
            continue

        if guess in guessed_letters:
            print(f"\n[!] You have already guessed '{guess.upper()}'. Try a different one.")
            continue

        guessed_letters.add(guess)

        # 6. Check guess outcomes
        if guess in secret_word:
            print(f"\nGood job! '{guess.upper()}' is in the word.")
            # Check win condition
            if all(char in guessed_letters for char in secret_word):
                print(HANGMAN_STAGES[incorrect_guesses])
                print(f"\n🎉 CONGRATULATIONS! You guessed the word: {secret_word.upper()} 🎉")
                return
        else:
            incorrect_guesses += 1
            print(f"\nOops! '{guess.upper()}' is not in the word.")

    # Out of attempts - Game Over
    print(HANGMAN_STAGES[max_attempts])
    print("\n💀 GAME OVER! 💀")
    print(f"The secret word was: {secret_word.upper()}")


if __name__ == "__main__":
    words = load_words()
    play_hangman(words)
