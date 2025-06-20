import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on the Smoothie will be: {name_on_order}")

cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Show the fruit table (optional)
st.dataframe(pd_df)

# Multiselect shows user-friendly FRUIT_NAME
options = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect("Choose up to 5 ingredients:", options, max_selections=5)

if ingredients_list and name_on_order:
    st.write("Selected fruits:", ingredients_list)

    # Join ingredients with comma + space to match expected format exactly
    ingredients_string = ', '.join(ingredients_list)

    # Optional: show SQL statement for debugging
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders("INGREDIENTS", "NAME_ON_ORDER", "ORDER_FILLED", "ORDER_TS") 
        VALUES ('{ingredients_string}', '{name_on_order}', FALSE, CURRENT_TIMESTAMP)
    """
    st.write(my_insert_stmt)

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
