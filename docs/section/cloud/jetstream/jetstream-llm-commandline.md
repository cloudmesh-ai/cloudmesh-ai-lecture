
**Using the Jetstream Cloud LLM (`https://llm.jetstream-cloud.org/`) from the VS Code command line**

Below is a plain‑text guide that shows three ways to call the model from inside Visual Studio Code:  

1. Directly from the integrated terminal (curl / httpie).  
2. Through a chat‑style VS Code extension that supports OpenAI‑compatible APIs.  
3. By defining a reusable VS Code task (or key‑binding) that runs a small shell script.

---

## 1. Call the API from the integrated terminal

Add the environment variables to the shell profile that VS Code uses (e.g., `~/.bashrc`, `~/.zshrc`, or the PowerShell profile).

```bash
export JETSTREAM_API_KEY="jsc-XXXXXXXXXXXXXXXXXXXXXXXX"
export JETSTREAM_MODEL="mixtral-8x7b-instruct"
```

### One‑shot request (plain numbers)

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

### Streaming request (token‑by‑token)

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

*Tip:* If you prefer `httpie`, replace `curl …` with:

```bash
http POST https://llm.jetstream-cloud.org/v1/chat/completions \
  Authorization:"Bearer $JETSTREAM_API_KEY" \
  model=$JETSTREAM_MODEL \
  messages:='[{"role":"user","content":"Your prompt here"}]' \
  max_tokens:=120 temperature:=0.7
```

---

## 2. Use a VS Code chat extension

Most extensions that support OpenAI‑compatible APIs can be pointed at Jetstream. The steps below use **ChatGPT – EasyCode** as an example, but the same workflow applies to other extensions (CodeGPT, OpenAI Assistant, Chat Copilot, etc.).

1. Open the Extensions view (`Ctrl+Shift+X`).  
2. Search for **“ChatGPT – EasyCode”** and click **Install**.  
3. Open Settings (`Ctrl+,`) and locate **ChatGPT: API Base**. Set the value to:

   ```
   https://llm.jetstream-cloud.org/v1
   ```

4. Locate **ChatGPT: API Key** and set it to `${env:JETSTREAM_API_KEY}` (or paste the key directly if you prefer).  

5. (Optional) Set a default model, temperature, and max‑tokens:

   ```json
   // settings.json (open via “Preferences: Open Settings (JSON)”)
   {
     "chatgpt.apiBase": "https://llm.jetstream-cloud.org/v1",
     "chatgpt.apiKey": "${env:JETSTREAM_API_KEY}",
     "chatgpt.model": "mixtral-8x7b-instruct",
     "chatgpt.temperature": 0.7,
     "chatgpt.maxTokens": 200
   }
   ```

6. Use the chat UI: press `Ctrl+Shift+P`, select **ChatGPT: New Chat**, and type prompts. The pane shows streaming responses and lets you **Insert at cursor** to paste the answer directly into the active file.

If you are on a VS Code version that includes the built‑in **AI Assistant**:

```json
{
  "aiAssistant.enabled": true,
  "aiAssistant.apiBase": "https://llm.jetstream-cloud.org/v1",
  "aiAssistant.apiKey": "${env:JETSTREAM_API_KEY}",
  "aiAssistant.model": "mixtral-8x7b-instruct",
  "aiAssistant.temperature": 0.7,
  "aiAssistant.maxTokens": 200
}
```

Open the panel via **View → AI Assistant** and interact in the same way.

---

## 3. Create a reusable VS Code task

For workflows that need to be triggered repeatedly (e.g., “generate a Jest test for the selected function”), define a shell script and a VS Code task.

### 3.1 Shell script (`jet_prompt.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail

# Use env vars if set, otherwise fall back to placeholders
export JETSTREAM_API_KEY="${JETSTREAM_API_KEY:-jsc-XXXXXXXXXXXXXXXXXXXXXXXX}"
MODEL="${JETSTREAM_MODEL:-mixtral-8x7b-instruct}"

