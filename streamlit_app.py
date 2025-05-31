import streamlit as st
import pandas as pd

df = pd.DataFrame(columns=["Row Number", "Error Code"])

# Function to log errors
def error(code, index):
    global df
    new_row = {"Row Number": index+2, "Error Code": code}
    df.loc[len(df)] = new_row

# Process the DataFrame with the conditional function
def main(data):
    global df
    st.session_state.errors = []  # Reset errors
    for index in range(data.shape[0]):
        d = data.iloc[index].to_dict()
        try:
            conditional_func(d, index)
        except Exception as e:
            st.error(f"Error processing row {index + 2}: {str(e)}")
    return df

# File upload and dataset selection (simplified for this example)
def upload_and_select_dataframe():
    uploaded_file = st.file_uploader("Upload your file", type=['csv', 'xls', 'xlsx'])
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        else:
            return pd.read_excel(uploaded_file)
    return None

# Main app logic
data = upload_and_select_dataframe()

if data is not None:
    dict_keys = data.columns
    condition_types = ["Equals", "Not equals", "Is null", "Is not null"]

    # Initialize session state
    if 'num_rules' not in st.session_state:
        st.session_state.num_rules = 0
    if 'conditional_code' not in st.session_state:
        st.session_state.conditional_code = None

    # Define conditional_func if code exists in session state
    if st.session_state.conditional_code:
        exec(st.session_state.conditional_code, globals())

    st.subheader("Define Conditional Rules")
    if st.button("Add New Rule"):
        st.session_state.num_rules += 1

    rules = []
    for rule_idx in range(st.session_state.num_rules):
        with st.expander(f"Rule {rule_idx + 1}"):
            num_conditions_key = f'num_conditions_{rule_idx}'
            if num_conditions_key not in st.session_state:
                st.session_state[num_conditions_key] = 0
            if st.button("Add Condition", key=f"add_cond_{rule_idx}"):
                st.session_state[num_conditions_key] += 1
            conditions = []
            for cond_idx in range(st.session_state[num_conditions_key]):
                st.write(f"Condition {cond_idx + 1}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    var = st.selectbox(
                        "Variable",
                        dict_keys,
                        key=f"var_{rule_idx}_{cond_idx}"
                    )
                with col2:
                    cond_type = st.selectbox(
                        "Condition",
                        condition_types,
                        key=f"cond_type_{rule_idx}_{cond_idx}"
                    )
                with col3:
                    if cond_type in ["Equals", "Not equals"]:
                        value = st.text_input(
                            "Value",
                            key=f"value_{rule_idx}_{cond_idx}"
                        )
                    else:
                        value = None
                conditions.append((var, cond_type, value))
            error_code = st.text_input(
                "Error Code",
                key=f"error_code_{rule_idx}"
            )
            if conditions and error_code:
                rules.append({'conditions': conditions, 'error_code': error_code})

    if st.button("Generate Code"):
        if rules:
            code = ""
            for rule in rules:
                cond_strs = []
                for var, cond_type, value in rule['conditions']:
                    if cond_type == "Equals":
                        cond_strs.append(f'd["{var}"] == {value}')
                    elif cond_type == "Not equals":
                        cond_strs.append(f'd["{var}"] != {value}')
                    elif cond_type == "Is null":
                        cond_strs.append(f'pd.isna(d["{var}"])')
                    elif cond_type == "Is not null":
                        cond_strs.append(f'not pd.isna(d["{var}"])')
                if cond_strs:
                    condition = " and ".join(cond_strs)
                    code += f'    if {condition}:\n'
                    code += f'        error("{rule["error_code"]}", index)\n'
            st.session_state.conditional_code = f"""
def conditional_func(d, index):
{code}
            """
            exec(st.session_state.conditional_code, globals())
        else:
            st.warning("No rules defined.")

    # Display generated code
    if st.session_state.conditional_code:
        st.subheader("Generated Conditional Function")
        st.code(st.session_state.conditional_code)

    # Run on Data button
    if st.button("Run on Data"):
        if st.session_state.conditional_code:
            try:
                main(data)
                st.success("Execution completed successfully.")
                st.write(df)
            except Exception as e:
                st.error(f"Error during execution: {str(e)}")
        else:
            st.warning("Please generate the code first.")
else:
    st.warning("Please upload a file to proceed.")