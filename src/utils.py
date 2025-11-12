"""Utility functions for the application"""
from datetime import datetime


def format_markdown_with_metadata(content, topic):
    """
    Format content with markdown metadata header (without saving to file)
    
    Args:
        content: The blog post content
        topic: Topic name for metadata
    
    Returns:
        str: Formatted markdown content with frontmatter
    """
    markdown_content = f"""---
title: {topic}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
generated_by: CrewAI Pipeline
---

{content}
"""
    return markdown_content


def generate_filename(topic):
    """
    Generate a safe filename from topic
    
    Args:
        topic: Topic string
    
    Returns:
        str: Safe filename with timestamp
    """
    safe_filename = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_filename = safe_filename.replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe_filename}_{timestamp}.md"