# Read prompt: arguments if supplied, otherwise stdin (selection)
if [[ $# -gt 0 ]]; then
    PROMPT="$*"
else
    PROMPT="$(cat -)"
fi

curl -s https://llm.jetstream-cloud.org/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JETSTREAM_API_KEY" \
  -d "$(printf '{\"model\":\"%s\",\"messages\":[{\"role\":\"user\",\"content\":\"%s\"}],\"max_tokens\":300,\"temperature\":0.7}' \
        "$MODEL" "$PROMPT")" |
jq -r '.choices[0].message.content'
```

Make it executable:

```bash
chmod +x jet_prompt.sh
```

Place the script in the workspace folder (or a location referenced by `${workspaceFolder}`).

### 3.2 Task definition (`.vscode/tasks.json`)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Ask Jetstream (selection)",
      "type": "shell",
      "command": "${workspaceFolder}/jet_prompt.sh",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "dedicated",
        "clear": true
      }
    },
    {
      "label": "Ask Jetstream (input box)",
      "type": "process",
      "command": "node",
      "args": [
        "-e",
        "const rl = require('readline').createInterface({input:process.stdin,output:process.stdout}); rl.question('Prompt: ', p=>{require('child_process').execSync(`${process.cwd()}/jet_prompt.sh \"${p}\"`, {stdio:'inherit'}); rl.close();});"
      ],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "dedicated",
        "clear": true
      }
    }
  ]
}
```

* **Task “Ask Jetstream (selection)”** – works on the currently highlighted text.  
  *Select code → `Ctrl+Shift+P` → “Run Task” → “Ask Jetstream (selection)”.*  
  The answer appears in a dedicated terminal pane.

* **Task “Ask Jetstream (input box)”** – pops up a prompt for free‑form text.

### 3.3 Optional key‑binding

Add the following to `keybindings.json` (File → Preferences → Keyboard Shortcuts → Open keybindings.json):

```json
[
  {
    "key": "ctrl+alt+j",
    "command": "workbench.action.tasks.runTask",
    "args": "Ask Jetstream (selection)"
  },
  {
    "key": "ctrl+alt+shift+j",
    "command": "workbench.action.tasks.runTask",
    "args": "Ask Jetstream (input box)"
  }
]
```

Now pressing **Ctrl + Alt + J** on a highlighted block runs the script and displays the model’s response.

---

## 4. Storing the API key safely

### Environment variable (recommended)

Add the line to the shell profile loaded by VS Code’s terminal:

```bash
export JETSTREAM_API_KEY="jsc-XXXXXXXXXXXXXXXXXXXXXXXX"
```

All extensions that read `${env:JETSTREAM_API_KEY}` will use the variable without persisting the secret in a settings file.

### Direct settings entry (if necessary)

Edit the appropriate settings file and include the key as a plain string:

```json
{
  "chatgpt.apiKey": "jsc-XXXXXXXXXXXXXXXXXXXXXXXX"
}
```

If you use Settings Sync, add a `"sync.ignore"` pattern to keep the key out of the sync payload.

---

## 5. Quick verification command

Run this in the VS Code terminal to confirm that the endpoint, model, and numeric parameters are being accepted:

```bash
curl -s https://llm.jetstream-cloud.org/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JETSTREAM_API_KEY" \
  -d '{"model":"mixtral-8x7b-instruct","messages":[{"role":"user","content":"What is the capital of Canada?"}],"max_tokens":120,"temperature":0.7}' \
  | jq -r '.choices[0].message.content'
```

All numeric literals (`max_tokens`: 120, `temperature`: 0.7) are plain integers or decimals, not scientific notation.

---

### Summary checklist

1. **Set environment variables** `JETSTREAM_API_KEY` and optionally `JETSTREAM_MODEL`.  
2. **For ad‑hoc use**, run the curl one‑liners in the integrated terminal.  
3. **For a GUI chat experience**, install a compatible VS Code extension and point its API base to `https://llm.jetstream-cloud.org/v1`.  
4. **For repeated prompts**, create `jet_prompt.sh` and a VS Code task, then bind a key‑shortcut if desired.  
5. **Keep the API key out of source control** by using an environment variable or excluding it from Settings Sync.

Following these steps gives you both a command‑line and a graphical workflow for the Jetstream Cloud LLM, entirely within Visual Studio Code.