import re

# Read the file
with open('scripts/run_pipeline.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace client with model
content = content.replace('client = genai.Client()', 'model = genai.GenerativeModel("gemini-pro")')
content = content.replace('return client', 'return model')
content = content.replace('def ai_call(client,', 'def ai_call(model,')
content = content.replace('# Create client - automatically uses GEMINI_API_KEY environment variable', 'genai.configure(api_key=GEMINI_API_KEY)')

# Replace the generate_content call
content = re.sub(
    r'response = client\.models\.generate_content\(\s*model="gemini-1\.5-flash",\s*contents=prompt\s*\)',
    'response = model.generate_content(prompt)',
    content,
    flags=re.DOTALL
)

# Write back
with open('scripts/run_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated successfully!')
