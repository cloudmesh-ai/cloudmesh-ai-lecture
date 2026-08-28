
# Using Jetstream Cloud LLM from VS Code

* <https://llm.jetstream-cloud.org>

The guide is split into three parts:

1. **Command‑line** – run `curl` / `httpie` from the integrated terminal.  
2. **VS Code GUI** – use the built‑in AI Assistant or a third‑party chat extension.  
3. **Other GUI clients** – Postman, Insomnia, or the VS Code REST Client extension.

All numeric values are plain integers or decimals (no scientific notation).  

---

## 1. Command‑line (integrated terminal)

### 1.1 Set environment variables (once)

| Shell | Command |
|-------|---------|
| Bash / Zsh | `export JETSTREAM_API_KEY="jsc-XXXXXXXXXXXXXXXXXXXXXXXX"`<br>`export JETSTREAM_MODEL="mixtral-8x7b-instruct"` |
| PowerShell | `$env:JETSTREAM_API_KEY = "jsc-XXXXXXXXXXXXXXXXXXXXXXXX"`<br>`$env:JETSTREAM_MODEL = "mixtral-8x7b-instruct"` |

Add the lines to your shell profile (`~/.bashrc`, `~/.zshrc`, or the PowerShell profile) so VS Code’s terminal inherits them automatically.

### 1.2 One‑shot request (plain numbers)

```bash
curl -s https://llm.jetstream-cloud.org/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JETSTREAM_API_KEY" \
  -d '{
        "model":"'"$JETSTREAM_MODEL"'",
        "messages":[{"role":"user","content":"Explain the difference between HTTP GET and POST in one sentence."}],
        "max_tokens":120,
        "temperature":0.7
      }' | jq -r '.choices[0].message.content'
```

### 1.3 Streaming request (token‑by‑token)

```bash
curl -s https://llm.jetstream-cloud.org/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JETSTREAM_API_KEY" \
  -d '{
        "model":"'"$JETSTREAM_MODEL"'",
        "messages":[{"role":"user","content":"Write a four‑line haiku about rain."}],
        "max_tokens":150,
        "temperature":0.9,
        "stream":true
      }' |
while IFS= read -r line; do
  echo "$line" | jq -r '.choices[0].delta.content // empty'
done
```

> **Alternative using `httpie`**  
> ```
> http POST https://llm.jetstream-cloud.org/v1/chat/completions \
>   Authorization:"Bearer $JETSTREAM_API_KEY" \
>   model=$JETSTREAM_MODEL \
>   messages:='[{"role":"user","content":"Your prompt here"}]' \
>   max_tokens:=120 temperature:=0.7
> ```

---

## 2. VS Code GUI (chat window)

### 2.1 Built‑in AI Assistant (VS Code ≥ 1.87)

1. Open **Settings** (`Ctrl+,`).  
2. Search for **“AI Assistant: Enabled”** and tick the checkbox.  
3. Search for **“AI Assistant: API Base”** → enter  

   ```
   https://llm.jetstream-cloud.org/v1
   ```

4. Search for **“AI Assistant: API Key”** → paste the Jetstream key **or** use the placeholder  

   ```
   ${env:JETSTREAM_API_KEY}
   ```

5. Search for **“AI Assistant: Model”** → type the model you own, e.g.  

   ```
   mixtral-8x7b-instruct
   ```

6. (Optional) Adjust **Temperature** and **Max Tokens** using the sliders that appear next to the model setting.  

7. Open the assistant panel: **View → AI Assistant** (or run *AI Assistant: Open* from the Command Palette).  

   The panel works like a chat window. Type a prompt, press **Enter**, and the answer streams live. Click **Insert** beside the response to paste it into the active editor.

### 2.2 Third‑party chat extension (example: *ChatGPT – EasyCode*)

1. Open the **Extensions** view (`Ctrl+Shift+X`).  
2. Search for **“ChatGPT – EasyCode”** and click **Install**.  
3. After installation, a chat icon appears in the Activity Bar.  

4. Open **Settings** (`Ctrl+,`).  

   * **API Base** – search for *ChatGPT: API Base*, click the edit (pencil) icon, and type  

     ```
     https://llm.jetstream-cloud.org/v1
     ```

   * **API Key** – search for *ChatGPT: API Key*, click edit, and paste the Jetstream key **or** `${env:JETSTREAM_API_KEY}`.  

   * **Model** – search for *ChatGPT: Model* and type the exact model name (e.g., `mixtral-8x7b-instruct`).  

   * **Temperature** – use the provided slider to set a value such as `0.7`.  

   * **Max Tokens** – type an integer like `200`.  

5. Open the chat pane via the new icon or run *ChatGPT: New Chat* from the Command Palette.  
   The UI behaves identically to the built‑in assistant and supports **Insert at cursor**.

### 2.3 Verify the connection (GUI)

1. In whichever chat pane you opened, type a simple prompt, e.g.  

   ```
   What is the capital of Canada?
   ```  

2. Press **Enter**.  

3. The model should reply within a second. If you see an error such as *Authentication failed* or *Invalid model*, return to the Settings UI and double‑check the API base, key, and model fields.

---

## 3. Other GUI clients (stand‑alone tools)

If you prefer a dedicated REST client, any of the following can be used without writing code.

### 3.1 Postman

1. **Download & install** Postman from https://www.postman.com/downloads/.  
2. Click **New → Request**, give it a name (e.g., *Jetstream Chat*), and save it in a collection.  

3. Fill out the request:

   * **Method** – `POST`  
   * **URL** – `https://llm.jetstream-cloud.org/v1/chat/completions`  

