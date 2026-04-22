# app.py - Updated with centered logo
import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import uuid
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io
from PIL import Image as PILImage
import base64

# Function to format currency in KES
def format_kes(amount):
    return f"KES {amount:,.2f}"

# Page configuration with favicon
favicon_path = "feruzi_logo.png"
if os.path.exists(favicon_path):
    with open(favicon_path, "rb") as f:
        favicon_bytes = f.read()
        favicon_base64 = base64.b64encode(favicon_bytes).decode()
    st.set_page_config(
        page_title="Feruzi Rentals - Camera Inventory System",
        page_icon=f"data:image/png;base64,{favicon_base64}",
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

# Custom CSS for better styling and centered elements
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
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .logo-text {
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        margin-top: 0.5rem;
    }
    /* Center align the logo container */
    .stImage {
        display: flex;
        justify-content: center;
    }
    /* Center the logo in the dashboard */
    .centered-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    /* Center content in columns */
    .centered {
        text-align: center;
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
        'total_cost', 'status', 'deposit_paid'
    ])

# Load sample data if empty
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
            'status': 'Active',
            'deposit_paid': 10000.0
        }
        st.session_state.rentals = pd.DataFrame([sample_rental])

# Save data to CSV
def save_data():
    st.session_state.inventory.to_csv('inventory.csv', index=False)
    st.session_state.rentals.to_csv('rentals.csv', index=False)

def load_data():
    if os.path.exists('inventory.csv'):
        st.session_state.inventory = pd.read_csv('inventory.csv')
    if os.path.exists('rentals.csv'):
        st.session_state.rentals = pd.read_csv('rentals.csv')
        # Convert date columns
        if 'rental_date' in st.session_state.rentals.columns:
            st.session_state.rentals['rental_date'] = pd.to_datetime(st.session_state.rentals['rental_date']).dt.date
        if 'return_date' in st.session_state.rentals.columns:
            st.session_state.rentals['return_date'] = pd.to_datetime(st.session_state.rentals['return_date']).dt.date

