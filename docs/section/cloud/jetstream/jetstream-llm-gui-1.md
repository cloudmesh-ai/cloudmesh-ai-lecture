
# Jetstream Cloud LLM in Visual Studio Code – GUI‑only setup  
*(no terminal commands, no JSON‑editing by hand)*  

The instructions below walk you through every click you need to make inside VS Code (or a standalone REST client) so that the Jetstream model can be used from the **graphical** interface.  
All numeric values are plain numbers (e.g. `120`, `0.7`) – you never have to type scientific notation.

---

## 1. Get the Jetstream API key  

1. Open a web browser and go to **https://jetstream-cloud.org**.  
2. Sign in (or create a free account).  
3. In the dashboard click **User → API Keys**.  
4. Press **Create New Key**, give the key a name (e.g. “VS Code”) and click **Create**.  
5. A string that starts with `jsc-` is shown. Click **Copy** – you will paste this value later.  

*Keep the key secret; treat it like a password.*

---

## 2. Choose how you want to chat inside VS Code  

There are two built‑in options:

| Option | When to use it | How to enable |
|--------|----------------|---------------|
| **AI Assistant (native to VS Code ≥ 1.87)** | You have the latest VS Code and prefer a *no‑extension* solution. | Enable in Settings → “AI Assistant: Enabled”. |
| **ChatGPT – EasyCode (or another OpenAI‑compatible extension)** | You already use an extension for code‑completion or want extra features (e.g. “Insert at cursor”). | Install from the Extensions view. |

Both approaches are configured through the **Settings UI**, not by editing JSON files.

### 2.1 Enable the native AI Assistant (recommended for newer VS Code)

1. Open **Settings** – press `Ctrl+,` (or choose *File → Preferences → Settings*).  
2. In the search bar type **“AI Assistant”**.  
3. Tick the checkbox **AI Assistant: Enabled**.  

   You will now see a new group of settings titled **AI Assistant**.

### 2.2 Install a third‑party chat extension  

1. Open the **Extensions** view – press `Ctrl+Shift+X`.  
2. In the search box type **“ChatGPT – EasyCode”** (or any extension that mentions “OpenAI compatible”).  
3. Click **Install** on the matching entry.  
4. After installation a chat‑icon appears in the Activity Bar on the left.

---

## 3. Configure the connection – all via the Settings UI  

Below the steps are identical for the native AI Assistant and for the EasyCode extension; the UI names differ only slightly.

### 3.1 Set the API base URL  

1. In Settings, keep the search bar focused and type **“API Base”**.  
2. You will see a field named one of the following:  

   * **AI Assistant: API Base**  (native)  
   * **ChatGPT: API Base**      (extension)  

3. Click the **Edit** (pencil) button that appears at the right of the field.  
4. Type the exact URL:  

   ```
   https://llm.jetstream-cloud.org/v1
   ```

5. Press **Enter** to confirm.

### 3.2 Enter the API key  

1. In Settings search for **“API Key”**.  
2. Choose the field that matches the component you are configuring (AI Assistant → API Key, or ChatGPT → API Key).  
3. Click **Edit** and paste the key you copied from the Jetstream dashboard.  

   *If you prefer not to store the key directly, you can use an environment variable.*  
   In that case type the placeholder  

   ```
   ${env:JETSTREAM_API_KEY}
   ```

   (Make sure the variable `JETSTREAM_API_KEY` is defined in your system environment.)

### 3.3 Choose the model  

1. Search for **“Model”**.  
2. Click **Edit** on the model field.  
3. Type the exact model name as shown on Jetstream’s **Models** page, e.g.  

   ```
   mixtral-8x7b-instruct
   ```

### 3.4 (Optional) Adjust temperature and max‑tokens  

1. Search for **“Temperature”** – a slider will appear. Move it to your preferred value, e.g. `0.7`.  
2. Search for **“Max Tokens”** – enter an integer such as `200`.  

These options control the randomness of the output and the maximum length of the generated text.

---

## 4. Open the chat window and test the connection  

### 4.1 Using the native AI Assistant  

1. From the main menu choose **View → AI Assistant**.  
2. A panel slides in on the right‑hand side with a text box at the top.  
3. Type a simple prompt, for example:  

   ```
   What is the capital of Canada?
   ```  

4. Press **Enter**. The answer (“Ottawa”) should appear within a second.  

   *If you see an error like “Authentication failed”, return to step 3.2 and verify the API key.*

### 4.2 Using the EasyCode extension  

1. Click the **ChatGPT** icon that appeared in the Activity Bar (left side).  
2. A chat pane opens at the bottom of the window.  
3. Type the same prompt (`What is the capital of Canada?`) and press **Enter**.  
4. The model’s response will be displayed. Use the **Insert at cursor** button (appears next to the response) to paste the answer directly into the file you are editing.

---

## 5. Keep a conversation alive (GUI only)  

Both the native assistant and the EasyCode extension maintain conversation context automatically. Every time you type a new message in the same chat pane, the previous exchanges are sent along, so the model can refer back to earlier parts of the dialogue.  

*No extra configuration is needed* – just keep the chat pane open.

---

## 6. Alternative GUI clients (outside VS Code)  

If you want a separate graphical REST client, you can configure Jetstream entirely through the client’s interface. Below are brief steps for the two most popular tools.

