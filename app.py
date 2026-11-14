import streamlit as st
import pandas as pd
import requests
import re

# Streamlit Page Config
st.set_page_config(
    page_title="US Property Preservation Contractor Lead Finder",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ US Property Preservation Contractor Lead Finder")

# Top Creator Banner
st.markdown(
    """
    <div style="
        display: inline-block;
        background: linear-gradient(90deg, rgba(239,68,68,0.15) 0%, rgba(56,189,248,0.15) 100%);
        border-left: 4px solid #ef4444;
        padding: 6px 14px;
        border-radius: 4px;
        margin-bottom: 12px;
    ">
        <span style="color: #e2e8f0; font-size: 13px;">
            🚀 Architected & Automated by <b style="color: #38bdf8; letter-spacing: 0.5px;">SAHRIA HIMEL</b> &nbsp;|&nbsp; Vendor Management & Operations
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("Finds local, independent, and family-owned contractors for property preservation work orders (winterization, lawn care, initial secures, lock changes, debris removal) and screens out chains, corporations, and toll-free vendors automatically using built-in filters.")

# Sidebar Configuration
st.sidebar.header("Search Settings")
zip_code = st.sidebar.text_input("US ZIP Code", value="78962")
trade = st.sidebar.selectbox("Trade", ["Lawn Care", "Handyman", "Locksmith", "Debris Removal", "Winterization"])

st.sidebar.markdown("---")
st.sidebar.subheader("API Key")
search_api_key = st.sidebar.text_input("Search API Key (Serper.dev)", type="password", help="Get a free key from serper.dev")

search_button = st.sidebar.button("Find & Filter Contractors")

# Helper function to check if a contractor is local/independent
def is_local_independent(name, phone):
    name_lower = name.lower()
    
    # Exclude keywords for large corporations, franchises, or commercial entities
    exclusion_keywords = [
        'inc', 'corp', 'llc', 'franchise', 'co.', 'company', 'service experts', 
        'nationwide', 'solutions', 'group', 'properties', 'rentals', 'homes'
    ]
    for keyword in exclusion_keywords:
        # Check as a separate word to avoid false positives (e.g., 'Lincoln')
        if re.search(r'\b' + keyword + r'\b', name_lower):
            return False, f"Contains corporate keyword: '{keyword}'"
            
    # Exclude Toll-Free phone numbers (1-800, 1-888, 1-877, 1-866, etc.)
    if phone:
        clean_phone = re.sub(r'\D', '', phone)
        if clean_phone.startswith(('800', '888', '877', '866', '855', '844', '833', '1800', '1888', '1877', '1866')):
            return False, "Uses toll-free corporate phone number"
            
    return True, "Independent / Family-owned local provider"

if search_button:
    if not search_api_key:
        st.error("Please enter your Serper Search API key in the sidebar. (You can get a free key from serper.dev)")
    else:
        with st.spinner(f"Searching and filtering contractors for ZIP: {zip_code} ({trade})..."):
            # Serper.dev API integration
            url = "https://google.serper.dev/places"
            payload = {
                "q": f"{trade} in ZIP {zip_code} USA",
                "gl": "us",
                "hl": "en"
            }
            headers = {
                'X-API-KEY': search_api_key,
                'Content-Type': 'application/json'
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    places = data.get('places', [])
                    
                    if not places:
                        st.warning("No businesses found for this ZIP code and trade. Try a different ZIP code.")
                    else:
                        processed_leads = []
                        for place in places:
                            name = place.get('title', 'N/A')
                            phone = place.get('phoneNumber', 'N/A')
                            address = place.get('address', 'N/A')
                            rating = place.get('rating', 'N/A')
                            source_url = place.get('website', 'Google Maps')
                            
                            # Run automated smart filtering
                            is_passed, reason = is_local_independent(name, phone)
                            
                            if is_passed:
                                processed_leads.append({
                                    "Business Name": name,
                                    "Phone Number": phone,
                                    "Category": trade,
                                    "Address": address,
                                    "Rating": rating,
                                    "Why Family-Owned/Local": reason,
                                    "Source": source_url
                                })
                        
                        if processed_leads:
                            df = pd.DataFrame(processed_leads)
                            st.success(f"Successfully filtered and found {len(df)} independent/local contractor leads!")
                            st.dataframe(df, use_container_width=True)
                            
                            # CSV Export
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Download Filtered Leads as CSV",
                                data=csv,
                                file_name=f"contractor_leads_{zip_code}_{trade}.csv",
                                mime='text/csv',
                            )
                        else:
                            st.warning("Found listings, but all of them were filtered out because they appeared to be corporate chains or used toll-free numbers.")
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Sidebar Bottom Developer Credit Card
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #38bdf8;
        border-radius: 10px;
        padding: 12px 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
        margin-top: 15px;
    ">
        <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px;">
            ⚡ Developed By
        </span><br>
        <span style="font-size: 16px; font-weight: 800; color: #38bdf8; letter-spacing: 1px;">
            SAHRIA HIMEL
        </span><br>
        <span style="font-size: 11px; color: #cbd5e1;">
            Vendor Management Team
        </span>
    </div>
    """,
    unsafe_allow_html=True
)