# Function to create receipt PDF with logo
def create_receipt_pdf(rental_data, logo_path="feruzi_logo.png"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Add logo if exists
    if os.path.exists(logo_path):
        try:
            # Load and resize logo for PDF
            img = Image(logo_path, width=2*inch, height=2*inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            st.warning(f"Could not load logo for PDF: {e}")
    
    # Company header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    story.append(Paragraph("FERUZI RENTALS", title_style))
    story.append(Paragraph("FILM.PHOTOGRAPHY.POSSIBILITY.", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Receipt title
    receipt_title = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
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
    rental_details = [
        ['Item Rented:', rental_data['item_name']],
        ['Rental Date:', rental_data['rental_date'].strftime('%Y-%m-%d')],
        ['Return Date:', rental_data['return_date'].strftime('%Y-%m-%d')],
        ['Duration (Days):', str((rental_data['return_date'] - rental_data['rental_date']).days)],
        ['Daily Rate:', f"KES {daily_rate:,.2f}"],
        ['Subtotal:', f"KES {rental_data.get('total_cost', 0) - rental_data.get('deposit_paid', 0):,.2f}"],
        ['Deposit Paid:', f"KES {rental_data.get('deposit_paid', 0):,.2f}"],
        ['Total Paid:', f"KES {rental_data.get('total_cost', 0):,.2f}"]
    ]
    
    rental_table = Table(rental_details, colWidths=[1.5*inch, 3*inch])
    rental_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(rental_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Terms and conditions
    terms_style = ParagraphStyle(
        'Terms',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    terms_text = """
    <b>Terms & Conditions:</b><br/>
    1. Items must be returned by the specified return date<br/>
    2. Late returns will incur additional daily charges of KES 500 per day<br/>
    3. Customer is responsible for any damage to equipment<br/>
    4. Deposit is refundable upon return of undamaged equipment
    """
    
    story.append(Paragraph(terms_text, terms_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Thank you for choosing Feruzi Rentals!", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Function to display centered logo
def display_centered_logo(logo_path="feruzi_logo.png", width=200):
    if os.path.exists(logo_path):
        # Use HTML to center the image
        with open(logo_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
        
        centered_logo_html = f"""
        <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
            <img src="data:image/png;base64,{img_base64}" width="{width}" style="object-fit: contain;">
        </div>
        """
        st.markdown(centered_logo_html, unsafe_allow_html=True)
        return True
    return False

# Main app
def main():
    # Load data
    load_data()
    if st.session_state.inventory.empty:
        load_sample_data()
    
    # Sidebar with centered logo
    st.sidebar.markdown("---")
    
    # Center logo in sidebar using columns
    logo_path = "feruzi_logo.png"
    if os.path.exists(logo_path):
        # Create columns to center the logo in sidebar
        col1, col2, col3 = st.sidebar.columns([1, 2, 1])
        with col2:
            try:
                st.image(logo_path, use_container_width=True)
            except:
                st.markdown("### 📷 FERUZI RENTALS")
    else:
        st.sidebar.markdown("### 📷 FERUZI RENTALS")
        st.sidebar.markdown("*Film.Photography.Possibility.*")
    
    st.sidebar.markdown("---")
    st.sidebar.title("📋 Navigation")
    
    menu = st.sidebar.selectbox(
        "Choose an option",
        ["Dashboard", "Inventory Management", "New Rental", "Active Rentals", "Return Item", "Rental History"]
    )
    
    # Dashboard
    if menu == "Dashboard":
        # Display centered logo at the top of dashboard
        st.markdown("---")
        
        # Center the logo using columns
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(logo_path, width=250)
        
        # Company name and tagline centered
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
            completed_rentals = st.session_state.rentals[st.session_state.rentals['status'] == 'Completed']
            total_revenue = completed_rentals['total_cost'].sum() if not completed_rentals.empty else 0
            st.metric("💰 Total Revenue", format_kes(total_revenue))
        
        st.markdown("---")
        
        # Recent rentals
        st.subheader("📊 Recent Rentals")
        if not st.session_state.rentals.empty:
            recent = st.session_state.rentals.tail(5)
            display_df = recent.copy()
            display_df['total_cost'] = display_df['total_cost'].apply(lambda x: format_kes(x))
            st.dataframe(display_df[['rental_id', 'customer_name', 'item_name', 'rental_date', 'return_date', 'status', 'total_cost']], use_container_width=True)
        
        # Inventory status
        st.subheader("📦 Current Inventory Status")
        inventory_display = st.session_state.inventory[['item_id', 'item_name', 'category', 'status', 'current_renter']].copy()
        st.dataframe(inventory_display, use_container_width=True)
    
    # Inventory Management
    elif menu == "Inventory Management":
        # Display small centered logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(logo_path, width=150)
        
        st.markdown('<h1 class="main-header">Inventory Management</h1>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Add New Item", "Edit/Delete Items", "View All Items"])
        
        with tab1:
            with st.form("add_item_form"):
                col1, col2 = st.columns(2)
                with col1:
                    item_id = st.text_input("Item ID*", placeholder="e.g., CAM001")
                    item_name = st.text_input("Item Name*", placeholder="e.g., Sony A7III")
                    category = st.selectbox("Category*", ["Camera Body", "Lens", "Lighting", "Tripod", "Audio", "Accessory", "Other"])
                    brand = st.text_input("Brand", placeholder="e.g., Sony, Canon, Nikon")
                
                with col2:
                    model = st.text_input("Model", placeholder="e.g., A7III, 24-70mm")
                    serial_number = st.text_input("Serial Number*")
                    daily_rate = st.number_input("Daily Rate (KES)*", min_value=0.0, step=500.0, value=5000.0)
                    status = st.selectbox("Status", ["Available", "Rented", "Maintenance", "Lost/Damaged"])
                
                submitted = st.form_submit_button("Add Item")
                
                if submitted:
                    if item_id and item_name and serial_number and daily_rate > 0:
                        new_item = pd.DataFrame([{
                            'item_id': item_id,
                            'item_name': item_name,
                            'category': category,
                            'brand': brand,
                            'model': model,
                            'serial_number': serial_number,
                            'daily_rate': daily_rate,
                            'status': status,
                            'current_renter': ''
                        }])
                        st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                        save_data()
                        st.success(f"✅ {item_name} added successfully!")
                    else:
                        st.error("Please fill in all required fields (*)")
        
        with tab2:
            if not st.session_state.inventory.empty:
                item_to_edit = st.selectbox("Select item to edit", st.session_state.inventory['item_name'])
                if item_to_edit:
                    item_data = st.session_state.inventory[st.session_state.inventory['item_name'] == item_to_edit].iloc[0]
                    
                    with st.form("edit_item_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_item_name = st.text_input("Item Name", value=item_data['item_name'])
                            new_category = st.selectbox("Category", ["Camera Body", "Lens", "Lighting", "Tripod", "Audio", "Accessory", "Other"], 
                                                       index=["Camera Body", "Lens", "Lighting", "Tripod", "Audio", "Accessory", "Other"].index(item_data['category']))
                            new_brand = st.text_input("Brand", value=item_data['brand'])
                        
                        with col2:
                            new_model = st.text_input("Model", value=item_data['model'])
                            new_serial = st.text_input("Serial Number", value=item_data['serial_number'])
                            new_rate = st.number_input("Daily Rate (KES)", value=float(item_data['daily_rate']), step=500.0)
                            new_status = st.selectbox("Status", ["Available", "Rented", "Maintenance", "Lost/Damaged"],
                                                     index=["Available", "Rented", "Maintenance", "Lost/Damaged"].index(item_data['status']))
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            update = st.form_submit_button("Update Item")
                        with col4:
                            delete = st.form_submit_button("Delete Item", type="secondary")
                        
                        if update:
                            st.session_state.inventory.loc[st.session_state.inventory['item_name'] == item_to_edit, 'item_name'] = new_item_name
                            st.session_state.inventory.loc[st.session_state.inventory['item_name'] == new_item_name, 'category'] = new_category
                            st.session_state.inventory.loc[st.session_state.inventory['item_name'] == new_item_name, 'brand'] = new_brand
                            st.session_state.inventory.loc[st.session_state.inventory['item_name'] == new_item_name, 'model'] = new_model
                            st.session_state.inventory.loc[st.session_state.inventory['item_name'] == new_item_name, 'serial_number'] = new_serial
                            st.session_state.inventory.loc[st.session_state.inventory['item_name'] == new_item_name, 'daily_rate'] = new_rate
                            st.session_state.inventory.loc[st.session_state.inventory['item_name'] == new_item_name, 'status'] = new_status
                            save_data()
                            st.success("✅ Item updated successfully!")
                            st.rerun()
                        
                        if delete:
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
    
    # New Rental
    elif menu == "New Rental":
        # Display small centered logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(logo_path, width=150)
        
        st.markdown('<h1 class="main-header">Create New Rental</h1>', unsafe_allow_html=True)
        
        available_items = st.session_state.inventory[st.session_state.inventory['status'] == 'Available']
        
        if available_items.empty:
            st.warning("⚠️ No items available for rent at the moment.")
        else:
            # Initialize session state for rental creation
            if 'rental_created' not in st.session_state:
                st.session_state.rental_created = False
                st.session_state.last_rental_data = None
            
            # Form for rental input
            with st.form("rental_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    customer_name = st.text_input("Customer Name*")
                    customer_email = st.text_input("Email*")
                    customer_phone = st.text_input("Phone Number*", placeholder="e.g., 0712345678")
                
                with col2:
                    selected_item = st.selectbox("Select Item to Rent*", available_items['item_name'].tolist())
                    item_details = available_items[available_items['item_name'] == selected_item].iloc[0]
                    daily_rate = item_details['daily_rate']
                    st.info(f"Daily Rate: {format_kes(daily_rate)}")
                
                col3, col4, col5 = st.columns(3)
                with col3:
                    rental_date = st.date_input("Rental Date", datetime.date.today())
                with col4:
                    return_date = st.date_input("Return Date", datetime.date.today() + timedelta(days=3))
                with col5:
                    deposit = st.number_input("Deposit Amount (KES)*", min_value=0.0, value=5000.0, step=1000.0)
                
                if rental_date and return_date:
                    days = (return_date - rental_date).days
                    if days > 0:
                        total = days * daily_rate
                        st.success(f"💰 Total Cost: {format_kes(total)} for {days} days")
                    else:
                        st.error("Return date must be after rental date!")
                
                submitted = st.form_submit_button("Create Rental")
            
            # Process form submission
            if submitted:
                if customer_name and customer_email and customer_phone and selected_item:
                    days = (return_date - rental_date).days
                    if days > 0:
                        total = days * daily_rate
                        rental_id = f"RENT{str(uuid.uuid4())[:8].upper()}"
                        
                        new_rental = pd.DataFrame([{
                            'rental_id': rental_id,
                            'customer_name': customer_name,
                            'customer_email': customer_email,
                            'customer_phone': customer_phone,
                            'item_id': item_details['item_id'],
                            'item_name': selected_item,
                            'rental_date': rental_date,
                            'return_date': return_date,
                            'total_cost': total + deposit,
                            'status': 'Active',
                            'deposit_paid': deposit,
                            'daily_rate': daily_rate
                        }])
                        
                        st.session_state.rentals = pd.concat([st.session_state.rentals, new_rental], ignore_index=True)
                        
                        # Update inventory
                        st.session_state.inventory.loc[st.session_state.inventory['item_id'] == item_details['item_id'], 'status'] = 'Rented'
                        st.session_state.inventory.loc[st.session_state.inventory['item_id'] == item_details['item_id'], 'current_renter'] = customer_name
                        
                        save_data()
                        
                        # Store rental info for download
                        st.session_state.rental_created = True
                        st.session_state.last_rental_data = new_rental.iloc[0].to_dict()
                        
                        st.rerun()
                    else:
                        st.error("Please ensure return date is after rental date!")
                else:
                    st.error("Please fill in all customer information!")
            
            # Show download button after rental is created
            if st.session_state.rental_created and st.session_state.last_rental_data:
                st.success(f"✅ Rental created successfully! Rental ID: {st.session_state.last_rental_data['rental_id']}")
                
                # Generate receipt with logo
                pdf_buffer = create_receipt_pdf(st.session_state.last_rental_data, "feruzi_logo.png")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.download_button(
                        label="📄 Download Receipt (PDF)",
                        data=pdf_buffer,
                        file_name=f"receipt_{st.session_state.last_rental_data['rental_id']}.pdf",
                        mime="application/pdf",
                        key="download_receipt"
                    ):
                        st.balloons()
                
                # Button to clear without downloading
                if st.button("Create Another Rental", key="new_rental_btn"):
                    st.session_state.rental_created = False
                    st.session_state.last_rental_data = None
                    st.rerun()
    
    # Active Rentals
    elif menu == "Active Rentals":
        # Display small centered logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(logo_path, width=150)
        
        st.markdown('<h1 class="main-header">Active Rentals</h1>', unsafe_allow_html=True)
        
        active = st.session_state.rentals[st.session_state.rentals['status'] == 'Active']
        
        if active.empty:
            st.info("No active rentals at the moment.")
        else:
            display_active = active.copy()
            display_active['total_cost'] = display_active['total_cost'].apply(lambda x: format_kes(x))
            st.dataframe(display_active[['rental_id', 'customer_name', 'item_name', 'rental_date', 'return_date', 'total_cost']], use_container_width=True)
            
            for _, rental in active.iterrows():
                with st.expander(f"Rental #{rental['rental_id']} - {rental['customer_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Item:** {rental['item_name']}")
                        st.write(f"**Rental Date:** {rental['rental_date']}")
                        st.write(f"**Return Date:** {rental['return_date']}")
                    with col2:
                        st.write(f"**Total Cost:** {format_kes(rental['total_cost'])}")
                        st.write(f"**Deposit:** {format_kes(rental['deposit_paid'])}")
                        days_left = (rental['return_date'] - datetime.date.today()).days
                        if days_left >= 0:
                            st.info(f"⏰ {days_left} days left until return")
                        else:
                            st.warning(f"⚠️ Rental is {abs(days_left)} days overdue!")
    
    # Return Item
    elif menu == "Return Item":
        # Display small centered logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(logo_path, width=150)
        
        st.markdown('<h1 class="main-header">Process Item Return</h1>', unsafe_allow_html=True)
        
        active_rentals = st.session_state.rentals[st.session_state.rentals['status'] == 'Active']
        
        if active_rentals.empty:
            st.info("No active rentals to return.")
        else:
            rental_to_return = st.selectbox("Select rental to return", 
                                           active_rentals.apply(lambda x: f"{x['rental_id']} - {x['customer_name']} - {x['item_name']}", axis=1))
            
            if rental_to_return:
                rental_id = rental_to_return.split(" - ")[0]
                rental_data = st.session_state.rentals[st.session_state.rentals['rental_id'] == rental_id].iloc[0]
                
                st.write("### Rental Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Customer:** {rental_data['customer_name']}")
                    st.write(f"**Item:** {rental_data['item_name']}")
                    st.write(f"**Rental Date:** {rental_data['rental_date']}")
                with col2:
                    st.write(f"**Return Date:** {rental_data['return_date']}")
                    st.write(f"**Deposit Paid:** {format_kes(rental_data['deposit_paid'])}")
                
                # Calculate late fees if any
                today = datetime.date.today()
                if today > rental_data['return_date']:
                    days_late = (today - rental_data['return_date']).days
                    late_fee = days_late * 500
                    st.warning(f"⚠️ Rental is {days_late} days late. Late fee: {format_kes(late_fee)}")
                else:
                    late_fee = 0
                
                col3, col4 = st.columns(2)
                with col3:
                    damage_fee = st.number_input("Damage Fee (KES)", min_value=0.0, step=500.0, value=0.0)
                with col4:
                    condition_notes = st.text_area("Condition Notes", placeholder="Any damage or issues with returned equipment?")
                
                if st.button("Process Return"):
                    # Update rental status
                    st.session_state.rentals.loc[st.session_state.rentals['rental_id'] == rental_id, 'status'] = 'Completed'
                    
                    # Update inventory
                    st.session_state.inventory.loc[st.session_state.inventory['item_id'] == rental_data['item_id'], 'status'] = 'Available'
                    st.session_state.inventory.loc[st.session_state.inventory['item_id'] == rental_data['item_id'], 'current_renter'] = ''
                    
                    # Calculate refund
                    deposit_refund = rental_data['deposit_paid'] - damage_fee - late_fee
                    
                    save_data()
                    
                    st.success("✅ Return processed successfully!")
                    
                    if deposit_refund > 0:
                        st.info(f"💰 Deposit refund amount: {format_kes(deposit_refund)}")
                    elif deposit_refund < 0:
                        st.warning(f"⚠️ Additional payment due: {format_kes(abs(deposit_refund))}")
                    
                    st.balloons()
    
    # Rental History
    elif menu == "Rental History":
        # Display small centered logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            display_centered_logo(logo_path, width=150)
        
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
            display_filtered['total_cost'] = display_filtered['total_cost'].apply(lambda x: format_kes(x))
            st.dataframe(display_filtered[['rental_id', 'customer_name', 'item_name', 'rental_date', 'return_date', 'total_cost', 'status']], use_container_width=True)
            
            # Statistics
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

if __name__ == "__main__":
    main()