4. **Headers** (add two rows)  

   | Key           | Value                                        |
   |---------------|----------------------------------------------|
   | Content-Type  | application/json                             |
   | Authorization | Bearer `jsc-XXXXXXXXXXXXXXXXXXXXXXXX` (or `Bearer {{JETSTREAM_API_KEY}}`) |

   To use an environment variable, create an environment (gear icon → *Manage Environments*) with a variable named `JETSTREAM_API_KEY` containing the key, then reference it as `{{JETSTREAM_API_KEY}}`.

5. **Body** – select **raw → JSON** and paste:

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

6. Click **Send**. The response appears in the lower pane. You can copy the `content` field or write a test script to extract it automatically.

### 3.2 Insomnia

1. Install Insomnia from https://insomnia.rest/download.  
2. Click **Create → Request**, name it, and set the method to **POST**.  
3. URL → `https://llm.jetstream-cloud.org/v1/chat/completions`.  

4. **Headers**  

   * `Content-Type: application/json`  
   * `Authorization: Bearer {{JETSTREAM_API_KEY}}`  

   Create an environment variable `JETSTREAM_API_KEY` with the key (top‑right “Environment” → Manage Environments).

5. **Body** – choose **JSON** and paste:

   ```json
   {
     "model": "mixtral-8x7b-instruct",
     "messages": [
       {
         "role": "user",
         "content": "Write a short Python function that returns the fibonacci sequence up to n."
       }
     ],
     "max_tokens": 300,
     "temperature": 0.6
   }
   ```

6. Click **Send**. The response appears on the right side.

### 3.3 VS Code REST Client extension

1. Install the **REST Client** extension (`humao.rest-client`) from the Extensions view.  
2. Create a file named `jetstream.http` in your workspace.  

3. Paste the following (the API key can be read from an environment variable):

   ```http
   @base = https://llm.jetstream-cloud.org/v1
   @apiKey = ${env:JETSTREAM_API_KEY}

   ### One‑shot request
   POST {{base}}/chat/completions
   Content-Type: application/json
   Authorization: Bearer {{apiKey}}

   {
     "model": "mixtral-8x7b-instruct",
     "messages": [
       {
         "role": "user",
         "content": "What is the capital of Canada?"
       }
     ],
     "max_tokens": 120,
     "temperature": 0.7
   }
   ```

4. Place the cursor anywhere inside the request block and click **Send Request** (or press `Ctrl+Alt+R`).  

   - The response appears in a side panel.  
   - For a streaming request, add `"stream": true` to the JSON payload; the raw stream will be shown line‑by‑line.

5. To avoid storing the key in the file, define it in VS Code settings:

   ```json
   {
     "rest-client.environmentVariables": {
       "$shared": {
         "apiKey": "${env:JETSTREAM_API_KEY}"
       }
     }
   }
   ```

   Now `{{apiKey}}` resolves from the environment variable.

---

## 4. Quick verification command (any method)

```bash
curl -s https://llm.jetstream-cloud.org/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JETSTREAM_API_KEY" \
  -d '{"model":"mixtral-8x7b-instruct","messages":[{"role":"user","content":"What is the capital of Canada?"}],"max_tokens":120,"temperature":0.7}' \
  | jq -r '.choices[0].message.content'
```

Expected output: `Ottawa`.

If you receive an error, revisit the steps where the API key, base URL, or model are set.

---

## 5. Troubleshooting checklist (GUI‑focused)

| Symptom | Likely cause | GUI fix |
|---------|--------------|---------|
| “Authentication failed” in the chat pane | API key not supplied or mistyped | Re‑open Settings → **API Key** and ensure the field contains the exact key **or** `${env:JETSTREAM_API_KEY}`. If using an environment variable, verify it with `echo $JETSTREAM_API_KEY` in the integrated terminal. |
| Empty or missing `content` in response | Wrong model name | Open the Jetstream dashboard → **Models**, copy the exact name, and update the **Model** field in Settings or in the request body. |
| “Rate limit exceeded” after several rapid calls | Free‑tier quota reached | Insert a small pause (`sleep 1`) between calls, or upgrade the Jetstream plan. |
| Streaming request only returns `{}` lines | Client does not support streaming | Use the built‑in AI Assistant, the chat extension, or the REST Client file with the `"stream": true` flag. |
| Settings UI shows the old endpoint after editing | Workspace settings overriding user settings | Open the `.vscode/settings.json` file in the workspace and remove any `"aiAssistant.apiBase"` entry, then set the value again via the Settings UI. |

---

## 6. Summary checklist

- **Generate API key** on the Jetstream portal.  
- **Set the key** either directly in VS Code settings or via an environment variable (`JETSTREAM_API_KEY`).  
- **Pick a GUI method**:  
  * Built‑in AI Assistant (recommended for newest VS Code versions) **or**  
  * Third‑party chat extension (ChatGPT – EasyCode, CodeGPT, etc.).  
- **Configure the extension** through the Settings UI: API Base → `https://llm.jetstream-cloud.org/v1`, API Key → key or `${env:JETSTREAM_API_KEY}`, Model → your chosen model, Temperature & Max Tokens as desired.  
- **Test** with a simple prompt (e.g., “What is the capital of Canada?”).  
- **Optional**: use Postman, Insomnia, or the VS Code REST Client for saved request collections that can be shared with teammates.  

Following these steps gives you full command‑line access and a fully integrated graphical chat experience for Jetstream’s language models inside Visual Studio Code.