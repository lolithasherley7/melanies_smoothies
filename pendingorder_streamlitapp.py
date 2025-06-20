import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col, when_matched

# UI Title
st.title(":cup_with_straw: Pending Smoothie Orders! :cup_with_straw:")
st.write("Orders that need to be filled.")

# Connect to Snowflake session
cnx=st.connection("snowflake")
session = cnx.session()

# Query unfilled orders including ORDER_ID
my_dataframe = (
    session.table("smoothies.public.orders")
    .filter(col("ORDER_FILLED") == False)
    .select("ORDER_UID", "INGREDIENTS", "NAME_ON_ORDER", "ORDER_FILLED")
    .collect()
)

if my_dataframe:
     # Convert Snowflake Rows to list of dicts
    data_dicts = [row.as_dict() for row in my_dataframe]

    # Convert to pandas DataFrame
    my_dataframe = pd.DataFrame(data_dicts)

    # Show editable data editor with the dataframe
    editable_df = st.data_editor(my_dataframe)
    # Submit button with correct emoji character (not shortcode)
    submitted = st.button("Submit")

    if submitted:
        
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)

        try:
             og_dataset.merge(edited_dataset
                     , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                     , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                    ) 
             st.success("Order(s) Updated!", icon="👍")

        except Exception as e:
             st.error(f"Something went wrong: {e}")
             st.text(traceback.format_exc())

else:
    st.success("There are no pending orders right now.", icon="👍")

# Show total pending orders
st.info(f"Total Pending Orders: {len(my_dataframe) if isinstance(my_dataframe, pd.DataFrame) else 0}")
   



    
   
        
    

  


