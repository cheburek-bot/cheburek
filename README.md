# Cheburek

Discord bot that generates text messages using the Markov chain.

## Features

- Per-server data storage (words & images)
- Text generation based on messages sent by users
- Learned words & word connections statistics
- Meme generation

## How to start

Run Cheburek using Docker Compose:

1. Create a file named `docker-compose.yml`
   ```yaml
   services:
     cheburek:
       image: ghcr.io/zorreth/cheburek:latest
       restart: always
       environment:
         - TOKEN=<your bot token>
         - START_WORD_TYPE=random
         - MESSAGE_CHANCE=0.05
       volumes:
         - ./data:/usr/src/app/data
   ```
2. Run Cheburek
   ```sh
   docker compose up -d
   ```

Or clone repository and run Cheburek using uv:

1. Clone the repository
   ```sh
   git clone https://github.com/zorreth/cheburek
   ```
2. Copy and configure `.env`
   ```sh
   cp .env.example .env
   ```
3. Start the bot using uv
   ```sh
   uv run main.py
   ```

## Credits

- Idea & implementation by `zorreth`
- Profile picture by `re.alexa`
