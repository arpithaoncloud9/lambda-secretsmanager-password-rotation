# Serverless Password Rotation System Using AWS Lambda & Secrets Manager

## STEP 1 — Create a Secret in Secrets Manager

##### This step sets up the **password** that your Lambda function will rotate later. You’re basically creating the “starting point” for your rotation system.
### **1.1 Open AWS Secrets Manager**

- Go to the AWS Console
- Search for **Secrets Manager**
- Open it
### **1.2 Click “Store a new secret”**

This starts the secret creation wizard.
### **1.3 Choose “Other type of secret”**

You’re not storing RDS credentials — just a simple key/value pair.
### **1.4 Add the key/value pair**

In the key/value section:

- **Key:** `password`
- **Value:** `Admin@1234`

This is your initial password. Lambda will replace it later.
### **1.5 Encryption**

Leave the default:

- **aws/secretsmanager** (default AWS-managed KMS key)

This is perfect for a beginner project.
### **1.6 Name your secret**

Use:

**MyApp/DB-Password**

This is clean, structured, and easy to reference in Lambda.
### **1.7 Save**

Click **Next → Next → Store** Your secret is now created.

<img width="928" height="239" alt="Screenshot 2026-01-21 at 8 01 39 PM" src="https://github.com/user-attachments/assets/a1504078-8bf0-4553-aa6f-282cfa768edc" />


## STEP 2 — Create the Lambda Function
##### This Lambda will be responsible for:
- Reading the current password from Secrets Manager
- Generating a new password
- Updating the secret with the new value
### **2.1 Go to AWS Console**

- Search for **Lambda**
- Click **Create function**
### **2.2 Choose “Author from scratch”**

Fill in the details:

- **Function name:** `RotatePasswordFunction`
- **Runtime:** Python (recent version)
- **Architecture:** x86_64
- **Permissions:** Leave default (we’ll modify later)

Click **Create function**.
### **2.3 Leave the default code for now**

We will replace it in the next step.
### **2.4 Confirm the function is created**

You should now see:
- Function name at the top
- Code editor
- Configuration tabs

## STEP 3 — Add IAM Permissions to Lambda

##### Your Lambda needs permission to:
- **Read** the current secret
- **Update** the secret with a new password
- **Decrypt** the secret using KMS

Without these, the rotation will fail.
### **3.1 Go to IAM → Roles**

- In the AWS Console, search for **IAM**
- Click **Roles**
    
- Find the role created for your Lambda
    
    - It will look like: **RotatePasswordFunction-role-xxxx**

Click it.
### **3.2 Click “Add permissions” → “Attach policies”**
 
 1. **Add Secrets Manager permissions**

- Go to IAM → Roles
- Search for the role created for your Lambda: `RotatePasswordFunction-role-xxxx`
    - Open it and search for  
- SecretsManagerReadWrite
- Check the box next to “SecretsManagerReadWrite"
- click the button "Add permissions"

The policy is now attached to your Lambda execution role

2. **Add KMS decrypt permission**
- Go to IAM → Roles
- Search for the role created for your Lambda: `RotatePasswordFunction-role-xxxx` 
    - Scroll to the “Permissions” tab
    - Click “Add permissions” → “Create inline policy”

Choose the JSON tab and paste this 

json

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "*"
    }
  ]
}
```
Click “Next” → Name the policy as "**KMSDecryptForRotation**" and save.

### **3.3. Confirm the role now has:**

- Secrets Manager read/write
- KMS decrypt
- Basic Lambda execution permissions

<img width="901" height="303" alt="Screenshot 2026-01-21 at 7 45 22 PM" src="https://github.com/user-attachments/assets/e377f8d3-6efd-4e93-bcb0-f5a7a87e607e" />


## STEP 4 — Add the Rotation Code to Lambda
##### This step gives your Lambda the actual logic to:
- Connects to AWS Secrets Manager
- Fetch the current password
- Generate a new random password
- Update the secret in Secrets Manager
### 4.1 Go to your Lambda function
- Go to **Lambda**
- Select your function: **RotatePasswordFunction**
### 4.2 **Scroll to the Code section and Replace the default code with this:**
```python
import boto3
import string
import random

