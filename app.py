import streamlit as st
from descope.descope_client import DescopeClient
from descope.exceptions import AuthException

DESCOPE_PROJECT_ID = str(st.secrets.get("DESCOPE_PROJECT_ID"))
descope_client = DescopeClient(project_id=DESCOPE_PROJECT_ID)


if "token" not in st.session_state:
    if "code" in st.query_params:
        code = st.query_params["code"]
        st.query_params.clear()
        try:
            # Exchange code
            with st.spinner("Loading..."):
                jwt_response = descope_client.sso.exchange_token(code)
            st.write("SSO Exchange successful")
            st.session_state["token"] = jwt_response["sessionToken"].get("jwt")
            st.session_state["user"] = jwt_response["user"]
            st.rerun()
        except AuthException:
            st.error("Login failed!")
    st.warning("You're not logged in, pls login")
    with st.container(border=True):
        with st.form(key="sso_form", clear_on_submit=True, border=False):
            email = st.text_input("Email address", placeholder="john@doe.com")
            sso_button = st.form_submit_button(
                "Sign in with SSO", use_container_width=True
            )
            st.write(
                '<p style="text-align:center">------- OR -------</p>',
                unsafe_allow_html=True,
            )
        if st.button("Sign In with Google", use_container_width=True):
            oauth_response = descope_client.oauth.start(
                provider="google", return_url="http://localhost:8501"
            )
            url = oauth_response["url"]
            # Redirect to Google
            st.markdown(
                f'<meta http-equiv="refresh" content="0; url={url}">',
                unsafe_allow_html=True,
            )
else:
    try:
        with st.spinner("Loading..."):
            descope_client.validate_session(st.session_state.token)
        st.title("Demo App")
        st.write("This is a demo app with Descope-powered authentication and SSO")
        st.subheader("Welcome! you're logged in")
        if "user" in st.session_state:
            user = st.session_state.user
            st.write("Name: " + user["name"])
            st.write("email: " + user["email"])
        if st.button("Logout"):
            del st.session_state.token
            st.rerun()
    except AuthException:
        del st.session_state.token
        st.rerun()
