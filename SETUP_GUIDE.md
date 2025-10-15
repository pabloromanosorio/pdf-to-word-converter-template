# Setup Guide: Deploying Your Personal PDF-to-DOCX Converter

Welcome! This guide will walk you through every step of deploying your own private version of the AI-powered PDF-to-DOCX converter. No prior coding experience is required. We will go step-by-step.

## Part 1: Google Cloud First Steps

**Objective:** To create a private, secure space on Google Cloud where your application will live.

Think of Google Cloud as renting a very powerful, secure computer that you can access from anywhere. We need to set up your account and create a private room (a "Project") for our app.

1.  **Create a Google Cloud Account:**
    *   Go to the [Google Cloud website](https://cloud.google.com/).
    *   Click "Get started for free".
    *   Sign in with your existing Google account or create a new one.
    *   You will need to provide a form of payment. **This is for identity verification and to prevent abuse.** Google provides a generous free tier, and the cost of running this application for personal use will be very low (likely less than a cup of coffee per month, if anything at all).

2.  **Create a New Project:**
    *   Once you are in the Google Cloud Console, find the project selector at the top of the page. It might show a name like "My First Project".
    *   Click on it, and then click **"New Project"**.
    *   Give your project a memorable name, like `my-pdf-converter-app`.
    *   Click **"Create"**.

3.  **Confirm Your Project ID:**
    *   Make sure your new project is selected in the top dropdown.
    *   Click the project name again, and you will see a dashboard. Find the **"Project info"** card. 
    *   Write down the **Project ID** (it might be different from the name you gave it). You will need this in Part 3.

## Part 2: Preparing Your Computer

**Objective:** To install the tools needed to communicate with your new Google Cloud account.

We need to install a special command-line tool called the Google Cloud SDK (or `gcloud`). This lets you send commands from your computer directly to your Google Cloud project.

1.  **Install the Google Cloud SDK:**
    *   Go to the official installation page: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
    *   Follow the instructions for your operating system (Windows, macOS, or Linux).

2.  **Connect Your Computer to Your Google Account:**
    *   Open a new terminal or command prompt.
    *   Run the following command. It will open a web browser and ask you to log in to your Google account.
        ```bash
        gcloud auth login
        ```
    *   Next, run this second command. This allows applications on your computer (like the Gemini CLI we will use) to use your credentials securely.
        ```bash
        gcloud auth application-default login
        ```

## Part 3: Deploying the App with the Gemini CLI

**Objective:** To install the application into your Google Cloud project.

We will use the Gemini CLI inside the Cursor code editor to perform the deployment. You will not need to write any code; you will only give the AI instructions.

1.  **Download the Application Template:**
    *   Go to the GitHub repository for this project.
    *   Click the green "Code" button and select "Download ZIP".
    *   Unzip the downloaded file on your computer.

2.  **Open the Project in Cursor:**
    *   Open the Cursor application.
    *   Go to "File" > "Open Folder..." and select the unzipped application folder (e.g., `pdf-converter-template-main`).

3.  **Deploy with a Prompt:**
    *   Open a new chat with Gemini (@Gemini).
    *   Copy and paste the following prompt into the chat. **Crucially, replace `[your-project-id-here]` with the Project ID you saved in Part 1.**

    > I have downloaded this application template and I want to deploy it to Google Cloud Run. My Project ID is `[your-project-id-here]` and I want to deploy to the `us-central1` region. Please enable the necessary APIs, deploy the service, and set the correct permissions for it to work.

4.  **Approve the Steps:**
    *   Gemini will show you the commands it plans to run. They will look like `gcloud services enable...`, `gcloud run deploy...`, etc.
    *   Approve each step. The deployment process may take a few minutes as Google Cloud builds and activates your application.

5.  **Success!**
    *   Once complete, Gemini will provide you with the URL for your live application.
    *   Congratulations! You now have your own private, AI-powered document conversion tool.

## Part 4: Common Issues (Troubleshooting)

If you run into an error, don't worry! Here are some of the most common issues and how to solve them.

### Issue: `gcloud: command not found`

*   **What it means:** Your computer can't find the Google Cloud SDK command.
*   **How to fix:**
    1.  Make sure you have fully completed the installation from Part 2.
    2.  The most common fix: **Close and re-open your terminal or Cursor application.** The installer often needs a restart to finalize the setup.
    3.  If it still doesn't work, try running the installer again.

### Issue: The command fails with a "Permission Denied" or "403" error

*   **What it means:** Google Cloud doesn't think you have the authority to perform the action. This is usually a stale login.
*   **How to fix:**
    1.  Run the authentication commands from Part 2 again to refresh your credentials:
        ```bash
        gcloud auth login
        ```
    2.  And then:
        ```bash
        gcloud auth application-default login
        ```

### Issue: The deployment fails with a "Billing" error

*   **What it means:** Your Google Cloud project is not linked to an active billing account. While you get a large free tier, a billing account is required to use most services.
*   **How to fix:**
    1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
    2.  In the navigation menu (☰), find **"Billing"**.
    3.  Follow the instructions to either link your project to your existing billing account or to create a new one.