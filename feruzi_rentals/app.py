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
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import io
import base64
import requests

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
    # Fix inventory dataframe
    if 'current_renter' in st.session_state.inventory.columns:
        st.session_state.inventory['current_renter'] = st.session_state.inventory['current_renter'].astype(str)
        st.session_state.inventory['current_renter'] = st.session_state.inventory['current_renter'].replace('nan', '')
    
    if 'item_id' in st.session_state.inventory.columns:
        st.session_state.inventory['item_id'] = st.session_state.inventory['item_id'].astype(str)
    
    if 'status' in st.session_state.inventory.columns:
        st.session_state.inventory['status'] = st.session_state.inventory['status'].astype(str)
    
    # Fix rentals dataframe
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
        
        # Fix data types after loading
        fix_dataframe_dtypes()
        
    except Exception as e:
        st.error(f"Error loading data: {e}")

def load_sample_data():
    """Load sample data if no data exists"""
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
                'status': 'Available',
                'current_renter': ''
            }
        ]
        st.session_state.inventory = pd.DataFrame(sample_items)

# ============================================================================
# PDF RECEIPT GENERATION
# ============================================================================

def create_receipt_pdf(rental_data):
    """Generate PDF receipt for rental"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # ========================================================================
    # ADD LOGO TO PDF - Using the same logic as the app
    # ========================================================================
    
    logo_added = False
    
    # Try to get logo from various sources
    logo_paths_to_try = [
        "feruzi_logo.png",
        "logo.png", 
        "favicon.ico",
        os.path.join(APP_DIR, "feruzi_logo.png"),
        os.path.join(APP_DIR, "logo.png"),
    ]
    
    for logo_path in logo_paths_to_try:
        if os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=2*inch, height=2*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
                logo_added = True
                break
            except Exception as e:
                continue
    
    # If no local logo found, try to use base64 encoded logo from get_logo_image()
    if not logo_added:
        logo_base64_data = get_logo_image()
        if logo_base64_data:
            try:
                # Decode base64 to bytes and save temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_file.write(base64.b64decode(logo_base64_data))
                    tmp_path = tmp_file.name
                
                img = Image(tmp_path, width=2*inch, height=2*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
                logo_added = True
                
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            except Exception as e:
                pass
    
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

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

# Page config with favicon
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
        'item_id', 'item_name', 'rental_date', 'return_date', 
        'total_cost', 'deposit_paid', 'balance_due', 'status', 'daily_rate'
    ])

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
        st.sidebar.markdown("### 📷 FERUZI RENTALS")
        st.sidebar.markdown("*Film.Photography.Possibility.*")
    
    st.sidebar.markdown("---")
    st.sidebar.title("📋 Navigation")
    
    menu = st.sidebar.selectbox(
        "Choose an option",
        ["Dashboard", "Inventory Management", "New Rental", "Active Rentals", "Return & Clear Balance", "Rental History"]
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
        
        # Metrics
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
        
        # Recent Rentals
        st.subheader("📊 Recent Rentals")
        if not st.session_state.rentals.empty:
            recent = st.session_state.rentals.tail(5)
            display_df = recent.copy()
            if 'deposit_paid' in display_df.columns:
                display_df['deposit_paid'] = display_df['deposit_paid'].apply(lambda x: format_kes(x))
            if 'balance_due' in display_df.columns:
                display_df['balance_due'] = display_df['balance_due'].apply(lambda x: format_kes(x))
            columns_to_show = ['rental_id', 'customer_name', 'item_name', 'rental_date', 'return_date', 'deposit_paid', 'balance_due', 'status']
            available_cols = [col for col in columns_to_show if col in display_df.columns]
            st.dataframe(display_df[available_cols], use_container_width=True)
        
        # Inventory Status
        st.subheader("📦 Current Inventory Status")
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
                        st.success(f"✅ {item_name} added successfully!")
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
                                st.success("✅ Item updated!")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Delete", type="secondary"):
                                st.session_state.inventory = st.session_state.inventory[st.session_state.inventory['item_name'] != item_to_edit]
                                save_data()
                                st.warning("🗑️ Item deleted!")
                                st.rerun()
        
        with tab3:
            display_df = st.session_state.inventory.copy()
            display_df['daily_rate'] = display_df['daily_rate'].apply(lambda x: format_kes(x))
            st.dataframe(display_df, use_container_width=True)
            if st.button("Export to CSV"):
                csv = st.session_state.inventory.to_csv(index=False)
                st.download_button("Download Inventory CSV", csv, "inventory_export.csv", "text/csv")
    
    # ========================================================================
    # NEW RENTAL
    # ========================================================================
    
    elif menu == "New Rental":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(width=150)
        
        st.markdown('<h1 class="main-header">Create New Rental</h1>', unsafe_allow_html=True)
        
        available_items = st.session_state.inventory[st.session_state.inventory['status'] == 'Available']
        
        if available_items.empty:
            st.warning("⚠️ No items available for rent.")
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
                    selected_item = st.selectbox("Select Item to Rent*", available_items['item_name'].tolist())
                    item_details = available_items[available_items['item_name'] == selected_item].iloc[0]
                    daily_rate = float(item_details['daily_rate'])
                    st.info(f"Daily Rate: {format_kes(daily_rate)}")
                
                col3, col4, col5 = st.columns(3)
                with col3:
                    rental_date = st.date_input("Rental Date", datetime.date.today())
                with col4:
                    return_date = st.date_input("Return Date", datetime.date.today() + timedelta(days=3))
                with col5:
                    deposit = st.number_input("Deposit Amount (KES)*", min_value=0.0, value=5000.0, step=1000.0,
                                             help="Amount customer pays today")
                
                if rental_date and return_date:
                    days = (return_date - rental_date).days
                    if days > 0:
                        total_cost = days * daily_rate
                        balance_due = total_cost - deposit
                        st.success(f"💰 Total Rental Cost: {format_kes(total_cost)} for {days} days")
                        st.info(f"💰 Deposit Paid Today: {format_kes(deposit)}")
                        if balance_due > 0:
                            st.warning(f"💰 Balance Due on Return: {format_kes(balance_due)}")
                        elif balance_due < 0:
                            st.error(f"⚠️ Deposit exceeds total cost! Please reduce deposit amount.")
                        else:
                            st.success(f"✅ Fully paid! No balance due.")
                    else:
                        st.error("Return date must be after rental date!")
                
                submitted = st.form_submit_button("Create Rental")
            
            if submitted:
                if customer_name and customer_email and customer_phone and selected_item:
                    days = (return_date - rental_date).days
                    if days > 0:
                        current_daily_rate = float(item_details['daily_rate'])
                        total_cost = days * current_daily_rate
                        balance_due = total_cost - deposit
                        
                        if balance_due < 0:
                            st.error("Deposit cannot exceed total rental cost!")
                        else:
                            rental_id = f"RENT{str(uuid.uuid4())[:8].upper()}"
                            
                            new_rental = pd.DataFrame([{
                                'rental_id': rental_id,
                                'customer_name': str(customer_name),
                                'customer_email': str(customer_email),
                                'customer_phone': str(customer_phone),
                                'item_id': str(item_details['item_id']),
                                'item_name': str(selected_item),
                                'rental_date': rental_date,
                                'return_date': return_date,
                                'total_cost': float(total_cost),
                                'deposit_paid': float(deposit),
                                'balance_due': float(balance_due),
                                'status': 'Active',
                                'daily_rate': current_daily_rate
                            }])
                            
                            st.session_state.rentals = pd.concat([st.session_state.rentals, new_rental], ignore_index=True)
                            
                            # Update inventory
                            item_index = st.session_state.inventory[st.session_state.inventory['item_id'] == str(item_details['item_id'])].index
                            if len(item_index) > 0:
                                st.session_state.inventory.at[item_index[0], 'status'] = 'Rented'
                                st.session_state.inventory.at[item_index[0], 'current_renter'] = str(customer_name)
                            
                            fix_dataframe_dtypes()
                            save_data()
                            
                            st.session_state.rental_created = True
                            st.session_state.last_rental_data = new_rental.iloc[0].to_dict()
                            st.rerun()
                    else:
                        st.error("Please ensure return date is after rental date!")
                else:
                    st.error("Please fill in all customer information!")
            
            if st.session_state.rental_created and st.session_state.last_rental_data:
                days_calc = (st.session_state.last_rental_data['return_date'] - st.session_state.last_rental_data['rental_date']).days
                correct_total = days_calc * st.session_state.last_rental_data['daily_rate']
                correct_balance = correct_total - st.session_state.last_rental_data['deposit_paid']
                
                st.success(f"✅ Rental created! ID: {st.session_state.last_rental_data['rental_id']}")
                st.info(f"💰 Total Rental Cost: {format_kes(correct_total)}")
                st.info(f"💰 Deposit paid: {format_kes(st.session_state.last_rental_data['deposit_paid'])}")
                st.info(f"💰 Balance due on return: {format_kes(correct_balance)}")
                
                pdf_buffer = create_receipt_pdf(st.session_state.last_rental_data)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.download_button("📄 Download Receipt", data=pdf_buffer,
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
            display_active = active.copy()
            if 'deposit_paid' in display_active.columns:
                display_active['deposit_paid'] = display_active['deposit_paid'].apply(lambda x: format_kes(x))
            if 'balance_due' in display_active.columns:
                display_active['balance_due'] = display_active['balance_due'].apply(lambda x: format_kes(x))
            st.dataframe(display_active[['rental_id', 'customer_name', 'item_name', 'rental_date', 'return_date', 'deposit_paid', 'balance_due']], use_container_width=True)
            
            for _, rental in active.iterrows():
                with st.expander(f"Rental #{rental['rental_id']} - {rental['customer_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Item:** {rental['item_name']}")
                        st.write(f"**Rental Date:** {rental['rental_date']}")
                        st.write(f"**Return Date:** {rental['return_date']}")
                    with col2:
                        st.write(f"**Total Cost:** {format_kes(rental['total_cost'])}")
                        st.write(f"**Deposit Paid:** {format_kes(rental['deposit_paid'])}")
                        st.write(f"**Balance Due:** {format_kes(rental['balance_due'])}")
                        days_left = (rental['return_date'] - datetime.date.today()).days
                        if days_left >= 0:
                            st.info(f"⏰ {days_left} days left until return")
                        else:
                            st.warning(f"⚠️ Rental is {abs(days_left)} days overdue!")
    
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
                                           active_rentals.apply(lambda x: f"{x['rental_id']} - {x['customer_name']} - {x['item_name']}", axis=1))
            
            if rental_to_return:
                rental_id = rental_to_return.split(" - ")[0]
                rental_data = st.session_state.rentals[st.session_state.rentals['rental_id'] == rental_id].iloc[0]
                
                st.write("### Rental Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Customer:** {rental_data['customer_name']}")
                    st.write(f"**Item:** {rental_data['item_name']}")
                    st.write(f"**Rental Date:** {rental_data['rental_date']}")
                with col2:
                    st.write(f"**Return Date:** {rental_data['return_date']}")
                    st.write(f"**Total Cost:** {format_kes(rental_data['total_cost'])}")
                    st.write(f"**Deposit Paid:** {format_kes(rental_data['deposit_paid'])}")
                    st.write(f"**Balance Due:** {format_kes(rental_data['balance_due'])}")
                
                # Calculate late fees
                today = datetime.date.today()
                late_fee = 0
                if today > rental_data['return_date']:
                    days_late = (today - rental_data['return_date']).days
                    late_fee = days_late * 500
                    st.warning(f"⚠️ {days_late} days late. Late fee: {format_kes(late_fee)}")
                
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
                st.info(f"💰 Total amount due: {format_kes(total_due)}")
                
                if balance_paid < total_due:
                    st.warning(f"⚠️ Short payment of {format_kes(total_due - balance_paid)}")
                elif balance_paid > total_due:
                    st.success(f"💰 Overpayment of {format_kes(balance_paid - total_due)} (refund to customer)")
                
                if st.button("Process Return & Clear Balance"):
                    st.session_state.rentals.loc[st.session_state.rentals['rental_id'] == rental_id, 'status'] = 'Completed'
                    st.session_state.rentals.loc[st.session_state.rentals['rental_id'] == rental_id, 'balance_due'] = 0
                    
                    # Update inventory
                    item_index = st.session_state.inventory[st.session_state.inventory['item_id'] == str(rental_data['item_id'])].index
                    if len(item_index) > 0:
                        st.session_state.inventory.at[item_index[0], 'status'] = 'Available'
                        st.session_state.inventory.at[item_index[0], 'current_renter'] = ''
                    
                    fix_dataframe_dtypes()
                    save_data()
                    
                    st.success("✅ Return processed successfully!")
                    
                    if balance_paid > total_due:
                        st.info(f"💰 Refund due to customer: {format_kes(balance_paid - total_due)}")
                    elif balance_paid < total_due:
                        st.warning(f"⚠️ Outstanding balance: {format_kes(total_due - balance_paid)}")
                    else:
                        st.success("✅ Balance fully cleared!")
                    
                    st.balloons()
    
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
            
            display_filtered = filtered.copy()
            if 'total_cost' in display_filtered.columns:
                display_filtered['total_cost'] = display_filtered['total_cost'].apply(lambda x: format_kes(x))
            if 'deposit_paid' in display_filtered.columns:
                display_filtered['deposit_paid'] = display_filtered['deposit_paid'].apply(lambda x: format_kes(x))
            if 'balance_due' in display_filtered.columns:
                display_filtered['balance_due'] = display_filtered['balance_due'].apply(lambda x: format_kes(x))
            
            st.dataframe(display_filtered[['rental_id', 'customer_name', 'item_name', 'rental_date', 'return_date', 'deposit_paid', 'balance_due', 'status']], use_container_width=True)
            
            st.markdown("---")
            st.subheader("📈 Rental Statistics")
            
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

# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == "__main__":
    main()
