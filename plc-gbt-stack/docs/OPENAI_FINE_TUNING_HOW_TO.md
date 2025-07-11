# 📚 OpenAI Fine-Tuning How-To

## Quick Reference for Common Tasks

### How to Fine-Tune a Model from Scratch

```bash
# Step 1: Set up environment
export OPENAI_API_KEY='your-api-key'
cd plc-gbt-stack/scripts/ai

# Step 2: Initialize project (first time only)
python openai_fine_tuning_cli.py init

# Step 3: Prepare your training data
python openai_fine_tuning_cli.py prepare --input-file training_data.jsonl

# Step 4: Start training
python openai_fine_tuning_cli.py train

# Step 5: Monitor progress
python openai_fine_tuning_cli.py status --watch

# Step 6: Validate the model
python openai_fine_tuning_cli.py validate

# Step 7: Deploy to production
python openai_fine_tuning_cli.py deploy
```

### How to Check Training Costs

```bash
# View cost summary
python openai_fine_tuning_cli.py cost

# View detailed breakdown
python openai_fine_tuning_cli.py cost --detailed
```

### How to Validate Training Data Quality

```bash
# Validate without saving
python openai_fine_tuning_cli.py prepare --input-file data.jsonl --validate-only
```

### How to Resume a Failed Job

```bash
# Check job status
python openai_fine_tuning_cli.py status --job-id ftjob-abc123

# If failed, prepare data again and retry
python openai_fine_tuning_cli.py train --training-file prepared_data.jsonl
```

### How to Create Training Data

Format your data as JSONL with this structure:
```json
{"messages": [
    {"role": "system", "content": "You are an expert in industrial control systems."},
    {"role": "user", "content": "Your question here"},
    {"role": "assistant", "content": "Expert response here"}
]}
```

Save one example per line in a `.jsonl` file.

### How to Test a Fine-Tuned Model

```python
import openai

client = openai.OpenAI()
response = client.chat.completions.create(
    model="ft:gpt-4o-mini:industrial-control:abc123",
    messages=[
        {"role": "user", "content": "What are optimal PID parameters?"}
    ]
)
print(response.choices[0].message.content)
```

### How to Update Environment Variables

After deployment, update your `.env` file:
```bash
echo "OPENAI_FINETUNE_MODEL=ft:gpt-4o-mini:industrial-control:abc123" >> .env
```

### How to Generate Documentation

```bash
# Generate comprehensive documentation
python openai_fine_tuning_cli.py docs

# Files created in ~/.plc-gpt/fine-tuning/docs/
```

## Common Issues and Solutions

### "Model not found" Error
- Wait for fine-tuning to complete
- Check job status: `python openai_fine_tuning_cli.py status`

### High Training Costs
- Reduce dataset size
- Use fewer epochs
- Check token counts in data preparation

### Validation Fails
- Add more diverse training examples
- Include safety-critical scenarios
- Check for domain coverage gaps

### Rate Limit Errors
- Add delays between API calls
- Upgrade OpenAI tier
- Use batch processing

## Tips for Success

1. **Start Small**: Test with 50-100 examples first
2. **Quality Matters**: Well-formatted examples > quantity
3. **Monitor Costs**: Set budget limits during init
4. **Validate Early**: Test before full deployment
5. **Document Everything**: Use the docs command regularly 