# ============================================================================
# FERUZI RENTALS - COMPLETE INVENTORY MANAGEMENT SYSTEM
# ============================================================================

import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import uuid
import os
import sys
import json
import io
import base64
import requests
import tempfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_app_dir():
    """Get the application directory path"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()

def format_kes(amount):
    """Format currency in Kenyan Shillings"""
    return f"KES {amount:,.2f}"

def get_logo_image():
    """Try to load logo from multiple sources"""
    logo_names = ["feruzi_logo.png", "logo.png", "favicon.ico", "feruzi.png"]
    
    # Check local files
    for logo_name in logo_names:
        local_path = os.path.join(APP_DIR, logo_name)
        if os.path.exists(local_path):
            try:
                with open(local_path, "rb") as f:
                    logo_data = f.read()
                    if logo_data:
                        return base64.b64encode(logo_data).decode()
            except:
                pass
        
        if os.path.exists(logo_name):
            try:
                with open(logo_name, "rb") as f:
                    logo_data = f.read()
                    if logo_data:
                        return base64.b64encode(logo_data).decode()
            except:
                pass
    
    # Try GitHub raw URL
    try:
        github_username = "subirahope"
        repo_name = "FERUZI_RENTALS"
        url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/main/feruzi_logo.png"
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.content:
            return base64.b64encode(response.content).decode()
    except:
        pass
    
    return None

def display_centered_logo(width=200):
    """Display centered logo in the app"""
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
        st.markdown('<p style="text-align: center; font-size: 1.5rem;">📷 FERUZI RENTALS</p>', unsafe_allow_html=True)
        return False

# ============================================================================
# DATA MANAGEMENT FUNCTIONS
# ============================================================================

def fix_dataframe_dtypes():
    """Ensure all columns have correct data types"""
    if 'current_renter' in st.session_state.inventory.columns:
        st.session_state.inventory['current_renter'] = st.session_state.inventory['current_renter'].astype(str)
        st.session_state.inventory['current_renter'] = st.session_state.inventory['current_renter'].replace('nan', '')
    
    if 'item_id' in st.session_state.inventory.columns:
        st.session_state.inventory['item_id'] = st.session_state.inventory['item_id'].astype(str)
    
    if 'status' in st.session_state.inventory.columns:
        st.session_state.inventory['status'] = st.session_state.inventory['status'].astype(str)
    
    if 'rental_id' in st.session_state.rentals.columns:
        st.session_state.rentals['rental_id'] = st.session_state.rentals['rental_id'].astype(str)
    if 'customer_name' in st.session_state.rentals.columns:
        st.session_state.rentals['customer_name'] = st.session_state.rentals['customer_name'].astype(str)
    if 'status' in st.session_state.rentals.columns:
        st.session_state.rentals['status'] = st.session_state.rentals['status'].astype(str)

def save_data():
    """Save data to CSV files"""
    try:
        st.session_state.inventory.to_csv('inventory.csv', index=False)
        st.session_state.rentals.to_csv('rentals.csv', index=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_data():
    """Load data from CSV files"""
    try:
        if os.path.exists('inventory.csv'):
            st.session_state.inventory = pd.read_csv('inventory.csv')
        if os.path.exists('rentals.csv'):
            st.session_state.rentals = pd.read_csv('rentals.csv')
            if 'rental_date' in st.session_state.rentals.columns:
                st.session_state.rentals['rental_date'] = pd.to_datetime(st.session_state.rentals['rental_date']).dt.date
            if 'return_date' in st.session_state.rentals.columns:
                st.session_state.rentals['return_date'] = pd.to_datetime(st.session_state.rentals['return_date']).dt.date
            if 'balance_due' not in st.session_state.rentals.columns:
                if 'total_cost' in st.session_state.rentals.columns and 'deposit_paid' in st.session_state.rentals.columns:
                    st.session_state.rentals['balance_due'] = st.session_state.rentals['total_cost'] - st.session_state.rentals['deposit_paid']
                else:
                    st.session_state.rentals['balance_due'] = 0
        
        fix_dataframe_dtypes()
        
    except Exception as e:
        st.error(f"Error loading data: {e}")

def load_sample_data():
    """Load sample data if no data exists"""
    if st.session_state.inventory.empty:
        sample_items = [
            {'item_id': 'CAM001', 'item_name': 'Sony A7III', 'category': 'Camera Body', 'brand': 'Sony', 'model': 'A7III', 'serial_number': 'SN123456', 'daily_rate': 5000.0, 'status': 'Available', 'current_renter': ''},
            {'item_id': 'LEN001', 'item_name': 'Canon 24-70mm f/2.8', 'category': 'Lens', 'brand': 'Canon', 'model': '24-70mm', 'serial_number': 'SN789012', 'daily_rate': 3500.0, 'status': 'Available', 'current_renter': ''},
            {'item_id': 'CAM002', 'item_name': 'Nikon Z6', 'category': 'Camera Body', 'brand': 'Nikon', 'model': 'Z6', 'serial_number': 'SN345678', 'daily_rate': 4500.0, 'status': 'Available', 'current_renter': ''}
        ]
        st.session_state.inventory = pd.DataFrame(sample_items)

# ============================================================================
# PROFESSIONAL PDF RECEIPT GENERATION
# ============================================================================

def create_multi_item_receipt_pdf(rental_data, items_list):
    """Generate professional redesigned PDF receipt for multi-item rental"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=0.75*inch, leftMargin=0.75*inch, 
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom colors
    primary_color = colors.HexColor('#1a1a2e')
    secondary_color = colors.HexColor('#e94560')
    accent_color = colors.HexColor('#0f3460')
    light_gray = colors.HexColor('#f8f9fa')
    border_gray = colors.HexColor('#dee2e6')
    
    # ========================================================================
    # HEADER SECTION
    # ========================================================================
    
    # Logo
    logo_added = False
    logo_paths_to_try = ["feruzi_logo.png", "logo.png", "favicon.ico", 
                         os.path.join(APP_DIR, "feruzi_logo.png"),
                         os.path.join(APP_DIR, "logo.png")]
    
    for logo_path in logo_paths_to_try:
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=1.2*inch, height=1.2*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 0.15*inch))
                logo_added = True
                break
            except:
                continue
    
    # Company Name
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22,
                                 textColor=primary_color, alignment=TA_CENTER, spaceAfter=5)
    story.append(Paragraph("FERUZI RENTALS", title_style))
    
    tagline_style = ParagraphStyle('Tagline', parent=styles['Normal'], fontSize=10,
                                   textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceAfter=0.25*inch)
    story.append(Paragraph("Film. Photography. Possibility.", tagline_style))
    
    # Divider
    divider_style = ParagraphStyle('Divider', parent=styles['Normal'], fontSize=8,
                                   textColor=border_gray, alignment=TA_CENTER, spaceAfter=0.2*inch)
    story.append(Paragraph("━" * 60, divider_style))
    
    # Receipt Title
    receipt_title_style = ParagraphStyle('ReceiptTitle', parent=styles['Heading2'], fontSize=16,
                                         textColor=secondary_color, alignment=TA_CENTER, spaceAfter=5)
    story.append(Paragraph("RENTAL RECEIPT", receipt_title_style))
    
    receipt_id_style = ParagraphStyle('ReceiptID', parent=styles['Normal'], fontSize=10,
                                      textColor=colors.HexColor('#888888'), alignment=TA_CENTER, spaceAfter=0.3*inch)
    story.append(Paragraph(f"ID: {rental_data['rental_id']}", receipt_id_style))
    
    # ========================================================================
    # CUSTOMER INFORMATION SECTION
    # ========================================================================
    
    # Section Header
    section_header_style = ParagraphStyle('SectionHeader', parent=styles['Heading3'], fontSize=12,
                                          textColor=primary_color, spaceAfter=0.1*inch, spaceBefore=0.2*inch)
    story.append(Paragraph("CUSTOMER INFORMATION", section_header_style))
    
    customer_data = [
        ['Customer Name:', rental_data['customer_name']],
        ['Email:', rental_data['customer_email']],
        ['Phone:', rental_data['customer_phone']],
        ['Date Issued:', datetime.date.today().strftime('%Y-%m-%d')]
    ]
    
    customer_table = Table(customer_data, colWidths=[1.5*inch, 3.5*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ========================================================================
    # RENTAL PERIOD SECTION
    # ========================================================================
    
    story.append(Paragraph("RENTAL PERIOD", section_header_style))
    
    days = (rental_data['return_date'] - rental_data['rental_date']).days
    period_data = [
        ['Check-out Date:', rental_data['rental_date'].strftime('%Y-%m-%d')],
        ['Return Date:', rental_data['return_date'].strftime('%Y-%m-%d')],
        ['Duration:', f"{days} day(s)"]
    ]
    
    period_table = Table(period_data, colWidths=[1.5*inch, 3.5*inch])
    period_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(period_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ========================================================================
    # ITEMS RENTED TABLE
    # ========================================================================
    
    story.append(Paragraph("ITEMS RENTED", section_header_style))
    
    # Table header
    item_table_data = [['Item', 'Daily Rate', 'Total']]
    
    for item in items_list:
        item_table_data.append([
            item['item_name'],
            f"KES {item['daily_rate']:,.2f}",
            f"KES {item['cost']:,.2f}"
        ])
    
    col_widths = [3.5*inch, 1.2*inch, 1.5*inch]
    item_table = Table(item_table_data, colWidths=col_widths, repeatRows=1)
    
    # Style the table
    table_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_gray),
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
    ]
    
    # Add alternating row colors
    for i in range(1, len(item_table_data)):
        if i % 2 == 1:
            table_style.append(('BACKGROUND', (0, i), (-1, i), light_gray))
    
    item_table.setStyle(TableStyle(table_style))
    story.append(item_table)
    story.append(Spacer(1, 0.25*inch))
    
    # ========================================================================
    # PAYMENT SUMMARY
    # ========================================================================
    
    story.append(Paragraph("PAYMENT SUMMARY", section_header_style))
    
    total_cost = rental_data['total_cost']
    deposit = rental_data['deposit_paid']
    balance = rental_data['balance_due']
    
    # Create a boxed summary
    summary_data = [
        ['Total Rental Cost:', f"KES {total_cost:,.2f}"],
        ['Deposit Paid (Today):', f"KES {deposit:,.2f}"],
        ['', ''],
        ['Balance Due on Return:', f"KES {balance:,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    
    summary_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -2), 8),
        ('TOPPADDING', (0, 0), (-1, -2), 8),
        ('FONTNAME', (0, 0), (0, -2), 'Helvetica-Bold'),
    ]
    
    # Highlight the balance due
    summary_style.append(('BACKGROUND', (1, 3), (1, 3), accent_color))
    summary_style.append(('TEXTCOLOR', (1, 3), (1, 3), colors.whitesmoke))
    summary_style.append(('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'))
    summary_style.append(('FONTSIZE', (1, 3), (1, 3), 14))
    
    summary_table.setStyle(TableStyle(summary_style))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Payment status badge
    status_bg = colors.HexColor('#d4edda')
    status_color = colors.HexColor('#155724')
    
    status_style = ParagraphStyle('PaymentStatus', parent=styles['Normal'], fontSize=10,
                                  textColor=status_color, alignment=TA_CENTER, spaceAfter=0.2*inch)
    story.append(Paragraph("✓ DEPOSIT PAYMENT RECEIVED", status_style))
    
    # Divider
    story.append(Paragraph("━" * 60, divider_style))
    
    # ========================================================================
    # TERMS & CONDITIONS
    # ========================================================================
    
    terms_title_style = ParagraphStyle('TermsTitle', parent=styles['Normal'], fontSize=9,
                                       textColor=primary_color, alignment=TA_CENTER, spaceAfter=5)
    story.append(Paragraph("<b>TERMS & CONDITIONS</b>", terms_title_style))
    
    terms_text = """
    1. Items must be returned by the specified return date.<br/>
    2. Late returns incur additional charges of KES 500 per day per item.<br/>
    3. Customer is fully responsible for any damage or loss of equipment.<br/>
    4. Deposit is non-refundable and secures the rental.<br/>
    5. Balance must be paid in full upon return of equipment.
    """
    
    terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=8,
                                 textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceAfter=0.2*inch)
    story.append(Paragraph(terms_text, terms_style))
    story.append(Spacer(1, 0.15*inch))
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                                  textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
    story.append(Paragraph("Thank you for choosing Feruzi Rentals!", footer_style))
    story.append(Paragraph("Follow us on Instagram: @feruzirentals", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

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
    .centered-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=[
        'item_id', 'item_name', 'category', 'brand', 'model', 
        'serial_number', 'daily_rate', 'status', 'current_renter'
    ])

if 'rentals' not in st.session_state:
    st.session_state.rentals = pd.DataFrame(columns=[
        'rental_id', 'customer_name', 'customer_email', 'customer_phone',
        'items_list', 'total_cost', 'deposit_paid', 'balance_due', 
        'rental_date', 'return_date', 'status'
    ])

if 'cart_items' not in st.session_state:
    st.session_state.cart_items = []

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Load data
    load_data()
    if st.session_state.inventory.empty:
        load_sample_data()
    
    # ========================================================================
    # SIDEBAR NAVIGATION
    # ========================================================================
    
    st.sidebar.markdown("---")
    logo_base64_sidebar = get_logo_image()
    if logo_base64_sidebar:
        col1, col2, col3 = st.sidebar.columns([1, 2, 1])
        with col2:
            st.image(f"data:image/png;base64,{logo_base64_sidebar}", use_container_width=True)
    else:
        st.sidebar.markdown("### FERUZI RENTALS")
        st.sidebar.markdown("*Film.Photography.Possibility.*")
    
    st.sidebar.markdown("---")
    st.sidebar.title("Navigation")
    
    menu = st.sidebar.selectbox(
        "Choose an option",
        ["Dashboard", "Inventory Management", "New Rental", "Active Rentals", "Return & Clear Balance", "Rental History", "Clear All Data"]
    )
    
    # ========================================================================
    # DASHBOARD
    # ========================================================================
    
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
            st.markdown(f"""
            <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #b8d9e8;">
                <div style="font-size: 2rem;">📷</div>
                <div style="font-size: 0.85rem; color: #2c3e50; font-weight: 600;">Available Items</div>
                <div style="font-size: 1.8rem; color: #1f77b4; font-weight: bold;">{available_items}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            rented_items = len(st.session_state.inventory[st.session_state.inventory['status'] == 'Rented'])
            st.markdown(f"""
            <div style="background-color: #fde8e8; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #f5c6c6;">
                <div style="font-size: 2rem;">🔴</div>
                <div style="font-size: 0.85rem; color: #2c3e50; font-weight: 600;">Rented Out</div>
                <div style="font-size: 1.8rem; color: #dc3545; font-weight: bold;">{rented_items}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            active_rentals = len(st.session_state.rentals[st.session_state.rentals['status'] == 'Active'])
            st.markdown(f"""
            <div style="background-color: #fff3e0; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #ffe0b3;">
                <div style="font-size: 2rem;">📝</div>
                <div style="font-size: 0.85rem; color: #2c3e50; font-weight: 600;">Active Rentals</div>
                <div style="font-size: 1.8rem; color: #ff9800; font-weight: bold;">{active_rentals}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if 'balance_due' in st.session_state.rentals.columns:
                active_mask = st.session_state.rentals['status'] == 'Active'
                total_outstanding = st.session_state.rentals.loc[active_mask, 'balance_due'].sum()
            else:
                total_outstanding = 0
            st.markdown(f"""
            <div style="background-color: #e8f5e9; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #c8e6c9;">
                <div style="font-size: 2rem;">💰</div>
                <div style="font-size: 0.85rem; color: #2c3e50; font-weight: 600;">Outstanding Balance</div>
                <div style="font-size: 1.4rem; color: #27ae60; font-weight: bold;">{format_kes(total_outstanding)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("Recent Rentals")
        if not st.session_state.rentals.empty:
            recent = st.session_state.rentals.tail(5)
            display_df = recent.copy()
            if 'deposit_paid' in display_df.columns:
                display_df['deposit_paid'] = display_df['deposit_paid'].apply(lambda x: format_kes(x))
            if 'balance_due' in display_df.columns:
                display_df['balance_due'] = display_df['balance_due'].apply(lambda x: format_kes(x))
            st.dataframe(display_df[['rental_id', 'customer_name', 'rental_date', 'return_date', 'deposit_paid', 'balance_due', 'status']], use_container_width=True)
        
        st.subheader("Current Inventory Status")
        inventory_display = st.session_state.inventory[['item_id', 'item_name', 'category', 'status', 'current_renter']].copy()
        st.dataframe(inventory_display, use_container_width=True)
    
    # ========================================================================
    # INVENTORY MANAGEMENT
    # ========================================================================
    
    elif menu == "Inventory Management":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(width=150)
        
        st.markdown('<h1 class="main-header">Inventory Management</h1>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Add New Item", "Edit/Delete Items", "View All Items"])
        
        with tab1:
            with st.form("add_item_form"):
                col1, col2 = st.columns(2)
                with col1:
                    item_id = st.text_input("Item ID*", placeholder="e.g., CAM001")
                    item_name = st.text_input("Item Name*", placeholder="e.g., Sony A7III")
                    category = st.selectbox("Category*", ["Camera Body", "Lens", "Lighting", "Tripod", "Audio", "Accessory"])
                    brand = st.text_input("Brand", placeholder="e.g., Sony, Canon")
                with col2:
                    model = st.text_input("Model", placeholder="e.g., A7III")
                    serial_number = st.text_input("Serial Number*")
                    daily_rate = st.number_input("Daily Rate (KES)*", min_value=0.0, step=500.0, value=5000.0)
                    status = st.selectbox("Status", ["Available", "Rented", "Maintenance"])
                
                if st.form_submit_button("Add Item"):
                    if item_id and item_name and serial_number and daily_rate > 0:
                        new_item = pd.DataFrame([{
                            'item_id': item_id, 'item_name': item_name, 'category': category,
                            'brand': brand, 'model': model, 'serial_number': serial_number,
                            'daily_rate': daily_rate, 'status': status, 'current_renter': ''
                        }])
                        st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                        fix_dataframe_dtypes()
                        save_data()
                        st.success(f"{item_name} added successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields (*)")
        
        with tab2:
            if not st.session_state.inventory.empty:
                item_to_edit = st.selectbox("Select item to edit", st.session_state.inventory['item_name'])
                if item_to_edit:
                    item_data = st.session_state.inventory[st.session_state.inventory['item_name'] == item_to_edit].iloc[0]
                    with st.form("edit_item_form"):
                        new_item_name = st.text_input("Item Name", value=item_data['item_name'])
                        new_rate = st.number_input("Daily Rate (KES)", value=float(item_data['daily_rate']), step=500.0)
                        new_status = st.selectbox("Status", ["Available", "Rented", "Maintenance"])
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update"):
                                st.session_state.inventory.loc[st.session_state.inventory['item_name'] == item_to_edit, 'item_name'] = new_item_name
                                st.session_state.inventory.loc[st.session_state.inventory['item_name'] == new_item_name, 'daily_rate'] = new_rate
                                st.session_state.inventory.loc[st.session_state.inventory['item_name'] == new_item_name, 'status'] = new_status
                                fix_dataframe_dtypes()
                                save_data()
                                st.success("Item updated!")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Delete", type="secondary"):
                                st.session_state.inventory = st.session_state.inventory[st.session_state.inventory['item_name'] != item_to_edit]
                                save_data()
                                st.warning("Item deleted!")
                                st.rerun()
        
        with tab3:
            display_df = st.session_state.inventory.copy()
            display_df['daily_rate'] = display_df['daily_rate'].apply(lambda x: format_kes(x))
            st.dataframe(display_df, use_container_width=True)
            if st.button("Export to CSV"):
                csv = st.session_state.inventory.to_csv(index=False)
                st.download_button("Download Inventory CSV", csv, "inventory_export.csv", "text/csv")
    
    # ========================================================================
    # NEW RENTAL (Multi-Item Support)
    # ========================================================================
    
    elif menu == "New Rental":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(width=150)
        
        st.markdown('<h1 class="main-header">Create New Rental</h1>', unsafe_allow_html=True)
        
        available_items = st.session_state.inventory[st.session_state.inventory['status'] == 'Available']
        
        if available_items.empty:
            st.warning("No items available for rent.")
        else:
            if 'rental_created' not in st.session_state:
                st.session_state.rental_created = False
                st.session_state.last_rental_data = None
            
            with st.form("rental_form"):
                col1, col2 = st.columns(2)
                with col1:
                    customer_name = st.text_input("Customer Name*")
                    customer_email = st.text_input("Email*")
                    customer_phone = st.text_input("Phone Number*", placeholder="e.g., 0712345678")
                
                with col2:
                    rental_date = st.date_input("Rental Date", datetime.date.today())
                    return_date = st.date_input("Return Date", datetime.date.today() + timedelta(days=3))
                
                st.markdown("---")
                st.subheader("Select Items to Rent")
                
                selected_items = st.multiselect(
                    "Select items to rent",
                    available_items['item_name'].tolist(),
                    help="You can select multiple items"
                )
                
                if selected_items:
                    st.write("**Selected Items:**")
                    items_data = []
                    total_rental_cost = 0
                    days = (return_date - rental_date).days if return_date > rental_date else 0
                    
                    for item_name in selected_items:
                        item_details = available_items[available_items['item_name'] == item_name].iloc[0]
                        daily_rate = float(item_details['daily_rate'])
                        item_cost = days * daily_rate if days > 0 else 0
                        total_rental_cost += item_cost
                        items_data.append({
                            'item_name': item_name,
                            'item_id': str(item_details['item_id']),
                            'daily_rate': daily_rate,
                            'cost': item_cost
                        })
                    
                    items_df = pd.DataFrame(items_data)
                    items_df['daily_rate'] = items_df['daily_rate'].apply(lambda x: format_kes(x))
                    items_df['cost'] = items_df['cost'].apply(lambda x: format_kes(x))
                    st.dataframe(items_df[['item_name', 'daily_rate', 'cost']], use_container_width=True)
                    
                    if days > 0:
                        st.info(f"Rental Period: {days} days")
                        st.success(f"Total Rental Cost: {format_kes(total_rental_cost)}")
                    else:
                        st.error("Return date must be after rental date!")
                
                st.markdown("---")
                deposit = st.number_input("Deposit Amount (KES)*", min_value=0.0, value=5000.0, step=1000.0,
                                         help="Amount customer pays today")
                
                if selected_items and days > 0:
                    balance_due = total_rental_cost - deposit
                    if balance_due > 0:
                        st.warning(f"Balance Due on Return: {format_kes(balance_due)}")
                    elif balance_due < 0:
                        st.error(f"Deposit exceeds total cost! Please reduce deposit amount.")
                    else:
                        st.success(f"Fully paid! No balance due.")
                
                submitted = st.form_submit_button("Create Rental")
            
            if submitted:
                if customer_name and customer_email and customer_phone and selected_items:
                    days = (return_date - rental_date).days
                    if days > 0:
                        total_rental_cost = 0
                        items_for_storage = []
                        
                        for item_name in selected_items:
                            item_details = available_items[available_items['item_name'] == item_name].iloc[0]
                            daily_rate = float(item_details['daily_rate'])
                            item_cost = days * daily_rate
                            total_rental_cost += item_cost
                            items_for_storage.append({
                                'item_id': str(item_details['item_id']),
                                'item_name': item_name,
                                'daily_rate': daily_rate,
                                'cost': item_cost
                            })
                        
                        balance_due = total_rental_cost - deposit
                        
                        if balance_due < 0:
                            st.error("Deposit cannot exceed total rental cost!")
                        else:
                            rental_id = f"RENT{str(uuid.uuid4())[:8].upper()}"
                            items_json = json.dumps(items_for_storage)
                            
                            new_rental = pd.DataFrame([{
                                'rental_id': rental_id,
                                'customer_name': str(customer_name),
                                'customer_email': str(customer_email),
                                'customer_phone': str(customer_phone),
                                'items_list': items_json,
                                'total_cost': float(total_rental_cost),
                                'deposit_paid': float(deposit),
                                'balance_due': float(balance_due),
                                'rental_date': rental_date,
                                'return_date': return_date,
                                'status': 'Active'
                            }])
                            
                            st.session_state.rentals = pd.concat([st.session_state.rentals, new_rental], ignore_index=True)
                            
                            for item in items_for_storage:
                                item_index = st.session_state.inventory[st.session_state.inventory['item_id'] == item['item_id']].index
                                if len(item_index) > 0:
                                    st.session_state.inventory.at[item_index[0], 'status'] = 'Rented'
                                    st.session_state.inventory.at[item_index[0], 'current_renter'] = str(customer_name)
                            
                            fix_dataframe_dtypes()
                            save_data()
                            
                            st.session_state.rental_created = True
                            st.session_state.last_rental_data = new_rental.iloc[0].to_dict()
                            st.session_state.last_rental_data['items'] = items_for_storage
                            st.rerun()
                    else:
                        st.error("Please ensure return date is after rental date!")
                else:
                    st.error("Please fill in all customer information and select at least one item!")
            
            if st.session_state.rental_created and st.session_state.last_rental_data:
                items = st.session_state.last_rental_data.get('items', [])
                days_calc = (st.session_state.last_rental_data['return_date'] - st.session_state.last_rental_data['rental_date']).days
                
                st.success(f"Rental created! ID: {st.session_state.last_rental_data['rental_id']}")
                st.info(f"Customer: {st.session_state.last_rental_data['customer_name']}")
                st.info(f"Rental Period: {days_calc} days")
                
                st.subheader("Items Rented:")
                for item in items:
                    st.write(f"  • {item['item_name']} - {format_kes(item['daily_rate'])}/day = {format_kes(item['cost'])}")
                
                st.info(f"Total Rental Cost: {format_kes(st.session_state.last_rental_data['total_cost'])}")
                st.info(f"Deposit paid: {format_kes(st.session_state.last_rental_data['deposit_paid'])}")
                st.info(f"Balance due on return: {format_kes(st.session_state.last_rental_data['balance_due'])}")
                
                pdf_buffer = create_multi_item_receipt_pdf(st.session_state.last_rental_data, items)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.download_button("Download Receipt", data=pdf_buffer,
                                         file_name=f"receipt_{st.session_state.last_rental_data['rental_id']}.pdf",
                                         mime="application/pdf", key="download_receipt"):
                        st.balloons()
                
                if st.button("Create Another Rental", key="new_rental_btn"):
                    st.session_state.rental_created = False
                    st.session_state.last_rental_data = None
                    st.rerun()
    
    # ========================================================================
    # ACTIVE RENTALS
    # ========================================================================
    
    elif menu == "Active Rentals":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(width=150)
        
        st.markdown('<h1 class="main-header">Active Rentals</h1>', unsafe_allow_html=True)
        
        active = st.session_state.rentals[st.session_state.rentals['status'] == 'Active']
        
        if active.empty:
            st.info("No active rentals at the moment.")
        else:
            for _, rental in active.iterrows():
                with st.expander(f"Rental #{rental['rental_id']} - {rental['customer_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Customer:** {rental['customer_name']}")
                        st.write(f"**Email:** {rental['customer_email']}")
                        st.write(f"**Phone:** {rental['customer_phone']}")
                    with col2:
                        st.write(f"**Rental Date:** {rental['rental_date']}")
                        st.write(f"**Return Date:** {rental['return_date']}")
                        days_left = (rental['return_date'] - datetime.date.today()).days
                        if days_left >= 0:
                            st.info(f"{days_left} days left until return")
                        else:
                            st.warning(f"Rental is {abs(days_left)} days overdue!")
                    
                    st.write("**Items Rented:**")
                    items = json.loads(rental['items_list'])
                    for item in items:
                        st.write(f"  • {item['item_name']} - {format_kes(item['daily_rate'])}/day")
                    
                    st.write(f"**Total Cost:** {format_kes(rental['total_cost'])}")
                    st.write(f"**Deposit Paid:** {format_kes(rental['deposit_paid'])}")
                    st.write(f"**Balance Due:** {format_kes(rental['balance_due'])}")
    
    # ========================================================================
    # RETURN & CLEAR BALANCE
    # ========================================================================
    
    elif menu == "Return & Clear Balance":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(width=150)
        
        st.markdown('<h1 class="main-header">Return Item & Clear Balance</h1>', unsafe_allow_html=True)
        
        active_rentals = st.session_state.rentals[st.session_state.rentals['status'] == 'Active']
        
        if active_rentals.empty:
            st.info("No active rentals to return.")
        else:
            rental_to_return = st.selectbox("Select rental to return", 
                                           active_rentals.apply(lambda x: f"{x['rental_id']} - {x['customer_name']}", axis=1))
            
            if rental_to_return:
                rental_id = rental_to_return.split(" - ")[0]
                rental_data = st.session_state.rentals[st.session_state.rentals['rental_id'] == rental_id].iloc[0]
                
                st.write("### Rental Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Customer:** {rental_data['customer_name']}")
                    st.write(f"**Email:** {rental_data['customer_email']}")
                    st.write(f"**Phone:** {rental_data['customer_phone']}")
                    st.write(f"**Rental Date:** {rental_data['rental_date']}")
                with col2:
                    st.write(f"**Return Date:** {rental_data['return_date']}")
                    st.write(f"**Total Cost:** {format_kes(rental_data['total_cost'])}")
                    st.write(f"**Deposit Paid:** {format_kes(rental_data['deposit_paid'])}")
                    st.write(f"**Balance Due:** {format_kes(rental_data['balance_due'])}")
                
                st.write("**Items Rented:**")
                items = json.loads(rental_data['items_list'])
                for item in items:
                    st.write(f"  • {item['item_name']}")
                
                today = datetime.date.today()
                late_fee = 0
                if today > rental_data['return_date']:
                    days_late = (today - rental_data['return_date']).days
                    late_fee = days_late * 500 * len(items)
                    st.warning(f"{days_late} days late. Late fee: {format_kes(late_fee)}")
                
                col3, col4 = st.columns(2)
                with col3:
                    damage_fee = st.number_input("Damage Fee (KES)", min_value=0.0, step=500.0, value=0.0)
                with col4:
                    balance_paid = st.number_input("Balance Payment Received (KES)", 
                                                   min_value=0.0, 
                                                   max_value=rental_data['balance_due'] + late_fee + damage_fee,
                                                   value=rental_data['balance_due'] + late_fee + damage_fee,
                                                   step=500.0)
                
                total_due = rental_data['balance_due'] + late_fee + damage_fee
                st.info(f"Total amount due: {format_kes(total_due)}")
                
                if balance_paid < total_due:
                    st.warning(f"Short payment of {format_kes(total_due - balance_paid)}")
                elif balance_paid > total_due:
                    st.success(f"Overpayment of {format_kes(balance_paid - total_due)} (refund to customer)")
                
                if st.button("Process Return & Clear Balance"):
                    st.session_state.rentals.loc[st.session_state.rentals['rental_id'] == rental_id, 'status'] = 'Completed'
                    st.session_state.rentals.loc[st.session_state.rentals['rental_id'] == rental_id, 'balance_due'] = 0
                    
                    for item in items:
                        item_index = st.session_state.inventory[st.session_state.inventory['item_id'] == item['item_id']].index
                        if len(item_index) > 0:
                            st.session_state.inventory.at[item_index[0], 'status'] = 'Available'
                            st.session_state.inventory.at[item_index[0], 'current_renter'] = ''
                    
                    fix_dataframe_dtypes()
                    save_data()
                    
                    st.success("Return processed successfully!")
                    
                    if balance_paid > total_due:
                        st.info(f"Refund due to customer: {format_kes(balance_paid - total_due)}")
                    elif balance_paid < total_due:
                        st.warning(f"Outstanding balance: {format_kes(total_due - balance_paid)}")
                    else:
                        st.success("Balance fully cleared!")
                    
                    st.balloons()
                    st.rerun()
    
    # ========================================================================
    # RENTAL HISTORY
    # ========================================================================
    
    elif menu == "Rental History":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(width=150)
        
        st.markdown('<h1 class="main-header">Rental History</h1>', unsafe_allow_html=True)
        
        if st.session_state.rentals.empty:
            st.info("No rental history available.")
        else:
            status_filter = st.selectbox("Filter by status", ["All", "Active", "Completed"])
            
            if status_filter == "All":
                filtered = st.session_state.rentals
            else:
                filtered = st.session_state.rentals[st.session_state.rentals['status'] == status_filter]
            
            for _, rental in filtered.iterrows():
                with st.expander(f"Rental #{rental['rental_id']} - {rental['customer_name']} - {rental['status']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Customer:** {rental['customer_name']}")
                        st.write(f"**Email:** {rental['customer_email']}")
                        st.write(f"**Phone:** {rental['customer_phone']}")
                    with col2:
                        st.write(f"**Rental Date:** {rental['rental_date']}")
                        st.write(f"**Return Date:** {rental['return_date']}")
                        st.write(f"**Status:** {rental['status']}")
                    
                    st.write("**Items Rented:**")
                    items = json.loads(rental['items_list'])
                    for item in items:
                        st.write(f"  • {item['item_name']} - {format_kes(item['daily_rate'])}/day")
                    
                    st.write(f"**Total Cost:** {format_kes(rental['total_cost'])}")
                    st.write(f"**Deposit Paid:** {format_kes(rental['deposit_paid'])}")
                    st.write(f"**Balance Due:** {format_kes(rental['balance_due'])}")
            
            st.markdown("---")
            st.subheader("Rental Statistics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                total_rentals = len(st.session_state.rentals)
                st.metric("Total Rentals", total_rentals)
            with col2:
                total_revenue = st.session_state.rentals['total_cost'].sum()
                st.metric("Total Revenue", format_kes(total_revenue))
            with col3:
                unique_customers = st.session_state.rentals['customer_name'].nunique()
                st.metric("Unique Customers", unique_customers)
    
    # ========================================================================
    # CLEAR ALL DATA
    # ========================================================================
    
    elif menu == "Clear All Data":
        st.markdown('<h1 class="main-header">Clear All Data</h1>', unsafe_allow_html=True)
        
        st.warning("⚠️ WARNING: This will delete ALL inventory and rental data!")
        st.write("This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear All Data", type="secondary"):
                st.session_state.inventory = pd.DataFrame(columns=[
                    'item_id', 'item_name', 'category', 'brand', 'model', 
                    'serial_number', 'daily_rate', 'status', 'current_renter'
                ])
                
                st.session_state.rentals = pd.DataFrame(columns=[
                    'rental_id', 'customer_name', 'customer_email', 'customer_phone',
                    'items_list', 'total_cost', 'deposit_paid', 'balance_due', 
                    'rental_date', 'return_date', 'status'
                ])
                
                load_sample_data()
                fix_dataframe_dtypes()
                save_data()
                
                st.success("All data has been cleared and sample data loaded!")
                st.balloons()
                st.rerun()
        
        with col2:
            if st.button("Load Sample Data Only"):
                load_sample_data()
                fix_dataframe_dtypes()
                save_data()
                st.success("Sample data loaded!")
                st.rerun()
        
        st.markdown("---")
        st.subheader("Current Data Status")
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Inventory Items", len(st.session_state.inventory))
        with col4:
            st.metric("Rental Records", len(st.session_state.rentals))

# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == "__main__":
    main()
