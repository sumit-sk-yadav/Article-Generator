"""Main Streamlit application for AI Content Generator"""
import streamlit as st
from src.crew_manager import CrewManager
from src.utils import format_markdown_with_metadata, generate_filename
from config import DEFAULT_GROQ_API_KEY, DEFAULT_TAVILY_API_KEY

# Add this function near the top of app.py after imports
def display_checkpoint_progress(crew_manager):
    """Display checkpoint progress in real-time"""
    checkpoints = crew_manager.get_checkpoints()
    
    if checkpoints:
        cols = st.columns(3)
        tasks = ['plan', 'write', 'edit']
        icons = ['🔍', '✏️', '📝']
        
        for idx, task in enumerate(tasks):
            with cols[idx]:
                if task in checkpoints:
                    st.success(f"{icons[idx]} {task.upper()}\n✅ Completed")
                else:
                    st.info(f"{icons[idx]} {task.upper()}\n⏳ Pending")

# Page configuration
st.set_page_config(
    page_title="AI Content Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'crew_manager' not in st.session_state:
    st.session_state.crew_manager = CrewManager()
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = None
if 'generation_in_progress' not in st.session_state:
    st.session_state.generation_in_progress = False

# Initialize API keys WITHOUT showing defaults
if 'groq_api_key' not in st.session_state:
    # Use default if available, but don't display it
    st.session_state.groq_api_key = DEFAULT_GROQ_API_KEY if DEFAULT_GROQ_API_KEY else ""
if 'tavily_api_key' not in st.session_state:
    # Use default if available, but don't display it
    st.session_state.tavily_api_key = DEFAULT_TAVILY_API_KEY if DEFAULT_TAVILY_API_KEY else ""
if 'api_keys_valid' not in st.session_state:
    st.session_state.api_keys_valid = bool(st.session_state.groq_api_key and st.session_state.tavily_api_key)
if 'keys_from_user' not in st.session_state:
    # Track whether user has entered their own keys
    st.session_state.keys_from_user = False

# Title and description
st.title("✍️ AI Content Generator")
st.markdown("""
Generate high-quality blog posts using AI agents powered by CrewAI and Groq. 
The system uses three specialized agents working sequentially:
- **🔍 Planner**: Researches trends and creates content outlines
- **✏️ Writer**: Crafts compelling, SEO-optimized blog posts
- **📝 Editor**: Polishes content to journalistic standards
""")

# Sidebar for settings and checkpoints
with st.sidebar:
    st.header("🔑 API Configuration")
    
    with st.expander("API Keys", expanded=not st.session_state.api_keys_valid):
        st.markdown("""
        Enter your API keys below. These are stored only in your browser session and are not saved permanently.
        
        - **Groq API Key**: Get one from [console.groq.com](https://console.groq.com)
        - **Tavily API Key**: Get one from [tavily.com](https://app.tavily.com)
        """)
        
        # Groq API Key input - NEVER show the default value
        groq_key_input = st.text_input(
            "Groq API Key",
            value="" if not st.session_state.keys_from_user else st.session_state.groq_api_key,
            type="password",
            help="Required for LLM operations",
            placeholder="gsk_..." if not st.session_state.api_keys_valid else "••••••••••••••••"
        )
        
        # Tavily API Key input - NEVER show the default value
        tavily_key_input = st.text_input(
            "Tavily API Key",
            value="" if not st.session_state.keys_from_user else st.session_state.tavily_api_key,
            type="password",
            help="Required for web search functionality",
            placeholder="tvly-..." if not st.session_state.api_keys_valid else "••••••••••••••••"
        )
        
        # Save button
        if st.button("💾 Save API Keys", use_container_width=True):
            if groq_key_input and tavily_key_input:
                st.session_state.groq_api_key = groq_key_input
                st.session_state.tavily_api_key = tavily_key_input
                st.session_state.api_keys_valid = True
                st.session_state.keys_from_user = True
                st.success("✅ API Keys saved!")
                st.rerun()
            else:
                st.error("⚠️ Please provide both API keys")
        
        # Clear keys button
        if st.session_state.keys_from_user:
            if st.button("🗑️ Clear API Keys", use_container_width=True):
                st.session_state.groq_api_key = ""
                st.session_state.tavily_api_key = ""
                st.session_state.api_keys_valid = False
                st.session_state.keys_from_user = False
                st.info("API keys cleared")
                st.rerun()
    
    # Show API key status
    if st.session_state.api_keys_valid:
        if st.session_state.keys_from_user:
            st.success("✅ Using your API keys")
        else:
            # Only show this message if defaults exist but user hasn't entered their own
            if DEFAULT_GROQ_API_KEY and DEFAULT_TAVILY_API_KEY:
                st.info("ℹ️ Using default configuration")
            else:
                st.warning("⚠️ Please configure API keys above")
    else:
        st.warning("⚠️ Please configure API keys above")
    
    st.divider()
    
    st.header("⚙️ Settings")
    
    force_restart = st.checkbox(
        "Force Restart",
        value=False,
        help="Clear in-memory checkpoints and start from scratch",
        disabled=not st.session_state.api_keys_valid
    )
    
    st.divider()
    
    st.header("📊 Task Checkpoints")
    checkpoints = st.session_state.crew_manager.get_checkpoints()
    
    if checkpoints:
        for task_name, data in checkpoints.items():
            with st.expander(f"✅ {task_name.upper()}", expanded=False):
                st.write(f"**Agent:** {data.get('agent', 'Unknown')}")
                st.write(f"**Timestamp:** {data['timestamp']}")
                st.caption("Task completed and saved in memory")
    else:
        st.info("No checkpoints available for this session")
    
    if checkpoints:
        if st.button("🗑️ Clear All Checkpoints", type="secondary"):
            st.session_state.crew_manager.checkpoint_manager.clear_checkpoints()
            st.success("Checkpoints cleared!")
            st.rerun()
    
    st.divider()
    st.caption("💡 **Tip:** Checkpoints persist during your browser session and help resume work if interrupted.")

# Main content area
st.header("📝 Generate Your Article")

# Show warning if API keys are not configured
if not st.session_state.api_keys_valid:
    st.warning("⚠️ Please configure your API keys in the sidebar before generating content.")

# Topic input
topic = st.text_input(
    "Enter Blog Topic",
    placeholder="e.g., 'The Future of Generative AI in Healthcare'",
    help="Enter the topic you want to write about",
    disabled=st.session_state.generation_in_progress or not st.session_state.api_keys_valid
)

# Generate button
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    generate_button = st.button(
        "🚀 Generate Article", 
        type="primary", 
        disabled=st.session_state.generation_in_progress or not topic or not st.session_state.api_keys_valid,
        use_container_width=True
    )

with col2:
    if st.session_state.generated_content:
        if st.button("🔄 New Article", type="secondary", use_container_width=True):
            st.session_state.generated_content = None
            st.session_state.current_topic = None
            st.rerun()

# Generation logic
if generate_button:
    if not topic:
        st.error("⚠️ Please enter a topic")
    elif not st.session_state.api_keys_valid:
        st.error("⚠️ Please configure your API keys in the sidebar")
    else:
        st.session_state.generation_in_progress = True
        st.session_state.current_topic = topic
        
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            st.info("🤖 AI agents are collaborating to create your article...")
            checkpoint_placeholder = st.empty()

# Inside your generation try block, periodically update:
with progress_container:
    st.info("🤖 AI agents are collaborating to create your article...")
    
    # Show checkpoint progress
    checkpoint_container = st.container()
    with checkpoint_container:
            display_checkpoint_progress(st.session_state.crew_manager) 
            # Create progress bar and status text
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress updates
            status_text.text("🔍 Planner agent researching...")
            progress_bar.progress(10)
            
            try:
                # Execute the crew with user-provided API keys
                result = st.session_state.crew_manager.run_with_retry(
                    topic=topic,
                    groq_api_key=st.session_state.groq_api_key,
                    tavily_api_key=st.session_state.tavily_api_key,
                    force_restart=force_restart
                )
                
                # Update progress
                status_text.text("✏️ Writer agent crafting content...")
                progress_bar.progress(50)
                
                status_text.text("📝 Editor agent polishing...")
                progress_bar.progress(80)
                
                # Store result in session state
                st.session_state.generated_content = result
                st.session_state.generation_in_progress = False
                
                # Complete progress
                progress_bar.progress(100)
                status_text.text("✅ Article generated successfully!")
                
                st.success("✅ Your article is ready!")
                st.rerun()
                
            except Exception as e:
                st.session_state.generation_in_progress = False
                error_message = str(e)
                
                # Check for API key related errors
                if "api key" in error_message.lower() or "unauthorized" in error_message.lower():
                    st.error("❌ API Key Error: Please check that your API keys are valid and have sufficient credits.")
                else:
                    st.error(f"❌ An error occurred: {error_message}")
                
                st.warning("💾 Your progress has been saved. You can try again or check the checkpoints in the sidebar.")

# Display generated content
if st.session_state.generated_content:
    st.divider()
    st.header("📄 Your Generated Article")
    
    # Prepare markdown content with metadata
    formatted_content = format_markdown_with_metadata(
        st.session_state.generated_content, 
        st.session_state.current_topic
    )
    
    # Generate filename
    filename = generate_filename(st.session_state.current_topic)
    
    # Download button at the top
    col1, col2, col3 = st.columns([1.5, 1, 3.5])
    with col1:
        st.download_button(
            label="⬇️ Download Markdown",
            data=formatted_content,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True,
            help="Download the article as a .md file with metadata"
        )
    
    with col2:
        # Optional: Add a copy to clipboard button
        if st.button("📋 Copy Text", use_container_width=True):
            st.toast("Use Ctrl+C to copy from the Raw Markdown tab", icon="ℹ️")
    
    # Tabs for different views
    preview_tab, raw_tab = st.tabs(["📖 Preview", "📝 Raw Markdown"])
    
    with preview_tab:
        st.markdown(st.session_state.generated_content)
    
    with raw_tab:
        st.code(formatted_content, language="markdown")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem 0;'>
    <small>Powered by CrewAI • Groq • Streamlit | Built with ❤️ for Content Creators</small>
</div>
""", unsafe_allow_html=True)