secrets_client = boto3.client('secretsmanager')

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def lambda_handler(event, context):
    secret_name = "MyApp/DBPassword"

    # Get current secret value
    current_secret = secrets_client.get_secret_value(SecretId=secret_name)
    
    # Generate new password
    new_password = generate_password()

    # Update the secret with new password
    secrets_client.put_secret_value(
        SecretId=secret_name,
        SecretString=f'{{"password": "{new_password}"}}'
    )

    return {
        "status": "success",
        "new_password": new_password
    }
```
### **4.3 Click “Deploy”**
- Your Lambda is now ready to rotate the password.

## STEP 5 — Test the Lambda Function Manually

##### This step verifies that your Lambda can:
- Read the existing secret
- Generate a new password
- Update the secret in Secrets Manager

You’ll run it manually once to confirm everything works.
### **5.1 Open your Lambda function**  
- Go to: **Lambda → RotatePasswordFunction**
- Click the “Test” tab
### 5.2 **Create a new test event**
- Click **Create new event**
- Event name: `TestRotation`
- Leave the JSON as default:
```code
{}
```
- Save
### **5.3 Click “Test”**
- Lambda will run immediately.
##### **If everything is correct:**
- Execution status: **Succeeded**
- In the output, you’ll see something like:
```code
{
  "status": "success",
  "new_password": "A1b2C3!..."
}
```
<img width="1204" height="524" alt="Screenshot 2026-01-21 at 8 17 01 PM" src="https://github.com/user-attachments/assets/92eebdd7-f0a3-4b93-967e-1fd80921c9c8" />


##### **Now verify the secret actually changed:**
- Go to **Secrets Manager**
- Open **MyApp/DBPassword**
- Click **Retrieve secret value**
- You should see a **new password** instead of `InitialPass123!`

That confirms your rotation logic works end‑to‑end.

<img width="1200" height="649" alt="Screenshot 2026-01-21 at 8 18 27 PM" src="https://github.com/user-attachments/assets/639d71fc-2866-44b1-ba60-fe011783cffd" />


## STEP 6 — Trigger Rotation Automatically
##### Right now, your Lambda rotates the password **only when you manually run it**. If you want the system to rotate passwords automatically (for example, every 30 days), you can add an EventBridge rule.
### 6.1 Add an Automatic Trigger
- Go to Amazon **EventBridge** and select **EventBridge Schedule**
- click **Create Schedule**
- Specify schedule detail
    - **Name:** `RotatePasswordSchedule` 
    - **Schedule pattern:** Recurring schedule
    -  **Schedule type**:Cron-based schedule
- Cron expression
    Examples:
    - Rotate every day at midnight `0 0 * * ? *`
    - Rotate every 30 days (recommended for demo) `0 0 1 * ? *`
    - But for simplicity, **just use** `cron(0/5 * * * ? *)` for now (Rotates every 5 minutes)
- Set **flexible time window** to 5 min ( It lets AWS **delay the execution** of your scheduled task by a few minutes — intentionally. If your cron is set to run at **8:00 PM**, and you choose a **5-minute window**, AWS may run it **anytime between 8:00 PM and 8:05 PM**. This helps AWS balance load across millions of schedules )
- Click **Next**
### **6.2. Choose the target**
- Target type: **Lambda function**
- Function: **RotatePasswordFunction**
### **6.3 Create a Schedule
- Now your Lambda will run automatically based on the schedule you set

<img width="1180" height="264" alt="Screenshot 2026-01-21 at 8 59 59 PM" src="https://github.com/user-attachments/assets/b437add2-32cf-49b7-a78d-c7f7aa204e3b" />

<img width="1197" height="259" alt="Screenshot 2026-01-21 at 9 03 06 PM" src="https://github.com/user-attachments/assets/1a392cd1-044e-4d4d-90a9-e12bba7a180b" />

<img width="2322" height="468" alt="image" src="https://github.com/user-attachments/assets/663718d8-9610-429e-9253-536909c1a4b0" />


## Outcome: 
- Built an automated password‑rotation system using AWS Secrets Manager, Lambda, and EventBridge.
- Wrote a Python Lambda function to generate and update secrets securely.
- Applied least‑privilege IAM permissions, including SecretsManagerReadWrite and kms:Decrypt.
- Scheduled automatic rotations using cron rules and validated end‑to‑end execution.
- Strengthened skills in serverless automation, KMS encryption, and cloud troubleshooting.
