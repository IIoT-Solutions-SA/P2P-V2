import SuperTokens from "supertokens-auth-react";
import EmailPassword from "supertokens-auth-react/recipe/emailpassword";
import Session from "supertokens-auth-react/recipe/session";
import { API_BASE_URL, WEBSITE_BASE_URL } from './environment';

SuperTokens.init({
    appInfo: {
        appName: "P2P Sandbox for SMEs",
        apiDomain: API_BASE_URL,
        websiteDomain: WEBSITE_BASE_URL,
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
