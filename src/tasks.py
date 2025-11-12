"""Task definitions for the content generation crew"""
from crewai import Task
from crewai_tools import TavilySearchTool


def create_plan_task(planner_agent):
    """Create planning task - storytelling focus"""
    search_tool = TavilySearchTool()
    
    return Task(
        description=(
            "Research {topic} and design a story-driven content plan:\n\n"
            "1. OPENING HOOK (crucial):\n"
            "   - Personal anecdote related to topic\n"
            "   - OR surprising statistic that challenges assumptions\n"
            "   - OR relatable problem/scenario that draws readers in\n"
            "   - OR provocative question that creates curiosity\n\n"
            "2. STORY ARC (narrative structure, not outline):\n"
            "   - Setup: Introduce the topic through the hook's lens\n"
            "   - Development: 4-6 main insights/themes (plan these as story beats, not section headers)\n"
            "   - Resolution: What readers should do with this knowledge\n\n"
            "3. RESEARCH (to support the narrative):\n"
            "   - Find 3-5 credible sources with specific data\n"
            "   - Locate real-world examples or case studies\n"
            "   - For technical topics: identify code examples to demonstrate concepts\n"
            "   - For non-technical topics: find personal stories or expert experiences\n\n"
            "4. CONTENT INTEGRATION (not segregation):\n"
            "   - Plan how to weave statistics into flowing paragraphs (not bullet lists)\n"
            "   - Identify where examples naturally emerge in the narrative\n"
            "   - Note transition points between main themes\n\n"
            "AVOID planning for:\n"
            "- 'Target Audience Analysis' sections\n"
            "- 'SEO Strategy' sections\n"
            "- Bullet-pointed pain points or features\n"
            "- Marketing comparison tables\n\n"
            "OUTPUT: Story outline with narrative arc, hook ideas, key insights, sources, and examples"
        ),
        expected_output=(
            "Story-driven content plan with: compelling hook idea, narrative arc (4-6 main themes), "
            "research sources with data points, examples to illustrate concepts, transition notes between themes"
        ),
        tools=[search_tool],
        agent=planner_agent,
    )


def create_write_task(writer_agent, plan_task):
    """Create writing task - narrative focus"""
    return Task(
        description=(
            "Write a 2000-2500 word Medium article on {topic} that tells a story:\n\n"
            "STRUCTURE:\n"
            "# Engaging Title (curiosity-driven, not keyword-stuffed)\n\n"
            "Opening (200-300 words):\n"
            "- Start with the hook from the content plan\n"
            "- Draw readers in with a story, question, or surprising fact\n"
            "- Establish why this topic matters through narrative, not bullet points\n\n"
            "Main Body (1500-1800 words, organized in numbered sections):\n"
            "- Use ## 1. Section Title, ## 2. Section Title format\n"
            "- Each section: 300-400 words of flowing paragraphs (NOT bullet lists)\n"
            "- Weave in statistics naturally: 'Research shows that...' or 'According to...'\n"
            "- Include 3-5 practical demonstrations:\n"
            "  * For technical: code blocks with conversational explanations\n"
            "  * For non-technical: real-world examples or personal anecdotes\n"
            "- Use smooth transitions between sections (not just new headers)\n\n"
            "Conclusion (200-300 words):\n"
            "- Reflect on what was covered\n"
            "- Provide forward-looking perspective or call to action\n"
            "- End with memorable closing thought\n\n"
            "WRITING STYLE (critical):\n"
            "✅ DO:\n"
            "- Write in conversational first/second person ('I discovered...', 'You might wonder...')\n"
            "- Use short paragraphs (3-5 sentences max)\n"
            "- Vary sentence length and rhythm\n"
            "- Weave data into narrative: 'A recent study found that 75% of projects fail, "
            "which explains why developers are turning to...'\n"
            "- Use concrete examples: 'Take Stripe, for instance—they reduced API calls by...'\n"
            "- Include genuine insights, not obvious observations\n\n"
            "❌ DON'T:\n"
            "- Create sections called 'Target Audience', 'Pain Points', 'SEO Strategy'\n"
            "- Use bullet lists for features, pain points, or statistics\n"
            "- Write marketing speak ('revolutionize', 'game-changer', 'next-gen')\n"
            "- Include meta-commentary about article structure\n"
            "- Add keyword-stuffed meta descriptions or SEO sections\n"
            "- Write in passive voice or academic tone\n\n"
            "EXAMPLES INTEGRATION:\n"
            "Technical topics: Include 3-5 code examples with setup like:\n"
            "'Here's how you'd implement this in Python:' [code block] "
            "'This approach works because...'\n\n"
            "Non-technical topics: Weave in 3-5 real-world examples like:\n"
            "'I saw this firsthand when...' or 'Consider how Amazon approached this...'\n\n"
            "REFERENCES:\n"
            "- Include at the end as ## References or ## Further Reading\n"
            "- Format: [1] Source Title - Brief description (URL)\n"
            "- Reference inline naturally: 'According to OpenAI's documentation [1]...'"
        ),
        expected_output=(
            "2000-2500 word engaging article with: compelling title, story-driven opening, "
            "4-6 numbered sections with flowing paragraphs (NO bullet lists), "
            "3-5 practical examples naturally integrated, conversational tone, "
            "memorable conclusion, references section. "
            "NO 'SEO Strategy', 'Target Audience', or marketing sections."
        ),
        tools=[],
        context=[plan_task],
        agent=writer_agent,
    )


def create_edit_task(editor_agent, write_task):
    """Create editing task - story polishing"""
    return Task(
        description=(
            "Edit the article to ensure it's an engaging Medium story, not a corporate document:\n\n"
            "1. REMOVE (if present):\n"
            "   - Any sections called 'SEO Strategy', 'Target Audience', 'Pain Points', 'Market Impact'\n"
            "   - Bullet lists of features, statistics, or comparisons (convert to flowing text)\n"
            "   - Marketing jargon: 'revolutionary', 'game-changing', 'cutting-edge'\n"
            "   - Meta-commentary about the article structure itself\n"
            "   - Academic or corporate tone\n\n"
            "2. ENHANCE:\n"
            "   - Opening hook: Ensure it's compelling (personal story, surprising fact, or question)\n"
            "   - Conversational flow: Check that paragraphs connect naturally\n"
            "   - Voice: Ensure consistent use of 'I'/'you'/'we' (not passive third person)\n"
            "   - Examples: Verify they're woven naturally into text, not listed separately\n"
            "   - Transitions: Add smooth bridges between sections\n\n"
            "3. VERIFY:\n"
            "   - Proper markdown formatting (## for numbered sections, code blocks with language tags)\n"
            "   - Short paragraphs (3-5 sentences)\n"
            "   - Varied sentence rhythm\n"
            "   - Accurate information and working code examples\n"
            "   - Conclusion provides genuine insight, not just summary\n\n"
            "4. FINAL CHECK:\n"
            "   - Does the opening make you want to keep reading?\n"
            "   - Does it sound like a person talking, not a company brochure?\n"
            "   - Would someone share this with a friend?\n"
            "   - Are statistics and data points integrated naturally?\n\n"
            "OUTPUT: Return ONLY the final article. No editorial notes. No process commentary."
        ),
        expected_output=(
            "Publication-ready Medium article that: "
            "starts with compelling hook, uses conversational tone throughout, "
            "integrates examples naturally (no bullet lists), "
            "has smooth transitions, proper markdown formatting, "
            "and NO marketing/SEO/audience analysis sections. "
            "Must read like a story, not a product brochure."
        ),
        tools=[],
        context=[write_task],
        agent=editor_agent,
    )
