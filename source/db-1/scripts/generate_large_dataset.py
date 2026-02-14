#!/usr/bin/env python3
"""
Generate Large Dataset for db-1 Chat Messaging Platform.
Generates ~1 GB of profiles, chats, messages, chat_participants data.
"""

import logging
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE = Path(__file__).parent.parent / 'data'
TARGET = 1.0 * 1024**3  # 1 GB

SAMPLE_CONTENT = [
    "Hello, how are you?", "Great meeting today!", "Let me check that.",
    "I'll get back to you.", "Thanks for the update.", "Sounds good.",
    "Can we schedule for tomorrow?", "Here's the document.", "Review when you can.",
] * 100  # Longer content for more bytes per message


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    all_sql = []
    size = 0

    # Seed: 10k profiles, 50k chats
    logger.info("Seeding profiles and chats...")
    profile_ids = []
    for i in range(10000):
        uid = str(uuid.uuid4())
        profile_ids.append(uid)
        all_sql.append(f"""INSERT INTO profiles (id, username, email, display_name) VALUES
('{uid}', 'user{i}', 'user{i}@example.com', 'User {i}')
ON CONFLICT (username) DO NOTHING;""")

    chat_ids = []
    creator_ids = []
    for i in range(50000):
        cid = str(uuid.uuid4())
        chat_ids.append(cid)
        creator = random.choice(profile_ids)
        creator_ids.append(creator)
        all_sql.append(f"""INSERT INTO chats (id, created_by, title) VALUES
('{cid}', '{creator}', 'Chat {i}')
ON CONFLICT (id) DO NOTHING;""")

    for s in all_sql:
        size += len(s.encode('utf-8'))

    logger.info("Generating messages (main bulk)...")
    msg_count = 0
    while size < TARGET:
        for _ in range(10000):
            chat_id = random.choice(chat_ids)
            sender_id = random.choice(profile_ids)
            content = random.choice(SAMPLE_CONTENT) + " " * random.randint(0, 200)
            is_ai = random.choice([True, False])
            t = datetime.now() - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
            mid = str(uuid.uuid4())
            s = f"""INSERT INTO messages (id, chat_id, sender_id, is_ai, content, created_at) VALUES
('{mid}', '{chat_id}', '{sender_id}', {str(is_ai).upper()}, '{content.replace("'", "''")[:1000]}', '{t}')
ON CONFLICT (id) DO NOTHING;"""
            all_sql.append(s)
            size += len(s.encode('utf-8'))
            msg_count += 1
        if msg_count % 100000 == 0:
            logger.info(f"  {msg_count:,} messages, {size/(1024**3):.2f} GB")
        if size >= TARGET:
            break

    out = BASE / 'data_large.sql'
    with open(out, 'w') as f:
        f.write('\n'.join(all_sql))
    logger.info(f"Done: {out} ({out.stat().st_size/(1024**3):.2f} GB)")


if __name__ == '__main__':
    main()
