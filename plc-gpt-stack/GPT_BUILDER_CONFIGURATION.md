# 🤖 ChatGPT GPT Builder Configuration Guide

## 📋 Overview

This guide provides step-by-step instructions for creating a PLC-Savvy GPT using ChatGPT's GPT Builder with custom actions connected to our PLC knowledge graph and vector store.

## 🚀 Quick Setup Checklist

- [ ] Access GPT Builder (ChatGPT Plus/Enterprise required)
- [ ] Configure GPT Instructions and persona
- [ ] Set up custom Actions with OpenAPI specification
- [ ] Configure authentication with bearer token
- [ ] Test action connectivity
- [ ] Publish and set permissions

## 📝 Step 1: GPT Builder Access

1. **Navigate to GPT Builder**:
   - Go to [chat.openai.com](https://chat.openai.com)
   - Click **"Explore"** in the sidebar
   - Click **"Create a GPT"** button

2. **Choose Creation Method**:
   - Select **"Configure"** tab for manual setup
   - (Alternative: Use "Create" tab for conversational setup)

## 🎯 Step 2: Instructions Configuration

### **GPT Name**
```
PLC-Savvy GPT
```

### **Description**
```
Expert industrial automation assistant specializing in PLC programming, Allen-Bradley systems, and control engineering. Provides technical guidance for Studio 5000, L5X files, AOI development, and industrial best practices.
```

### **Instructions**
```markdown
# PLC-Savvy GPT Instructions

You are an expert industrial automation engineer specializing in PLC (Programmable Logic Controller) programming, with deep expertise in Allen-Bradley/Rockwell Automation systems, Studio 5000, and industrial control systems.

## Core Expertise Areas
- **PLC Programming**: Ladder logic, structured text, function blocks
- **Allen-Bradley Systems**: ControlLogix, CompactLogix, GuardLogix
- **Studio 5000**: Project development, AOI creation, HMI integration
- **Industrial Networks**: EtherNet/IP, DeviceNet, ControlNet
- **Motion Control**: Servo systems, VFDs, coordinated motion
- **Safety Systems**: GuardLogix safety, SIL ratings, safety functions
- **Process Control**: PID loops, cascade control, feedforward control

## Knowledge Access Protocol
**CRITICAL**: When users ask questions about specific PLC systems, components, or need technical guidance that requires access to our knowledge base, you MUST use the `queryKnowledge` action to retrieve accurate, up-to-date information.

### When to Use queryKnowledge Action:
- Questions about specific AOIs, routines, or PLC programs
- Technical specifications or component details
- Best practices for specific applications
- Troubleshooting guidance
- L5X file analysis or interpretation
- Configuration recommendations
- Safety system requirements
- Motion control setup guidance

### Query Examples:
- "What AOIs are available in Program MainProgram_v1.2?"
- "How do I configure a PID loop for temperature control?"
- "What are the safety considerations for this motion application?"
- "Analyze this L5X file structure"

## Response Format Guidelines
1. **Always cite sources** when using information from queryKnowledge
2. **Provide context** about why specific recommendations are made
3. **Include safety considerations** for all industrial applications
4. **Offer step-by-step guidance** for complex procedures
5. **Suggest best practices** based on industry standards

## Safety First Approach
- Always emphasize safety procedures and lockout/tagout
- Recommend proper testing in development environments
- Highlight potential safety implications of changes
- Reference relevant safety standards (IEC 61508, ISO 13849)

## Communication Style
- **Professional but approachable**: Use technical terms appropriately
- **Practical focus**: Provide actionable guidance
- **Educational**: Explain the "why" behind recommendations
- **Comprehensive**: Cover edge cases and considerations
- **Current**: Reference latest software versions and practices

## Limitations Acknowledgment
If the queryKnowledge action doesn't return sufficient information, clearly state this and provide general guidance while recommending consultation with official documentation or field experts for critical applications.
```

### **Conversation Starters**
```
1. "What AOIs are available in my PLC program?"
2. "How do I configure a PID loop for temperature control?"
3. "What are the best practices for motion control programming?"
4. "Help me analyze an L5X file structure"
```

## 🧠 Step 3: Knowledge Base Setup

### **Upload Documents** (Optional)
You can upload reference documents to supplement the GPT's knowledge:

**Recommended Documents**:
- Allen-Bradley Programming Manual excerpts
- Studio 5000 quick reference guides
- Safety system configuration guides
- Motion control best practices
- Common AOI templates

**File Limits**:
- Up to 20 files
- 512MB total size
- Supported formats: PDF, TXT, DOCX

## ⚙️ Step 4: Actions Configuration

### **Add Custom Action**

1. **Click "Create new action"**

2. **Authentication Setup**:
   - **Authentication Type**: `API Key`
   - **API Key**: `your-secure-bearer-token-here`
   - **Auth Type**: `Bearer`

3. **Schema Configuration**:
   - **Import from URL**: `http://localhost:8000/openapi.json` (if available)
   - **OR Paste Schema**: Copy the entire content from `openapi_specification.yaml`

### **OpenAPI Schema** (Paste this in the Schema field):
```yaml
# Paste the complete content from openapi_specification.yaml here
# (The file content is too long to include inline - reference the file)
```

### **Privacy Policy** (Optional)
```
https://github.com/reh3376/plc-gbt/blob/main/PRIVACY.md
```

## 🔧 Step 5: Model Configuration

### **Model Selection**
- **Primary Model**: `gpt-4o` (if available)
- **Fallback Model**: `gpt-4o-mini`
- **Temperature**: `0.3` (for consistent technical responses)
- **Top P**: `0.9`
- **Max Tokens**: `4000`

### **Advanced Settings**
- **Web Browsing**: `Disabled` (rely on knowledge base)
- **DALL-E**: `Disabled` (not needed for PLC applications)
- **Code Interpreter**: `Enabled` (for L5X file analysis)

## 🧪 Step 6: Testing Configuration

### **Test Queries**
Before publishing, test these queries:

1. **Basic Connectivity**:
   ```
   Test the system health
   ```

2. **Knowledge Query**:
   ```
   What AOIs are available in the system?
   ```

3. **Technical Question**:
   ```
   How do I configure a PID loop for temperature control?
   ```

4. **Complex Query**:
   ```
   What are the best practices for motion control programming with safety considerations?
   ```

### **Expected Behavior**
- GPT should automatically call `queryKnowledge` action for technical questions
- Responses should include citations and sources
- Should provide comprehensive, safety-focused guidance
- Response time should be under 10 seconds

## 📤 Step 7: Publishing

### **Visibility Settings**
- **Only me**: For testing and development
- **Anyone with a link**: For team sharing
- **Public**: For general availability (Enterprise only)

### **Category Selection**
- **Primary**: `Programming`
- **Secondary**: `Research & Analysis`

### **Additional Settings**
- **Allow others to chat with this GPT**: `Yes` (if sharing)
- **Allow others to copy this GPT**: `No` (to protect configuration)

## 🔒 Step 8: Security Configuration

### **Bearer Token Management**
1. **Current Token**: `your-secure-bearer-token-here`
2. **Token Rotation**: Plan for quarterly rotation
3. **Access Logging**: Monitor usage through gateway logs

### **Network Security**
- Ensure gateway is accessible from OpenAI's servers
- Configure firewall rules for HTTPS traffic
- Use HTTPS in production (update OpenAPI servers section)

## 📊 Step 9: Monitoring & Maintenance

### **Usage Monitoring**
- Monitor action calls through gateway logs
- Track response times and error rates
- Review user feedback and query patterns

### **Regular Updates**
- **Monthly**: Review and update instructions based on usage
- **Quarterly**: Update knowledge base documents
- **As needed**: Update OpenAPI specification for new features

## 🚨 Troubleshooting

### **Common Issues**

1. **Action Not Working**:
   - Verify bearer token is correct
   - Check gateway service is running
   - Validate OpenAPI schema syntax

2. **Slow Responses**:
   - Check gateway performance
   - Verify Neo4j and Qdrant are healthy
   - Monitor network latency

3. **Authentication Errors**:
   - Confirm bearer token format
   - Check CORS configuration
   - Verify endpoint URLs

### **Debug Steps**
1. Test gateway health endpoint directly
2. Validate OpenAPI schema with online tools
3. Check GPT action logs in builder interface
4. Monitor gateway logs for incoming requests

## 📋 Configuration Summary

| Setting | Value |
|---------|--------|
| **Name** | PLC-Savvy GPT |
| **Model** | gpt-4o / gpt-4o-mini |
| **Temperature** | 0.3 |
| **Actions** | queryKnowledge, healthCheck, getSystemStats |
| **Authentication** | Bearer Token |
| **Primary Endpoint** | /api/v1/query |
| **Max Tokens** | 4000 |

## 🎯 Success Criteria

- ✅ GPT responds to PLC-related queries with accurate information
- ✅ Actions successfully connect to knowledge base
- ✅ Response time under 10 seconds for most queries
- ✅ Proper citation of sources and safety considerations
- ✅ Professional, technical communication style
- ✅ Zero unauthorized access attempts

**Ready for Phase 6**: Once GPT is published and tested successfully, proceed to Phase 6: Maintenance & Governance Systems. 