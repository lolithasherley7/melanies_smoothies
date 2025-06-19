import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw: ")
st.write("Choose the fruits you want in your custom Smoothie")

name_on_order = st.text_input("Name on Smoothie: ")
st.write("The name on the Smoothie will be : ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Select both FRUIT_NAME and SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Show dataframe without stopping
st.dataframe(pd_df)

# Create mapping display_name -> FRUIT_NAME
display_to_fruit = {f"{row.FRUIT_NAME} ({row.SEARCH_ON})": row.FRUIT_NAME for row in pd_df.itertuples()}

options = list(display_to_fruit.keys())

# Use options with "FRUIT_NAME (SEARCH_ON)" format
ingredients_list_display = st.multiselect(
    "Choose up to 5 ingredients:",
    options,
    max_selections=5
)

# Convert back to fruit names for processing
ingredients_list = [display_to_fruit[disp_name] for disp_name in ingredients_list_display]

if ingredients_list and name_on_order:
    st.write("Selected fruits:", ingredients_list)
    
    ingredients_string = ' '.join(ingredients_list)
    
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write(f"The search value for {fruit_chosen} is {search_on}.")
        
        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(),use_container_width =True)
        
        # Fix the API url - assuming fruit_chosen should be appended, no "watermelon" prefix
        url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower().replace(' ', '')}"
        smoothiefroot_response = requests.get(url)
        if smoothiefroot_response.ok:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.write(f"Could not fetch nutrition info for {fruit_chosen}")

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders("INGREDIENTS", "NAME_ON_ORDER") 
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
