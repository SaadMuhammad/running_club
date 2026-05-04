from pathlib import Path

import pandas as pd
import streamlit as st

from funcs.helpers import (
    init_app_state,
    get_runs_df,
    set_runs_df,
    save_data,
    load_data,
    clean_runs_df,
    add_manual_entry,
    REQUIRED_COLUMNS,
    check_app_password,
)
from funcs.styles import inject_global_css, highlight_box

init_app_state()
check_app_password()
df = get_runs_df()

inject_global_css()

st.markdown(
    '<h1 style="font-size:2rem; font-weight:800;">\U0001f510 Admin</h1>',
    unsafe_allow_html=True,
)
st.caption("Manage CSV path, upload data, add entries, and maintain records.")

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "changeme")

if not st.session_state["admin_ok"]:
    password = st.text_input("Enter admin password", type="password")
    if st.button("Unlock Admin"):
        if password == ADMIN_PASSWORD:
            st.session_state["admin_ok"] = True
            st.success("Admin unlocked.")
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

st.markdown(highlight_box("Admin access granted."), unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    ["CSV Path", "Upload CSV", "Add Entry", "Preview / Export"]
)

with tab1:
    st.subheader("CSV Path")
    current_path = st.session_state["data_path"]

    new_path = st.text_input(
        "Path to CSV file",
        value=current_path,
        help="Example: assets/running.csv",
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Use this path"):
            st.session_state["data_path"] = new_path.strip()
            st.session_state["runs_df"] = load_data(st.session_state["data_path"])
            st.success(f"Now using: {st.session_state['data_path']}")
            st.rerun()

    with c2:
        if st.button("Create empty CSV at this path"):
            path = Path(new_path.strip())
            path.parent.mkdir(parents=True, exist_ok=True)
            empty_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
            empty_df.to_csv(path, index=False)

            st.session_state["data_path"] = new_path.strip()
            st.session_state["runs_df"] = load_data(st.session_state["data_path"])
            st.success(f"Created empty CSV at: {st.session_state['data_path']}")
            st.rerun()

with tab2:
    st.subheader("Upload / Replace CSV")
    st.caption("Required columns: runner_name, date, distance_km, run_type, notes")

    uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)

            for col in REQUIRED_COLUMNS:
                if col not in uploaded_df.columns:
                    uploaded_df[col] = None

            uploaded_df = uploaded_df[REQUIRED_COLUMNS]
            cleaned_df = clean_runs_df(uploaded_df)

            st.dataframe(cleaned_df.head(20), use_container_width=True, hide_index=True)

            if st.button("Save uploaded CSV to current path"):
                set_runs_df(cleaned_df)
                save_data(cleaned_df, st.session_state["data_path"])
                st.success(f"Saved to {st.session_state['data_path']}")
                st.rerun()

        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")

with tab3:
    st.subheader("Add Manual Entry")

    with st.form("manual_entry_form"):
        runner_name = st.text_input("Runner name")
        run_date = st.date_input("Date")
        distance_km = st.number_input("Distance (km)", min_value=0.0, value=5.0, step=0.1)
        run_type = st.selectbox(
            "Run type",
            ["Easy Run", "Long Run", "Interval", "Race", "Recovery Run", "Other"],
        )
        notes = st.text_input("Notes")

        submitted = st.form_submit_button("Add entry")

        if submitted:
            if not runner_name.strip():
                st.error("Runner name is required.")
            else:
                updated_df = add_manual_entry(
                    df=df,
                    runner_name=runner_name,
                    run_date=run_date,
                    distance_km=distance_km,
                    run_type=run_type,
                    notes=notes,
                )
                set_runs_df(updated_df)
                save_data(updated_df, st.session_state["data_path"])
                st.success("Entry added and saved.")
                st.rerun()

with tab4:
    st.subheader("Current Data")
    st.write(f"Current CSV path: `{st.session_state['data_path']}`")
    st.dataframe(df, use_container_width=True, hide_index=True)

    export_df = df.copy()
    if not export_df.empty and "date" in export_df.columns:
        export_df["date"] = pd.to_datetime(export_df["date"]).dt.strftime("%Y-%m-%d")

    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download current CSV",
        data=csv_bytes,
        file_name="running_export.csv",
        mime="text/csv",
    )

    if st.button("Reload from current CSV path"):
        st.session_state["runs_df"] = load_data(st.session_state["data_path"])
        st.success("Reloaded from file.")
        st.rerun()
