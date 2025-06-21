import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("🍹 Build Your Smoothie")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
order_filled = st.checkbox("Is the order filled?")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit data
try:
    fruit_df = session.table("smoothies.public.fruit_options").select(
        col("FRUIT_NAME"), col("SEARCH_ON")
    ).to_pandas()

    st.dataframe(fruit_df)  # show available fruits

    options = fruit_df["FRUIT_NAME"].tolist()
    ingredients_list = st.multiselect("Choose up to 5 fruits:", options, max_selections=5)

    if ingredients_list and name_on_order:
        ingredients_string = ','.join(ingredients_list)

        # Insert to Snowflake
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders("INGREDIENTS", "NAME_ON_ORDER", "ORDER_FILLED", "ORDER_TS")
            VALUES ('{ingredients_string}', '{name_on_order}', {str(order_filled).upper()}, CURRENT_TIMESTAMP)
        """
        st.write(insert_stmt)

        if st.button("Submit Order"):
            session.sql(insert_stmt).collect()
            st.success("Order placed successfully!")

        # Show nutrition info
        for fruit in ingredients_list:
            search_on = fruit_df.loc[fruit_df["FRUIT_NAME"] == fruit, "SEARCH_ON"].iloc[0]
            st.subheader(f"{fruit} Nutrition")
            response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            st.dataframe(response.json(), use_container_width=True)

except Exception as e:
    st.error(f"Error loading fruits or connecting to Snowflake: {e}")
