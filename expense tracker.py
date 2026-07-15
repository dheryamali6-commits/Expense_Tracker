import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['date','category','amount','description'])

def add_expense(date,category,amount,description):
    new_expense = pd.DataFrame([[date,category,amount,description]], columns= st.session_state.expenses.columns)  
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)

def load_expenses():
    uploaded_file = st.file_uploader("choose a file",type=['csv'])
    if uploaded_file is not None:
        st.session_state.expenses = pd.read_csv(uploaded_file)

def save_expenses():
    st.session_state.expenses.to_csv('expenses.csv', index=False)
    st.success("Expenses saved successfully")

def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=16, style="B")
    
    pdf.cell(200, 10, txt="Accurate Expense Tracker Statement", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", size=11, style="B")
    pdf.cell(35, 10, "Date", border=1)
    pdf.cell(35, 10, "Category", border=1)
    pdf.cell(30, 10, "Amount", border=1)
    pdf.cell(90, 10, "Description", border=1)
    pdf.ln()
    
    pdf.set_font("Helvetica", size=10)
    for index, row in df.iterrows():
        pdf.cell(35, 8, str(row['date']), border=1)
        pdf.cell(35, 8, str(row['category']), border=1)
        pdf.cell(30, 8, f"${float(row['amount']):.2f}", border=1)
        pdf.cell(90, 8, str(row['description']), border=1)
        pdf.ln()
        
    pdf.ln(5)
    pdf.set_font("Helvetica", size=12, style="B")
    pdf.cell(200, 10, txt=f"Total Documented Outflow: ${df['amount'].sum():,.2f}", ln=True, align="R")
    return pdf.output()    

def Visualize_Expenses(dataframe_to_plot):
    if not dataframe_to_plot.empty and dataframe_to_plot['amount'].sum() > 0:
        total_spent = dataframe_to_plot['amount'].sum()
        highest_category = dataframe_to_plot.groupby('category')['amount'].sum().idxmax()

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="💰 Total Expenses", value=f"${total_spent:,.2f}")
        with col2:
            st.metric(label="🔥 Higehst Spending Category", value=highest_category.title())

        st.markdown("---")

        chart_data = dataframe_to_plot.groupby('category', as_index=False)['amount'].sum()
        col_graph1, col_graph2 = st.columns(2)
        with col_graph1:
            st.subheader("📊 Spending by Category (Bar)")
            st.bar_chart(data=chart_data, x='category', y='amount', color='#29b5e8', use_container_width=True)

        with col_graph2:
            st.subheader("🍩 Distribution Percentage (donut)")
            fig = px.pie(chart_data, values='amount', names='category', hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Plotly3)
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
    # else:
    #     st.warning("No Expenses to Visualize! Make Sure you have entered amounts greater than 0.")
        st.subheader("📊 Spending Breakdown by Category")
        st.bar_chart(
            data=chart_data,
            x='category',
            y='amount',
            color='#29b5e8',
            use_container_width=True
        )    
        # fig , ax = plt.subplots()
        # sns.barplot(data=st.session_state.expenses, x='category', y='amount', ax=ax)
        # plt.xticks(rotation=45)
        # st.pyplot(fig)
    else:
        st.warning("No Expenses to Visualize! Make Sure you have entered amounts greater than 0.")    
    # else:
    # st.warning("No Expenses to Visualize!")


st.title("Accurate Expense Tracker")
with st.sidebar:
    st.header('Add Expense')
    date = st.date_input("Date")
    category = st.selectbox('Category',['Food','Transport','Entertainment','Utilities','Other'])
    amount = st.number_input('Amount', min_value=0.0, format="%.2f")
    description = st.text_input("Description")
    if st.button('Add'):
        add_expense(date,category,amount,description)
        st.success('Expense Added')
    st.markdown("---")     
    st.header("🎯 Budget Settings")
    budget = st.number_input("Monthly Budget ($)",min_value=0.0, value=2000.0, step=100.0)

if not st.session_state.expenses.empty:
    total_spent = st.session_state.expenses['amount'].sum()
    budget_percentage = min(total_spent / budget, 1.0) if budget > 0 else 0.0

    st.subheader("🎯Monthly Budget Progress")
    st.progress(budget_percentage)

    if total_spent > budget:
        st.error(f"🚨 Warning: you have exceeded your budget by ${total_spent - budget:,.2f}!")
    elif budget_percentage >= 0.8:
        st.warning(f"⚠️ Watch Out! you have use {budget_percentage*100:.1f}% of your budget.")
    else:
        st.info(f"👍🏻 Safe Zone! you have ${budget - total_spent:,.2f} remaining out of your ${budget:,.2f} budget.")

st.markdown("---")  
st.header('File Operations')
if st.button('Save expenses'):
        save_expenses()
if st.button('Load expenses'):
        load_expenses()

st.markdown("---")
st.header('Expenses')

if not st.session_state.expenses.empty:
    min_date = min(st.session_state.expenses['date'])
    max_date = max(st.session_state.expenses['date'])
    date_range = st.date_input(
        "select Date Range to Filter Logs & Charts:",
        value =(min_date, max_date),
        min_value=min_date,
        max_value= max_date
    )

    if isinstance(date_range , tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = st.session_state.expenses[
            (st.session_state.expenses['date'] >= start_date) &
            (st.session_state.expenses['date'] <= end_date)

        ]
    else:
        filtered_df = st.session_state.expenses    



if not st.session_state.expenses.empty:
    st.markdown("💡 *Double-cilck cells to edit. select a row row indicator and press 'Delete' on your keyboard to remove it.*")
    edited_df = st.data_editor(st.session_state.expenses, num_rows="dynamic", use_container_width=True)
    if not edited_df.equals(filtered_df):
        st.session_state.expenses = edited_df
        st.rerun()

    st.markdown("### 📥 Export Records")
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Expense Report')
        st.download_button(
            label="📊 Download as Excel (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name="expense_statement.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_dl2:
        try:
            pdf_bytes = generate_pdf(filtered_df)
            st.download_button(
                label="📄 Download as PDF Report (.pdf)",
                data=bytes(pdf_bytes),
                file_name="expense_statement.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error("Could not render PDF template.")    

    st.markdown("### 📥 Export Records")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Expense Report')

    st.download_button(
        label="📥 Download current filtered list as excel (.xlsx)",
        data=buffer.getvalue(),
        file_name="expense_statement.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )        
else:
  filtered_df = st.session_state.expenses
  st.write(st.session_state.expenses)

st.markdown("---")
st.header('Visualization')
if st.button('Visualize Expenses'):
    Visualize_Expenses(filtered_df)
