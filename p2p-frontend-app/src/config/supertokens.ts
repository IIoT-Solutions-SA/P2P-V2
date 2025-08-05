import SuperTokens from "supertokens-auth-react";
import EmailPassword from "supertokens-auth-react/recipe/emailpassword";
import Session from "supertokens-auth-react/recipe/session";

SuperTokens.init({
    appInfo: {
        appName: "P2P Sandbox for SMEs",
        apiDomain: "http://localhost:8000",
        websiteDomain: "http://localhost:5173",
        apiBasePath: "/api/v1/auth",
        websiteBasePath: "/auth"
    },
    recipeList: [
        EmailPassword.init({
            signInAndUpFeature: {
                signUpForm: {
                    formFields: [
                        {
                            id: "name",
                            label: "Full Name",
                            placeholder: "Enter your full name"
                        }
                    ]
                }
            }
        }),
        Session.init()
    ]
});
