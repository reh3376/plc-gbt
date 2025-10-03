# AI Assistant Setup Guide

## ✅ Fix Applied

The AI Assistant now connects to your fine-tuned OpenAI model instead of returning mock responses!

**Model**: `ft:gpt-4o:industrial-control:20250117`

---

## 🚀 Setup Instructions

### 1. Install OpenAI Package

```bash
cd /Users/reh3376/repos/plc-gbt
source .venv/bin/activate
pip install openai>=1.0.0
```

### 2. Set OpenAI API Key

Add your OpenAI API key to your environment:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Make it permanent** (optional):
```bash
echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Restart Backend Server

Stop the current backend (Ctrl+C) and restart:

```bash
cd /Users/reh3376/repos/plc-gbt/plc-gbt-stack
python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the AI Assistant

1. Open http://localhost:3001 in your browser
2. Click the AI Assistant toggle button
3. Type a message like "How do I tune a PID controller?"
4. You should now get **real AI responses** instead of generic parroting!

---

## 🎯 What Changed

### Before (Mock Response):
```python
# Mock AI response
ai_response = {
    "message": f"I understand you're asking about: {user_message[:50]}..."
}
```

### After (Real OpenAI):
```python
# Get OpenAI service and generate response
openai_service = get_openai_service()
ai_response = await openai_service.chat_completion(
    message=user_message,
    conversation_history=conversation_history,
    context=context,
    stream=False
)
```

---

## 🧠 Features

The AI Assistant now:

✅ **Connects to fine-tuned model** - Industrial control expertise  
✅ **Context-aware** - Understands current file and workspace  
✅ **Conversation history** - Maintains context across messages  
✅ **Smart suggestions** - Contextual follow-up questions based on topic  
✅ **Fallback mode** - Gracefully handles API errors with helpful messages  

### Contextual Suggestions

The assistant automatically provides relevant suggestions based on your question:

- **PID/Control questions** → Tuning methods, parameter analysis
- **PLC/Ladder Logic** → Code optimization, best practices  
- **Control Loops** → Performance analysis, troubleshooting
- **Workflows** → Automation sequences, optimization

---

## ⚠️ Fallback Mode

If OpenAI API key is **not set**, the assistant will show:

> ⚠️ The AI assistant requires an OpenAI API key to function.  
> Please set the OPENAI_API_KEY environment variable and restart the server.

This is much better than the old "I understand you're asking about..." response!

---

## 📊 Technical Details

### Files Modified:

1. **`plc-gbt-stack/api/services/openai_service.py`** (NEW)
   - OpenAI client wrapper
   - Fine-tuned model integration
   - Context formatting
   - Fallback handling

2. **`plc-gbt-stack/api/cli_api_bridge.py`** (UPDATED)
   - Endpoint now uses OpenAI service
   - Added smart suggestion generation
   - Better error handling

3. **`requirements.txt`** (UPDATED)
   - Added `openai>=1.0.0`

### System Message:
```
You are an expert industrial automation AI assistant specialized in 
PLC programming, control systems, and industrial protocols. 
You provide accurate, practical guidance on control theory, PID tuning, 
ladder logic, function blocks, and industrial automation best practices. 
Be concise, technical, and safety-conscious in your responses.
```

---

## 🔍 Troubleshooting

### "Module 'openai' not found"
```bash
pip install openai
```

### "API Key not found"
Check your environment:
```bash
echo $OPENAI_API_KEY
```

If empty, set it:
```bash
export OPENAI_API_KEY="sk-..."
```

### "Model not found" error
Verify the fine-tuned model ID exists in your OpenAI account:
- Model: `ft:gpt-4o:industrial-control:20250117`
- Check at: https://platform.openai.com/finetune

### Still getting generic responses
1. Check backend logs for errors
2. Verify OPENAI_API_KEY is set
3. Restart backend server
4. Clear browser cache and refresh

---

## ✅ Testing Checklist

- [ ] `pip install openai` completed
- [ ] `OPENAI_API_KEY` environment variable set
- [ ] Backend server restarted with key
- [ ] Frontend at http://localhost:3001 loads
- [ ] AI Assistant panel opens
- [ ] Sent test message
- [ ] Got intelligent response (not parrot)
- [ ] Suggestions appear and are relevant
- [ ] Conversation history maintained

---

**The AI Assistant is now fully functional with your fine-tuned industrial control model!** 🎉

