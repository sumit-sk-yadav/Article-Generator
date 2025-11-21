"""Main Streamlit application for AI Content Generator"""
import streamlit as st
from src.crew_manager import CrewManager
from src.utils import format_markdown_with_metadata, generate_filename
from config import (
    SELECTED_PROVIDER, 
    PROVIDER_API_KEYS, 
    DEFAULT_TAVILY_API_KEY
)
import markdown2
import pdfkit
from io import BytesIO

def convert_markdown_to_pdf(markdown_content, topic):
    """Convert markdown content to PDF"""
    try:
        # Convert markdown to HTML
        html = markdown2.markdown(markdown_content, extras=['tables', 'fenced-code-blocks'])
        
        # Add some basic styling
        styled_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    padding: 40px;
                    max-width: 800px;
                    margin: 0 auto;
                }}
                h1, h2, h3 {{ color: #333; }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Configure pdfkit options
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # Convert to PDF
        pdf_bytes = pdfkit.from_string(styled_html, False, options=options)
        return pdf_bytes
        
    except Exception as e:
        st.error(f"Error converting to PDF: {str(e)}")
        return None


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

# Initialize API keys based on selected provider
if 'selected_provider' not in st.session_state:
    st.session_state.selected_provider = SELECTED_PROVIDER

if 'llm_api_key' not in st.session_state:
    st.session_state.llm_api_key = PROVIDER_API_KEYS.get(st.session_state.selected_provider, "")

if 'tavily_api_key' not in st.session_state:
    st.session_state.tavily_api_key = DEFAULT_TAVILY_API_KEY if DEFAULT_TAVILY_API_KEY else ""

if 'api_keys_valid' not in st.session_state:
    st.session_state.api_keys_valid = bool(st.session_state.llm_api_key and st.session_state.tavily_api_key)

if 'keys_from_user' not in st.session_state:
    st.session_state.keys_from_user = False

# Title and description
st.title("✍️ AI Content Generator")
st.markdown("""
Generate high-quality blog posts using AI agents powered by CrewAI with your choice of LLM provider. 
The system uses three specialized agents working sequentially:
- **🔍 Planner**: Researches trends and creates content outlines
- **✏️ Writer**: Crafts compelling, SEO-optimized blog posts
- **📝 Editor**: Polishes content to journalistic standards
""")

# Sidebar for settings and checkpoints
with st.sidebar:
    st.header("🔑 API Configuration")
    
    with st.expander("LLM Provider & API Keys", expanded=not st.session_state.api_keys_valid):
        # Provider selection
        provider_options = {
            "cerebras": "🚀 Cerebras (Ultra-fast - 2200+ tok/s)",
            "groq": "⚡ Groq (Fast - Free tier)",
        }
        
        selected_provider = st.selectbox(
            "Select LLM Provider",
            options=list(provider_options.keys()),
            format_func=lambda x: provider_options[x],
            index=list(provider_options.keys()).index(st.session_state.selected_provider),
            help="Choose your preferred LLM provider"
        )
        
        # Update provider if changed
        if selected_provider != st.session_state.selected_provider:
            st.session_state.selected_provider = selected_provider
            st.session_state.llm_api_key = PROVIDER_API_KEYS.get(selected_provider, "")
            st.rerun()
        
        st.markdown(f"""
        **Current Provider**: {provider_options[selected_provider]}
        
        Get API keys:
        - **Groq**: [console.groq.com](https://console.groq.com)
        - **Cerebras**: [cloud.cerebras.ai](https://cloud.cerebras.ai)
        - **Tavily**: [tavily.com](https://app.tavily.com)
        """)
        
        # LLM API Key input
        llm_key_placeholder = {
            "groq": "gsk_...",
            "cerebras": "csk-..."
        }
        
        llm_key_input = st.text_input(
            f"{selected_provider.title()} API Key",
            value="" if not st.session_state.keys_from_user else st.session_state.llm_api_key,
            type="password",
            help=f"Required for {selected_provider.title()} LLM operations",
            placeholder=llm_key_placeholder[selected_provider] if not st.session_state.api_keys_valid else "••••••••••••••••"
        )
        
        # Tavily API Key input
        tavily_key_input = st.text_input(
            "Tavily API Key",
            value="" if not st.session_state.keys_from_user else st.session_state.tavily_api_key,
            type="password",
            help="Required for web search functionality",
            placeholder="tvly-..." if not st.session_state.api_keys_valid else "••••••••••••••••"
        )
        
        # Save button
        if st.button("💾 Save API Keys", use_container_width=True):
            if llm_key_input and tavily_key_input:
                st.session_state.llm_api_key = llm_key_input
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
                st.session_state.llm_api_key = ""
                st.session_state.tavily_api_key = ""
                st.session_state.api_keys_valid = False
                st.session_state.keys_from_user = False
                st.info("API keys cleared")
                st.rerun()
    
    # Show API key status
    if st.session_state.api_keys_valid:
        if st.session_state.keys_from_user:
            st.success(f"✅ Using {st.session_state.selected_provider.title()} API")
        else:
            if st.session_state.llm_api_key and st.session_state.tavily_api_key:
                st.info(f"ℹ️ Using default {st.session_state.selected_provider.title()} configuration")
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
    
    st.header("📊 Task Status")
    checkpoints = st.session_state.crew_manager.get_checkpoints()
    
    if checkpoints:
        # Simple status display
        task_info = {
            'plan': {'icon': '🔍', 'name': 'Research & Planning'},
            'write': {'icon': '✏️', 'name': 'Writing'},
            'edit': {'icon': '📝', 'name': 'Editing'},
            'final': {'icon': '✅', 'name': 'Complete'}
        }
        
        for task_name in ['plan', 'write', 'edit', 'final']:
            if task_name in checkpoints:
                data = checkpoints[task_name]
                icon = task_info.get(task_name, {}).get('icon', '📝')
                name = task_info.get(task_name, {}).get('name', task_name.title())
                
                st.success(f"{icon} **{name}** - Completed")
                st.caption(f"Saved at {data['timestamp']}")
            else:
                icon = task_info.get(task_name, {}).get('icon', '📝')
                name = task_info.get(task_name, {}).get('name', task_name.title())
                st.info(f"{icon} **{name}** - Pending")
    else:
        st.info("No checkpoints available for this session")
    
    if checkpoints:
        if st.button("🗑️ Clear All Checkpoints", type="secondary", use_container_width=True):
            st.session_state.crew_manager.checkpoint_manager.clear_all_checkpoints()
            st.session_state.generated_content = None
            st.session_state.current_topic = None
            st.success("All checkpoints cleared!")
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
    placeholder="e.g., 'The Future of Quantum Computing in 2025'",
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
        # Auto-clear checkpoints if topic changed
        if st.session_state.current_topic and st.session_state.current_topic != topic:
            st.info(f"📝 Topic changed from '{st.session_state.current_topic}' to '{topic}'. Clearing old checkpoints...")
            st.session_state.crew_manager.checkpoint_manager.clear_checkpoints(st.session_state.current_topic)
            st.session_state.generated_content = None
        
        st.session_state.generation_in_progress = True
        st.session_state.current_topic = topic
        
        # Create progress container and execute immediately
        progress_container = st.container()
        
        with progress_container:
            st.info(f"🤖 AI agents are collaborating to create your article using {st.session_state.selected_provider.title()}...")
            
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
                    provider=st.session_state.selected_provider,
                    llm_api_key=st.session_state.llm_api_key,
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
    
    # Download buttons at the top
    col1, col2, col3 = st.columns([1.5, 1.5, 3])
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
        # Generate PDF
        pdf_filename = filename.replace('.md', '.pdf')
        pdf_data = convert_markdown_to_pdf(st.session_state.generated_content, st.session_state.current_topic)
        
        if pdf_data:
            st.download_button(
                label="📄 Download PDF",
                data=pdf_data,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True,
                help="Download the article as a PDF file"
            )
        else:
            st.button("📄 Download PDF", disabled=True, use_container_width=True)

    # Tabs for different views
    preview_tab, raw_tab = st.tabs(["📖 Preview", "📝 Raw Markdown"])
    
    with preview_tab:
        st.markdown(st.session_state.generated_content)
    
    with raw_tab:
        st.code(formatted_content, language="markdown")

# Footer
st.divider()
st.markdown(f"""
<div style='text-align: center; color: gray; padding: 2rem 0;'>
    <small>Powered by CrewAI • {st.session_state.selected_provider.title()} • Streamlit | Built with ❤️ for Content Creators</small>
</div>
""", unsafe_allow_html=True)
