# Cheburek

Discord bot that generates text messages using the Markov chain.

## Features

- Text generation based on the messages that were sent by users
- Meme image generation
- Statistics of the learned words

## How to start

Run Cheburek using Docker:

```sh
docker run --name cheburek \
    -e TOKEN="your Discord bot token" \
    -e START_WORD_TYPE="random" \
    -e MESSAGE_CHANCE="0.1" \
    ghcr.io/zorreth/cheburek:latest
```

Or clone repository and run it using uv:

1. Clone the repository:
   ```sh
   git clone https://github.com/zorreth/cheburek
   ```
2. Start the bot using uv:
   ```sh
   uv run main.py
   ```

## Credits

- Idea & implementation by `zorreth`
- Profile picture by `re.alexa`
