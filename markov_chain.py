import json
import os
import random


class MarkovChain:
    def __init__(self) -> None:
        self.chains: dict[int, dict[str, dict[str, int]]] = {}

    def get_chain(self, guild_id: int) -> dict[str, dict[str, int]]:
        if guild_id not in self.chains:
            self.load(guild_id)

        return self.chains[guild_id]

    def process_words(self, words: list[str], guild_id: int):
        if not words:
            return

        chain = self.get_chain(guild_id)

        new_words = 0

        for i, word in enumerate(words):
            if not word.strip() or word == "__START__" or word == "__END__":
                continue

            if not word in chain:
                chain[word] = {}
                new_words += 1

            if i == 0:
                chain["__START__"][word] = chain["__START__"].get(word, 0) + 1

            if i < len(words) - 1:
                next_word = words[i + 1]
                chain[word][next_word] = chain[word].get(next_word, 0) + 1
            else:
                chain[word]["__END__"] = chain[word].get("__END__", 0) + 1

        if new_words > 0:
            print(f"📖 New words: {new_words} ({self.get_words_count(guild_id)} total)")

        self.save(guild_id, chain)

    def generate_message(self, max_length: int, guild_id: int) -> str:
        self.load(guild_id)

        chain = self.get_chain(guild_id)

        if not chain["__START__"]:
            raise Exception("The word chain is empty")

        START_WORD_TYPE = os.environ["START_WORD_TYPE"]

        if START_WORD_TYPE == "freq":
            start_words = list(chain["__START__"].keys())
            weights = list(chain["__START__"].values())
            first_word = random.choices(start_words, weights, k=1)[0]
        elif START_WORD_TYPE == "random":
            words = list(chain.keys())
            words.remove("__START__")
            first_word = random.choice(words)
        else:
            raise Exception("START_WORD_TYPE must be either freq or random")

        message = [first_word]

        i = 0

        while len(message) <= max_length:
            current_word = message[i]

            next_words = list(chain[current_word].keys())
            weights = list(chain[current_word].values())
            next_word = random.choices(next_words, weights, k=1)[0]

            if next_word == "__END__":
                break

            message.append(next_word)
            i += 1

        return " ".join(message)

    def get_words_count(self, guild_id: int) -> int:
        self.load(guild_id)

        chain = self.get_chain(guild_id)

        return len(chain) - 1

    def get_links_count(self, guild_id: int) -> int:
        self.load(guild_id)

        chain = self.get_chain(guild_id)

        return sum(len(inner) for inner in chain.values())

    def save(self, guild_id: int, chain: dict[str, dict[str, int]]) -> None:
        path = f"data/{guild_id}/words.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(f"data/{guild_id}/words.json", "w", encoding="utf8") as f:
            json.dump(chain, f, indent=2, ensure_ascii=False)

    def load(self, guild_id: int) -> None:
        path = f"data/{guild_id}/words.json"

        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            chain = {"__START__": {}}
            self.save(guild_id, chain)
        else:
            with open(path, "r", encoding="utf8") as f:
                chain = json.load(f)

        self.chains[guild_id] = chain
