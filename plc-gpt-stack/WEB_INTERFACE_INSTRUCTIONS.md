# 🌐 PLC-GPT Web Interface Access Instructions

## ✅ **CORRECT URL to Use**

**Access the web interface at:**
```
http://127.0.0.1:8081/plc-gbt-stack/web_interface.html
```

## ❌ **Do NOT Use This URL**

**This will cause "Failed to Fetch" errors:**
```
file:///Users/reh3376/repos/plc-gbt/plc-gbt-stack/web_interface.html
```

## 🔧 **Why This Matters**

- **File Protocol Issue**: Opening HTML files directly (`file://`) causes CORS (Cross-Origin Resource Sharing) restrictions
- **HTTP Server Required**: The web interface needs to be served via HTTP to communicate with the API at `localhost:8000`
- **Proper CORS Setup**: The gateway is configured to allow requests from `http://127.0.0.1:8081`

## 🚀 **How to Start the Web Interface**

1. **HTTP Server**: Already running on port 8081 (started automatically)
2. **Gateway API**: Running in Docker on port 8000
3. **Access URL**: http://127.0.0.1:8081/plc-gbt-stack/web_interface.html

## 🧪 **Testing the Interface**

Once opened, you can:

1. **Try Example Queries** - Click any example to auto-fill
2. **Submit Custom Queries** - Type your own PLC questions
3. **View Results** - See answers, graph context, vector context, and citations
4. **Monitor Performance** - Response times are displayed

## 🔍 **Example Queries to Test**

- "What AOIs are in Program MainProgram_v1.2?"
- "Find all routines that use timer instructions"
- "Show me all UDTs in the system"
- "What devices are connected to the controller?"
- "Find safety-related components"

## 🛠 **Troubleshooting**

If you still get "Failed to Fetch":

1. **Check URL**: Ensure you're using `http://127.0.0.1:8081/plc-gbt-stack/web_interface.html`
2. **Check Services**: Verify Docker containers are running (`docker-compose ps`)
3. **Check HTTP Server**: Verify server is running (`ps aux | grep http.server`)

## ✅ **Success Indicators**

- Web interface loads with professional styling
- Example queries are clickable
- Query form accepts input
- Results display with metrics
- No "Failed to Fetch" errors 