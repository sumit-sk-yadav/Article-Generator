"""Utility functions for the application"""
from datetime import datetime


def format_markdown_with_metadata(content: str, topic: str) -> str:
    """Format markdown content with metadata header"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    metadata = f"""---
title: Generated Article
topic: {topic}
generated: {timestamp}
generator: AI Content Generator
---

"""
    return metadata + content


def generate_filename(topic: str) -> str:
    """Generate a filename from the topic"""
    import re
    
    # Remove special characters and replace spaces with hyphens
    filename = re.sub(r'[^\w\s-]', '', topic.lower())
    filename = re.sub(r'[-\s]+', '-', filename)
    
    # Add timestamp to make it unique
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{filename}_{timestamp}.md"
