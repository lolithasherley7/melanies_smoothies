import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Title and instructions
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on the Smoothie will be: {name_on_order}")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# Show fruit list (optional)
st.dataframe(pd_df)

# Fruit selection
options = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect("Choose up to 5 ingredients:", options, max_selections=5)

if ingredients_list and name_on_order:
    st.write("Selected fruits:", ingredients_list)

    # Create string for database
    ingredients_string = ','.join(ingredients_list)

    # SQL insert
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders("INGREDIENTS", "NAME_ON_ORDER", "ORDER_FILLED", "ORDER_TS") 
        VALUES ('{ingredients_string}', '{name_on_order}', FALSE, CURRENT_TIMESTAMP)
    """
    st.write(my_insert_stmt)

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

    # ✅ Exactly like the screenshot: now use SEARCH_ON
    ingredients_string = ''  # Optional: collecting again if needed

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the search_on value from dataframe
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Optional debug info
        # st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # Show subheader and nutrition data from API
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)

        try:
            fv_df = fruityvice_response.json()
            st.dataframe(fv_df, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load nutrition data for {fruit_chosen}: {e}")