### 6.1 Postman  

1. **Download & install** Postman from <https://www.postman.com/downloads/>.  
2. Click **New → Request**, give it a name (e.g., “Jetstream Chat”) and add it to a collection.  
3. Set the request method to **POST** and the URL to  

   ```
   https://llm.jetstream-cloud.org/v1/chat/completions
   ```

4. Open the **Headers** tab and add two rows:  

   | Key            | Value                                          |
   |----------------|------------------------------------------------|
   | Content-Type   | application/json                               |
   | Authorization  | Bearer jsc-XXXXXXXXXXXXXXXXXXXXXXXX (or `Bearer {{JETSTREAM_API_KEY}}` if you create an environment variable) |

5. Switch to the **Body** tab → select **raw → JSON** and paste this template (replace the prompt as needed):  

   ```json
   {
     "model": "mixtral-8x7b-instruct",
     "messages": [
       {
         "role": "user",
         "content": "Explain the difference between HTTP GET and POST in one sentence."
       }
     ],
     "max_tokens": 120,
     "temperature": 0.7
   }
   ```

6. Click **Send**. The response appears in the lower pane. You can copy the `content` field or write a test script in the **Tests** tab to extract it automatically.

### 6.2 Insomnia  

1. Install Insomnia from <https://insomnia.rest/download>.  
2. Click **Create → Request**, name it, and set the method to **POST**.  
3. URL: `https://llm.jetstream-cloud.org/v1/chat/completions`.  

4. In the **Headers** section add:  

   - `Content-Type: application/json`  
   - `Authorization: Bearer {{JETSTREAM_API_KEY}}`  

   Create an environment (top‑right **Environment** dropdown → **Manage Environments**) and add the variable `JETSTREAM_API_KEY` with the value of your Jetstream key.

5. In the **Body** tab choose **JSON** and paste the same JSON payload shown for Postman.  

6. Hit **Send** and view the response on the right.

Both tools let you save the request for later reuse or share it with teammates.

---

## 7. Troubleshooting checklist (GUI focus)

| Symptom | Likely cause | How to fix via GUI |
|---------|--------------|-------------------|
| **Authentication failed** | Wrong or missing API key | Open **Settings**, re‑enter the key (or verify the `${env:JETSTREAM_API_KEY}` placeholder). In Postman/Insomnia, double‑check the Authorization header. |
| **Empty `content` field** | `max_tokens` too low or model rejected request | Increase **Max Tokens** in Settings (or edit the numeric value in the request body of Postman/Insomnia). |
| **“Invalid model”** | Model name typo | In Settings, edit the **Model** field to exactly match the name shown on Jetstream’s **Models** page. |
| **Rate‑limit error after a few rapid clicks** | Free‑tier quota exhausted | Add a brief pause between requests (in Postman you can set a delay in the collection runner) or upgrade the Jetstream plan. |
| **Streaming output shows only `{}` lines** | Client does not support the `stream:true` flag | Use the built‑in AI Assistant, EasyCode chat pane, or the REST Client file with the `stream` flag; Postman’s basic UI does not render streaming chunks. |
| **Settings UI shows the old endpoint after editing** | Workspace settings overriding user settings | Open the **Workspace Settings** (gear icon → *Open Workspace Settings*) and remove any `apiBase` entry, then set it again in the **User Settings** UI. |

---

## 8. Quick visual‑reference cheat‑sheet  

| Action | Where to click |
|--------|----------------|
| **Open Settings** | `Ctrl+,` or *File → Preferences → Settings* |
| **Search a setting** | Type the keyword in the Settings search bar (e.g., “API Base”) |
| **Edit a field** | Click the **pencil** icon that appears on the right of the field |
| **Enable AI Assistant** | Search “AI Assistant Enabled”, tick the checkbox |
| **Open AI Assistant panel** | *View → AI Assistant* (or run *AI Assistant: Open* from the Command Palette) |
| **Install EasyCode extension** | Extensions view (`Ctrl+Shift+X`) → search “ChatGPT – EasyCode” → **Install** |
| **Open EasyCode chat pane** | Click the chat icon that appears in the Activity Bar after installation |
| **Add environment variable in Postman** | Gear icon → *Manage Environments* → **Add Variable** |
| **Add environment variable in Insomnia** | Top‑right **Environment** dropdown → **Manage Environments** → **Add Variable** |

---

## 9. Summary of steps (no code, pure GUI)

1. **Create an API key** on the Jetstream website.  
2. **Open VS Code Settings** and enable the **AI Assistant** (or install a chat extension).  
3. **Enter the API base** as `https://llm.jetstream-cloud.org/v1`.  
4. **Paste the API key** (or use `${env:JETSTREAM_API_KEY}`).  
5. **Set the model** name (e.g., `mixtral-8x7b-instruct`).  
6. Optionally adjust **Temperature** and **Max Tokens**.  
7. **Open the chat panel** (AI Assistant or EasyCode) and type a prompt to verify the connection.  
8. Keep the chat panel open to maintain conversational context; each new message automatically includes the previous history.  

You now have a fully functional, graphical interface to Jetstream’s LLM inside Visual Studio Code (and, optionally, in external REST clients). No terminal commands or manual JSON editing are required. Enjoy the AI‑powered workflow!