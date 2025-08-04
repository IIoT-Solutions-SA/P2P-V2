import SuperTokens from "supertokens-auth-react";
import EmailPassword from "supertokens-auth-react/recipe/emailpassword";
import Session from "supertokens-auth-react/recipe/session";

SuperTokens.init({
    appInfo: {
        // These match the backend configuration
        appName: "P2P Sandbox for SMEs",
        apiDomain: "http://localhost:8000",
        websiteDomain: "http://localhost:3000",
        apiBasePath: "/auth",
        websiteBasePath: "/auth"
    },
    recipeList: [
        EmailPassword.init({
            signInAndUpFeature: {
                signUpForm: {
                    formFields: [
                        {
                            id: "email",
                            label: "Email",
                            placeholder: "Enter your email"
                        },
                        {
                            id: "password", 
                            label: "Password",
                            placeholder: "Enter your password"
                        },
                        {
                            id: "firstName",
                            label: "First Name",
                            placeholder: "Enter your first name"
                        },
                        {
                            id: "lastName",
                            label: "Last Name", 
                            placeholder: "Enter your last name"
                        }
                    ]
                }
            }
        }),
        Session.init()
    ]
});
