import streamlit as st
import pandas as pd
import io

# Set page config
st.set_page_config(
    page_title="Marketing Tactic Detector",
    page_icon="🎯",
    layout="wide"
)

# Default dictionaries
DEFAULT_DICTIONARIES = {
    'urgency_marketing': {
        'limited', 'limited time', 'limited run', 'limited edition', 'order now',
        'last chance', 'hurry', 'while supplies last', 'before they\'re gone',
        'selling out', 'selling fast', 'act now', 'don\'t wait', 'today only',
        'expires soon', 'final hours', 'almost gone'
    },
    'exclusive_marketing': {
        'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
        'members only', 'vip', 'special access', 'invitation only',
        'premium', 'privileged', 'limited access', 'select customers',
        'insider', 'private sale', 'early access'
    }
}

def detect_tactics(text, dictionaries):
    """Detect marketing tactics in text and return results."""
    if pd.isna(text) or not isinstance(text, str):
        return {'urgency_marketing': 0, 'exclusive_marketing': 0, 'matched_terms': []}
   
    text_lower = text.lower()
    results = {'urgency_marketing': 0, 'exclusive_marketing': 0, 'matched_terms': []}
   
    for tactic, terms in dictionaries.items():
        for term in terms:
            if term in text_lower:
                results[tactic] = 1
                results['matched_terms'].append(term)
   
    return results

def load_csv_file(uploaded_file):
    """Load CSV file with robust parsing."""
    try:
        # Try comma separator first
        df = pd.read_csv(uploaded_file)
        uploaded_file.seek(0)  # Reset file pointer
       
        # Check if semicolon-separated
        if len(df.columns) == 1 and ';' in df.columns[0]:
            df = pd.read_csv(uploaded_file, sep=';')
           
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None
   
    return df

def process_data(df, statement_column, dictionaries):
    """Process dataframe and add marketing tactic detection."""
    # Apply detection to Statement column
    detections = df[statement_column].apply(lambda x: detect_tactics(x, dictionaries))
   
    # Extract results into separate columns
    df_result = df.copy()
    df_result['urgency_detected'] = [d['urgency_marketing'] for d in detections]
    df_result['exclusive_detected'] = [d['exclusive_marketing'] for d in detections]
    df_result['matched_terms'] = [', '.join(d['matched_terms']) for d in detections]
   
    return df_result

def main():
    st.title("🎯 Marketing Tactic Detector")
    st.markdown("Upload your dataset and detect urgency and exclusive marketing tactics in text data.")
   
    # Sidebar for dictionary editing
    st.sidebar.header("📝 Edit Dictionaries")
   
    # Initialize session state for dictionaries
    if 'dictionaries' not in st.session_state:
        st.session_state.dictionaries = DEFAULT_DICTIONARIES.copy()
   
    # Dictionary editing interface
    st.sidebar.subheader("Urgency Marketing Terms")
    urgency_text = st.sidebar.text_area(
        "Enter terms (one per line):",
        value='\n'.join(st.session_state.dictionaries['urgency_marketing']),
        height=150,
        key="urgency_terms"
    )
   
    st.sidebar.subheader("Exclusive Marketing Terms")
    exclusive_text = st.sidebar.text_area(
        "Enter terms (one per line):",
        value='\n'.join(st.session_state.dictionaries['exclusive_marketing']),
        height=150,
        key="exclusive_terms"
    )
   
    # Update dictionaries when text changes
    st.session_state.dictionaries['urgency_marketing'] = set(
        term.strip().lower() for term in urgency_text.split('\n') if term.strip()
    )
    st.session_state.dictionaries['exclusive_marketing'] = set(
        term.strip().lower() for term in exclusive_text.split('\n') if term.strip()
    )
   
    # Reset to defaults button
    if st.sidebar.button("Reset to Defaults"):
        st.session_state.dictionaries = DEFAULT_DICTIONARIES.copy()
        st.rerun()
   
    # Main content area
    col1, col2 = st.columns([2, 1])
   
    with col1:
        st.header("📁 Upload Dataset")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload a CSV file containing text data to analyze"
        )
       
        if uploaded_file is not None:
            # Load and display the data
            df = load_csv_file(uploaded_file)
           
            if df is not None:
                st.success(f"✅ File loaded successfully! Shape: {df.shape}")
               
                # Column selection
                st.subheader("📋 Data Preview")
                st.dataframe(df.head(), use_container_width=True)
               
                # Select statement column
                statement_column = st.selectbox(
                    "Select the column containing text to analyze:",
                    options=df.columns.tolist(),
                    index=df.columns.tolist().index('Statement') if 'Statement' in df.columns else 0
                )
               
                # Process button
                if st.button("🔍 Analyze Marketing Tactics", type="primary"):
                    with st.spinner("Processing data..."):
                        result_df = process_data(df, statement_column, st.session_state.dictionaries)
                   
                    # Display results
                    st.subheader("📊 Analysis Results")
                   
                    # Summary metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Total Statements", len(result_df))
                    with col_b:
                        st.metric("Urgency Tactics Detected", result_df['urgency_detected'].sum())
                    with col_c:
                        st.metric("Exclusive Tactics Detected", result_df['exclusive_detected'].sum())
                   
                    # Show detected tactics
                    detected_df = result_df[
                        (result_df['urgency_detected'] == 1) |
                        (result_df['exclusive_detected'] == 1)
                    ]
                   
                    if len(detected_df) > 0:
                        st.subheader("🎯 Statements with Marketing Tactics")
                       
                        # Display with highlighting
                        for idx, row in detected_df.iterrows():
                            with st.expander(f"Row {idx + 1}: {row[statement_column][:100]}..."):
                                st.write(f"**Full Statement:** {row[statement_column]}")
                               
                                tactics = []
                                if row['urgency_detected']:
                                    tactics.append("🚨 Urgency")
                                if row['exclusive_detected']:
                                    tactics.append("⭐ Exclusive")
                               
                                st.write(f"**Tactics Detected:** {', '.join(tactics)}")
                                st.write(f"**Matched Terms:** {row['matched_terms']}")
                    else:
                        st.info("No marketing tactics detected in the uploaded data.")
                   
                    # Full results table
                    st.subheader("📋 Complete Results")
                    st.dataframe(result_df, use_container_width=True)
                   
                    # Download button
                    csv_buffer = io.StringIO()
                    result_df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                   
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv_data,
                        file_name="marketing_tactics_analysis.csv",
                        mime="text/csv"
                    )
   
    with col2:
        st.header("ℹ️ Current Dictionary")
       
        st.subheader("🚨 Urgency Terms")
        st.write(f"**{len(st.session_state.dictionaries['urgency_marketing'])} terms:**")
        for term in sorted(st.session_state.dictionaries['urgency_marketing']):
            st.write(f"• {term}")
       
        st.subheader("⭐ Exclusive Terms")
        st.write(f"**{len(st.session_state.dictionaries['exclusive_marketing'])} terms:**")
        for term in sorted(st.session_state.dictionaries['exclusive_marketing']):
            st.write(f"• {term}")
       
        st.markdown("---")
        st.markdown("**💡 Tips:**")
        st.markdown("- Edit terms in the sidebar")
        st.markdown("- One term per line")
        st.markdown("- Terms are case-insensitive")
        st.markdown("- Click 'Reset to Defaults' to restore original terms")

if __name__ == "__main__":
    main()
