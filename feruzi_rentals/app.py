# app.py - Updated with better logo handling for GitHub deployment
import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import uuid
import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io
from PIL import Image as PILImage
import base64
import requests

# Get the directory where the app is running
def get_app_dir():
    """Get the application directory path"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()

# Function to format currency in KES
def format_kes(amount):
    return f"KES {amount:,.2f}"

# Enhanced function to get logo from multiple sources
def get_logo_image():
    """Try to load logo from multiple sources including GitHub raw"""
    
    # List of possible logo file names
    logo_names = ["feruzi_logo.png", "logo.png", "favicon.ico", "feruzi.png", "feruzi_logo.jpg"]
    
    # Method 1: Check local files in app directory
    for logo_name in logo_names:
        local_path = os.path.join(APP_DIR, logo_name)
        if os.path.exists(local_path):
            try:
                with open(local_path, "rb") as f:
                    logo_data = f.read()
                    if logo_data:  # Check if file has content
                        return base64.b64encode(logo_data).decode()
            except:
                pass
    
    # Method 2: Check current working directory
    for logo_name in logo_names:
        if os.path.exists(logo_name):
            try:
                with open(logo_name, "rb") as f:
                    logo_data = f.read()
                    if logo_data:
                        return base64.b64encode(logo_data).decode()
            except:
                pass
    
    # Method 3: Try to download from GitHub raw URL (for Streamlit Cloud)
    try:
        # Replace with your actual GitHub username and repository
        github_username = "subirahope"  # Replace with your GitHub username
        repo_name = "feruzi_rentals"    # Replace with your repository name
        
        github_raw_urls = [
            f"https://raw.githubusercontent.com/{github_username}/{repo_name}/main/feruzi_logo.png",
            f"https://raw.githubusercontent.com/{github_username}/{repo_name}/main/logo.png",
            f"https://raw.githubusercontent.com/{github_username}/{repo_name}/main/favicon.ico",
        ]
        
        for url in github_raw_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200 and response.content:
                    return base64.b64encode(response.content).decode()
            except:
                continue
    except:
        pass
    
    return None

# Page configuration with favicon
logo_base64 = get_logo_image()
if logo_base64:
    st.set_page_config(
        page_title="Feruzi Rentals - Camera Inventory System",
        page_icon=f"data:image/png;base64,{logo_base64}",
        layout="wide",
        initial_sidebar_state="expanded"
    )
else:
    st.set_page_config(
        page_title="Feruzi Rentals - Camera Inventory System",
        page_icon="📷",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #34495e;
        margin-top: 1rem;
    }
    .centered-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=[
        'item_id', 'item_name', 'category', 'brand', 'model', 
        'serial_number', 'daily_rate', 'status', 'current_renter'
    ])

if 'rentals' not in st.session_state:
    st.session_state.rentals = pd.DataFrame(columns=[
        'rental_id', 'customer_name', 'customer_email', 'customer_phone',
        'item_id', 'item_name', 'rental_date', 'return_date', 
        'total_cost', 'deposit_paid', 'balance_due', 'status'
    ])

# Load sample data
def load_sample_data():
    if st.session_state.inventory.empty:
        sample_items = [
            {
                'item_id': 'CAM001',
                'item_name': 'Sony A7III',
                'category': 'Camera Body',
                'brand': 'Sony',
                'model': 'A7III',
                'serial_number': 'SN123456',
                'daily_rate': 5000.0,
                'status': 'Available',
                'current_renter': ''
            },
            {
                'item_id': 'LEN001',
                'item_name': 'Canon 24-70mm f/2.8',
                'category': 'Lens',
                'brand': 'Canon',
                'model': '24-70mm',
                'serial_number': 'SN789012',
                'daily_rate': 3500.0,
                'status': 'Available',
                'current_renter': ''
            },
            {
                'item_id': 'CAM002',
                'item_name': 'Nikon Z6',
                'category': 'Camera Body',
                'brand': 'Nikon',
                'model': 'Z6',
                'serial_number': 'SN345678',
                'daily_rate': 4500.0,
                'status': 'Rented',
                'current_renter': 'John Doe'
            }
        ]
        st.session_state.inventory = pd.DataFrame(sample_items)
    
    if st.session_state.rentals.empty:
        sample_rental = {
            'rental_id': 'RENT001',
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'customer_phone': '0712345678',
            'item_id': 'CAM002',
            'item_name': 'Nikon Z6',
            'rental_date': datetime.date.today() - timedelta(days=2),
            'return_date': datetime.date.today() + timedelta(days=3),
            'total_cost': 22500.0,
            'deposit_paid': 10000.0,
            'balance_due': 12500.0,
            'status': 'Active'
        }
        st.session_state.rentals = pd.DataFrame([sample_rental])

def save_data():
    try:
        st.session_state.inventory.to_csv('inventory.csv', index=False)
        st.session_state.rentals.to_csv('rentals.csv', index=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_data():
    try:
        if os.path.exists('inventory.csv'):
            st.session_state.inventory = pd.read_csv('inventory.csv')
        if os.path.exists('rentals.csv'):
            st.session_state.rentals = pd.read_csv('rentals.csv')
            # Convert date columns
            if 'rental_date' in st.session_state.rentals.columns:
                st.session_state.rentals['rental_date'] = pd.to_datetime(st.session_state.rentals['rental_date']).dt.date
            if 'return_date' in st.session_state.rentals.columns:
                st.session_state.rentals['return_date'] = pd.to_datetime(st.session_state.rentals['return_date']).dt.date
            # Add balance_due if missing
            if 'balance_due' not in st.session_state.rentals.columns:
                if 'total_cost' in st.session_state.rentals.columns and 'deposit_paid' in st.session_state.rentals.columns:
                    st.session_state.rentals['balance_due'] = st.session_state.rentals['total_cost'] - st.session_state.rentals['deposit_paid']
                else:
                    st.session_state.rentals['balance_due'] = 0
    except Exception as e:
        st.error(f"Error loading data: {e}")

# Function to create receipt PDF
def create_receipt_pdf(rental_data, logo_path="feruzi_logo.png"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Try to add logo from multiple sources
    logo_added = False
    
    # Try local file first
    for possible_logo in ["feruzi_logo.png", "logo.png", "favicon.ico"]:
        if os.path.exists(possible_logo):
            try:
                img = Image(possible_logo, width=2*inch, height=2*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
                logo_added = True
                break
            except:
                continue
    
    # Company header
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
                                 textColor=colors.HexColor('#2c3e50'), alignment=TA_CENTER, spaceAfter=10)
    story.append(Paragraph("FERUZI RENTALS", title_style))
    
    tagline_style = ParagraphStyle('Tagline', parent=styles['Normal'], fontSize=10,
                                   textColor=colors.HexColor('#7f8c8d'), alignment=TA_CENTER, spaceAfter=30)
    story.append(Paragraph("FILM.PHOTOGRAPHY.POSSIBILITY.", tagline_style))
    
    # Receipt title
    receipt_title = ParagraphStyle('ReceiptTitle', parent=styles['Heading2'], fontSize=16,
                                   textColor=colors.HexColor('#34495e'), alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph(f"RENTAL RECEIPT #{rental_data['rental_id']}", receipt_title))
    story.append(Spacer(1, 0.2*inch))
    
    # Customer information
    customer_data = [
        ['Customer Name:', rental_data['customer_name']],
        ['Email:', rental_data['customer_email']],
        ['Phone:', rental_data['customer_phone']],
        ['Date Issued:', datetime.date.today().strftime('%Y-%m-%d')]
    ]
    
    customer_table = Table(customer_data, colWidths=[1.5*inch, 3*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Rental details
    daily_rate = rental_data.get('daily_rate', 0)
    days = (rental_data['return_date'] - rental_data['rental_date']).days
    rental_subtotal = days * daily_rate
    
    rental_details = [
        ['Item Rented:', rental_data['item_name']],
        ['Rental Date:', rental_data['rental_date'].strftime('%Y-%m-%d')],
        ['Return Date:', rental_data['return_date'].strftime('%Y-%m-%d')],
        ['Duration (Days):', str(days)],
        ['Daily Rate:', f"KES {daily_rate:,.2f}"],
        ['Total Rental Cost:', f"KES {rental_subtotal:,.2f}"],
        ['Deposit Paid (Today):', f"KES {rental_data.get('deposit_paid', 0):,.2f}"],
        ['Balance Due (On Return):', f"KES {rental_data.get('balance_due', 0):,.2f}"]
    ]
    
    rental_table = Table(rental_details, colWidths=[1.5*inch, 3*inch])
    
    table_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]
    
    table_style.append(('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#d4edda')))
    table_style.append(('TEXTCOLOR', (0, 6), (-1, 6), colors.HexColor('#155724')))
    table_style.append(('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#fff3cd')))
    table_style.append(('TEXTCOLOR', (0, 7), (-1, 7), colors.HexColor('#856404')))
    
    rental_table.setStyle(TableStyle(table_style))
    story.append(rental_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Payment instructions
    payment_style = ParagraphStyle('PaymentStatus', parent=styles['Normal'], fontSize=10,
                                   textColor=colors.HexColor('#28a745'), alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph("<b>✓ Deposit Payment Received</b>", payment_style))
    
    # Terms
    terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=8,
                                 textColor=colors.grey, alignment=TA_CENTER)
    terms_text = """
    <b>Payment Terms:</b><br/>
    1. Deposit paid today secures the rental<br/>
    2. Balance must be paid upon return of equipment<br/>
    3. Late returns incur additional charges of KES 500 per day<br/>
    4. Customer is responsible for any damage to equipment
    """
    story.append(Paragraph(terms_text, terms_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                                  textColor=colors.grey, alignment=TA_CENTER)
    story.append(Paragraph("Thank you for choosing Feruzi Rentals!", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Function to display centered logo
def display_centered_logo(width=200):
    logo_base64_local = get_logo_image()
    if logo_base64_local:
        centered_logo_html = f"""
        <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
            <img src="data:image/png;base64,{logo_base64_local}" width="{width}" style="object-fit: contain;">
        </div>
        """
        st.markdown(centered_logo_html, unsafe_allow_html=True)
        return True
    else:
        # Fallback to text logo
        st.markdown('<p style="text-align: center; font-size: 1.5rem;">📷 FERUZI RENTALS</p>', unsafe_allow_html=True)
        return False

# Main app
def main():
    load_data()
    if st.session_state.inventory.empty:
        load_sample_data()
    
    # Sidebar
    st.sidebar.markdown("---")
    logo_base64_sidebar = get_logo_image()
    if logo_base64_sidebar:
        col1, col2, col3 = st.sidebar.columns([1, 2, 1])
        with col2:
            st.image(f"data:image/png;base64,{logo_base64_sidebar}", use_container_width=True)
    else:
        st.sidebar.markdown("### 📷 FERUZI RENTALS")
    
    st.sidebar.markdown("---")
    st.sidebar.title("📋 Navigation")
    
    menu = st.sidebar.selectbox(
        "Choose an option",
        ["Dashboard", "Inventory Management", "New Rental", "Active Rentals", "Return & Clear Balance", "Rental History"]
    )
    
    # Dashboard
    if menu == "Dashboard":
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(width=250)
        
        st.markdown('<h1 class="main-header">FERUZI RENTALS</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #7f8c8d;">FILM.PHOTOGRAPHY.POSSIBILITY.</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            available_items = len(st.session_state.inventory[st.session_state.inventory['status'] == 'Available'])
            st.metric("📷 Available Items", available_items)
        with col2:
            rented_items = len(st.session_state.inventory[st.session_state.inventory['status'] == 'Rented'])
            st.metric("🔴 Rented Out", rented_items)
        with col3:
            active_rentals = len(st.session_state.rentals[st.session_state.rentals['status'] == 'Active'])
            st.metric("📝 Active Rentals", active_rentals)
        with col4:
            if 'balance_due' in st.session_state.rentals.columns:
                active_mask = st.session_state.rentals['status'] == 'Active'
                total_outstanding = st.session_state.rentals.loc[active_mask, 'balance_due'].sum()
            else:
                total_outstanding = 0
            st.metric("💰 Outstanding Balance", format_kes(total_outstanding))
        
        st.markdown("---")
        
        st.subheader("📊 Recent Rentals")
        if not st.session_state.rentals.empty:
            recent = st.session_state.rentals.tail(5)
            display_df = recent.copy()
            
            if 'total_cost' in display_df.columns:
                display_df['total_cost'] = display_df['total_cost'].apply(lambda x: format_kes(x))
            if 'deposit_paid' in display_df.columns:
                display_df['deposit_paid'] = display_df['deposit_paid'].apply(lambda x: format_kes(x))
            if 'balance_due' in display_df.columns:
                display_df['balance_due'] = display_df['balance_due'].apply(lambda x: format_kes(x))
            
            columns_to_show = ['rental_id', 'customer_name', 'item_name', 'rental_date', 'return_date', 'deposit_paid', 'balance_due', 'status']
            available_cols = [col for col in columns_to_show if col in display_df.columns]
            st.dataframe(display_df[available_cols], use_container_width=True)
        
        st.subheader("📦 Current Inventory Status")
        inventory_display = st.session_state.inventory[['item_id', 'item_name', 'category', 'status', 'current_renter']].copy()
        st.dataframe(inventory_display, use_container_width=True)
    
    # New Rental (simplified for brevity - keep your existing code)
    elif menu == "New Rental":
        st.markdown('<h1 class="main-header">Create New Rental</h1>', unsafe_allow_html=True)
        st.info("Rental creation form would go here - keeping your existing code")
        # ... (your existing New Rental code)
    
    # Active Rentals
    elif menu == "Active Rentals":
        st.markdown('<h1 class="main-header">Active Rentals</h1>', unsafe_allow_html=True)
        active = st.session_state.rentals[st.session_state.rentals['status'] == 'Active']
        if active.empty:
            st.info("No active rentals.")
        else:
            display_active = active.copy()
            if 'deposit_paid' in display_active.columns:
                display_active['deposit_paid'] = display_active['deposit_paid'].apply(lambda x: format_kes(x))
            if 'balance_due' in display_active.columns:
                display_active['balance_due'] = display_active['balance_due'].apply(lambda x: format_kes(x))
            st.dataframe(display_active[['rental_id', 'customer_name', 'item_name', 'rental_date', 'return_date', 'deposit_paid', 'balance_due']], use_container_width=True)
    
    # Return & Clear Balance
    elif menu == "Return & Clear Balance":
        st.markdown('<h1 class="main-header">Return Item & Clear Balance</h1>', unsafe_allow_html=True)
        st.info("Return form would go here - keeping your existing code")
        # ... (your existing Return code)
    
    # Inventory Management
    elif menu == "Inventory Management":
        st.markdown('<h1 class="main-header">Inventory Management</h1>', unsafe_allow_html=True)
        st.info("Inventory management would go here - keeping your existing code")
        # ... (your existing Inventory code)
    
    # Rental History
    elif menu == "Rental History":
        st.markdown('<h1 class="main-header">Rental History</h1>', unsafe_allow_html=True)
        if not st.session_state.rentals.empty:
            display_history = st.session_state.rentals.copy()
            if 'total_cost' in display_history.columns:
                display_history['total_cost'] = display_history['total_cost'].apply(lambda x: format_kes(x))
            if 'deposit_paid' in display_history.columns:
                display_history['deposit_paid'] = display_history['deposit_paid'].apply(lambda x: format_kes(x))
            if 'balance_due' in display_history.columns:
                display_history['balance_due'] = display_history['balance_due'].apply(lambda x: format_kes(x))
            st.dataframe(display_history, use_container_width=True)

if __name__ == "__main__":
    main()
