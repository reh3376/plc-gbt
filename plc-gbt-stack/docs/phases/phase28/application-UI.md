# Building a VS Code-Style Multi-Pane UI for PLC-GBT

**Phase 28: Application UI Development**  
**Date:** Updated for improved formatting  
**Status:** Planning & Design Document

---

## Overview

This document outlines approaches for creating a browser-based interface with a **VS Code-like layout** for the PLC-GBT platform. We explore both **Python-based solutions** (Streamlit preferred) and alternative front-end frameworks, with references to open-source projects and templates that demonstrate these concepts.

### Key Requirements
- Multi-pane layout similar to VS Code
- File explorer sidebar
- Tabbed editor interface
- Workflow canvas (n8n/Node-RED style)
- Chat interface for LLM integration
- User authentication and role-based access
- Python-first approach (where possible)

---

## Table of Contents

1. [Streamlit-Based Approach (Python)](#1-streamlit-based-approach-python)
2. [Open-Source Design References & Frameworks](#2-open-source-design-references--frameworks)
3. [Recommended Implementation Path](#3-recommended-implementation-path)
4. [Technical References](#4-technical-references)

---

## 1. Streamlit-Based Approach (Python)

Streamlit provides a quick way to build UIs in Python, and with extensions it can approximate a multi-pane IDE layout.

### 1.1 Layout with Sidebar and Main Area

Streamlit natively supports:
- **Sidebar** (`st.sidebar`) - Can serve as file explorer panel
- **Main content area** - For editors and other content

#### File Explorer Integration
The open-source **streamlit-file-browser** component can render an interactive file tree in Streamlit, mimicking VS Code's explorer:

```python
import streamlit as st
from streamlit_file_browser import st_file_browser

# Create file browser in sidebar
with st.sidebar:
    event = st_file_browser("Select a file", path="./project")
    
    if event:
        st.write(f"Selected: {event['selected']}")
```

**Features:**
- Folder navigation
- File preview
- Upload functionality
- Tree-style directory structure

### 1.2 Custom Multi-Pane Layout

While Streamlit doesn't natively support drag-resize panels, the **Streamlit Elements** library enables:

- Embedding React components (Material UI, Monaco editor)
- Creating draggable, resizable panels
- Advanced layout management

#### Implementation Example

```python
from streamlit_elements import elements, mui, html, sync
from streamlit_elements import nivo, editor

def create_ide_layout():
    with elements("ide_layout"):
        # Top AppBar (File/Edit menus)
        with mui.AppBar(position="static"):
            with mui.Toolbar():
                mui.Typography("PLC-GBT IDE", variant="h6")
        
        # Main layout with drawer
        with mui.Box(sx={"display": "flex"}):
            # Left Drawer (sidebar)
            with mui.Drawer(variant="permanent", 
                           sx={"width": 240}):
                # File tree component
                file_tree()
            
            # Main content area
            with mui.Box(component="main", 
                        sx={"flexGrow": 1, "p": 3}):
                # Monaco editor
                editor.monaco(
                    height=500,
                    defaultLanguage="python",
                    defaultValue="# Welcome to PLC-GBT",
                    key="code_editor"
                )
```

### 1.3 Tabbed Editor/Workspace

Streamlit now supports tabs (`st.tabs`) for simulating a tabbed editor interface:

```python
tab1, tab2, tab3 = st.tabs(["Main.py", "Config.yaml", "Workflow"])

with tab1:
    # Monaco editor for Python code
    st_monaco_editor(
        value="# Python code here",
        language="python",
        height="400px"
    )

with tab2:
    # YAML configuration editor
    st_monaco_editor(
        value="# YAML config here",
        language="yaml",
        height="400px"
    )

with tab3:
    # Workflow canvas
    workflow_canvas()
```

### 1.4 Workflow Canvas (n8n/Node-RED Style)

For a Node-RED/n8n style node-editor, integrate a third-party JS library:

#### React Flow Integration

```python
from streamlit_elements import elements, sync
import streamlit_react_flow as srf

def workflow_canvas():
    """Create a node-based workflow editor"""
    
    # Define initial nodes
    initial_nodes = [
        {
            "id": "1",
            "type": "input",
            "data": {"label": "Start"},
            "position": {"x": 100, "y": 100}
        },
        {
            "id": "2", 
            "type": "default",
            "data": {"label": "Process"},
            "position": {"x": 300, "y": 100}
        }
    ]
    
    # Create React Flow component
    srf.react_flow(
        nodes=initial_nodes,
        edges=[],
        height=400,
        key="workflow_editor"
    )
```

### 1.5 Chat Interface Pane

Streamlit's built-in chat elements make LLM integration straightforward:

```python
def chat_interface():
    """Create LLM chat interface"""
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your PLC system..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt
        })
        
        # Get LLM response
        response = call_llm_api(prompt)
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
        
        st.rerun()
```

### 1.6 User Authentication & Sessions

Implement secure authentication using **streamlit-authenticator**:

```python
import streamlit_authenticator as stauth

def setup_authentication():
    """Configure user authentication"""
    
    # User credentials (in production, use database)
    names = ['John Doe', 'Jane Smith']
    usernames = ['jdoe', 'jsmith']
    passwords = ['secure123', 'secure456']
    
    # Hash passwords
    hashed_passwords = stauth.Hasher(passwords).generate()
    
    # Create authenticator
    authenticator = stauth.Authenticate(
        names,
        usernames, 
        hashed_passwords,
        'cookie_name',
        'signature_key',
        cookie_expiry_days=30
    )
    
    return authenticator

def main():
    authenticator = setup_authentication()
    
    name, authentication_status, username = authenticator.login(
        'Login', 
        'main'
    )
    
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*')
        
        # Main application interface
        render_ide_interface()
        
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
```

### 1.7 Code Organization

Structure the UI code in the `/plc-gbt/ui` directory:

```
/plc-gbt/ui/
├── app.py                 # Main Streamlit application
├── pages/                 # Multipage app structure
│   ├── dashboard.py       # Main dashboard
│   ├── editor.py          # Code editor page
│   ├── workflows.py       # Workflow builder
│   └── settings.py        # Configuration
├── components/            # Reusable UI components
│   ├── file_browser.py    # File explorer component
│   ├── chat.py           # Chat interface
│   ├── editor.py         # Code editor wrapper
│   └── workflow.py       # Workflow canvas
├── auth/                  # Authentication logic
│   └── authenticator.py   # User authentication
├── utils/                 # Utility functions
│   ├── api_client.py     # REST API integration
│   └── session.py        # Session management
└── requirements.txt       # UI dependencies
```

### 1.8 Limitations and Considerations

**Streamlit Strengths:**
- ✅ Rapid Python development
- ✅ Built-in session management
- ✅ Easy API integration
- ✅ Community components available

**Streamlit Limitations:**
- ❌ Layout constraints (not true multi-pane)
- ❌ Limited drag-and-drop capabilities
- ❌ Performance with complex UIs
- ❌ Refresh-based interaction model

---

## 2. Open-Source Design References & Frameworks

If Streamlit proves too limiting, consider these JavaScript/web-based alternatives.

### 2.1 VS Code-Style IDE Frameworks

#### Eclipse Theia
**Theia** is an open-source framework for building VS Code-like applications:

- **Features:**
  - Web-based and extensible
  - Reuses Monaco editor
  - Dockable panel layout
  - Top menus, sidebar, tabbed panels
  - VS Code extension support

- **Use Case:**
  - Full "IDE shell" for custom features
  - Custom panels for PLC workflows
  - Integrated chat pane for LLM

- **Trade-offs:**
  - Requires TypeScript/JavaScript development
  - More complex than Streamlit
  - Better for complex IDE requirements

**Reference:** [Theia IDE Platform](https://theia-ide.org/)

### 2.2 Browser-Based Workflow Editors

#### Node-RED
**Node-RED** provides an excellent reference for multi-pane workflow layouts:

**Layout Structure:**
- **Top menu bar** - Deploy, settings, etc.
- **Left sidebar** - Node palette
- **Main canvas** - Flow editor
- **Right sidebar** - Node details/debug

**Key Features:**
- Browser-based editor
- Multi-user support (with security)
- Drag-and-drop interface
- Real-time execution feedback

**Reference:** [Node-RED Flow Editor](https://sourceforge.net/projects/node-red-low-code.mirror/)

#### n8n Workflow Automation
**n8n** offers a modern workflow editor interface:

**Features:**
- Intuitive drag-and-drop interface
- Modern, clean design
- Role-based access control
- Self-hostable and open-source

**UI Components:**
- Node menu (left sidebar)
- Central workflow canvas
- Execution log/inspector (right sidebar)
- Top navigation bar

**Reference:** [n8n Workflow Automation](https://www.infralovers.com/blog/2025-05-09-n8n-workflow-automation/)

### 2.3 Code Editor Components

#### Monaco Editor
For custom JS/HTML front-ends, **Monaco Editor** provides VS Code's editing experience:

```javascript
// Initialize Monaco Editor
import * as monaco from 'monaco-editor';

const editor = monaco.editor.create(document.getElementById('container'), {
    value: '# PLC-GBT Python Code',
    language: 'python',
    theme: 'vs-dark',
    automaticLayout: true
});

// Support for multiple tabs
const editors = new Map();

function createTab(filename, content, language) {
    const model = monaco.editor.createModel(content, language);
    editors.set(filename, model);
    editor.setModel(model);
}
```

**Features:**
- Full VS Code editor functionality
- Syntax highlighting for 100+ languages
- IntelliSense and code completion
- Themes and customization
- MIT licensed

**Reference:** [Monaco Editor](https://microsoft.github.io/monaco-editor/)

### 2.4 Layout Managers

#### Golden Layout
**Golden Layout** provides VS Code-style resizable panes:

```javascript
import GoldenLayout from 'golden-layout';

const config = {
    content: [{
        type: 'row',
        content: [{
            type: 'component',
            componentName: 'fileExplorer',
            width: 20
        }, {
            type: 'stack',
            content: [{
                type: 'component',
                componentName: 'codeEditor',
                title: 'Editor'
            }, {
                type: 'component', 
                componentName: 'workflowCanvas',
                title: 'Workflow'
            }]
        }, {
            type: 'component',
            componentName: 'chatPanel',
            width: 25
        }]
    }]
};

const layout = new GoldenLayout(config);
```

**Features:**
- Drag, resize, and dock panels
- Complex nested layouts
- Persistent layout state
- Used by many IDE-style applications

**Reference:** [Golden Layout](https://golden-layout.github.io/golden-layout/)

### 2.5 React Component Libraries

#### Material-UI / Blueprint.js
For React-based solutions, leverage established UI kits:

**Material-UI Example:**
```jsx
import { 
    AppBar, Toolbar, Drawer, List, ListItem,
    Typography, Box, Tab, Tabs
} from '@mui/material';

function IDELayout() {
    return (
        <Box sx={{ display: 'flex' }}>
            <AppBar position="fixed">
                <Toolbar>
                    <Typography variant="h6">PLC-GBT</Typography>
                </Toolbar>
            </AppBar>
            
            <Drawer variant="permanent" sx={{ width: 240 }}>
                <FileExplorer />
            </Drawer>
            
            <Box component="main" sx={{ flexGrow: 1 }}>
                <TabPanel>
                    <MonacoEditor />
                </TabPanel>
            </Box>
            
            <Drawer variant="permanent" anchor="right" sx={{ width: 300 }}>
                <ChatInterface />
            </Drawer>
        </Box>
    );
}
```

**Blueprint.js** is specifically designed for complex developer tools and provides:
- Tree components for file explorers
- Code editor integration
- Dialog and overlay management
- Professional developer tool styling

### 2.6 Integration with Backend REST API

Regardless of UI framework, integration patterns remain consistent:

#### Streamlit Integration
```python
import requests
import streamlit as st

class PLCGBTClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_project_files(self):
        response = requests.get(
            f"{self.base_url}/api/projects/files",
            headers=self.headers
        )
        return response.json()
    
    def execute_plc_command(self, command):
        response = requests.post(
            f"{self.base_url}/api/plc/execute",
            json={"command": command},
            headers=self.headers
        )
        return response.json()

# Usage in Streamlit
@st.cache_data
def load_project_files():
    client = PLCGBTClient(st.secrets["api_url"], st.session_state.token)
    return client.get_project_files()
```

#### React Integration
```javascript
class PLCGBTClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async getProjectFiles() {
        const response = await fetch(`${this.baseUrl}/api/projects/files`, {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        });
        return response.json();
    }
    
    async executePLCCommand(command) {
        const response = await fetch(`${this.baseUrl}/api/plc/execute`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command })
        });
        return response.json();
    }
}

// Usage with React hooks
function useProjectFiles() {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const client = new PLCGBTClient(API_URL, authToken);
        
        client.getProjectFiles()
            .then(setFiles)
            .finally(() => setLoading(false));
    }, []);
    
    return { files, loading };
}
```

### 2.7 User Authentication & Roles

#### JWT Token-Based Authentication
```javascript
// Authentication context for React
const AuthContext = createContext();

function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    
    const login = async (username, password) => {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.token) {
            setToken(data.token);
            setUser(data.user);
            localStorage.setItem('token', data.token);
        }
    };
    
    return (
        <AuthContext.Provider value={{ user, token, login }}>
            {children}
        </AuthContext.Provider>
    );
}

// Role-based component rendering
function AdminPanel() {
    const { user } = useContext(AuthContext);
    
    if (user?.role !== 'admin') {
        return <div>Access denied</div>;
    }
    
    return <div>Admin controls...</div>;
}
```

### 2.8 Desktop App Alternative (Electron)

For a desktop-app experience, consider **Electron** or **Tauri**:

#### Electron Wrapper
```javascript
// main.js - Electron main process
const { app, BrowserWindow } = require('electron');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });
    
    // Load your React app or Streamlit server
    mainWindow.loadURL('http://localhost:3000');
}

app.whenReady().then(createWindow);
```

**Benefits:**
- Desktop-app feel (like VS Code)
- System integration (menu bar, system tray)
- Offline capabilities
- Native file system access

**Considerations:**
- Additional packaging complexity
- Larger distribution size
- May be overkill for web-based tool

---

## 3. Recommended Implementation Path

Given the preference for Python development, follow this progressive approach:

### Phase 1: Streamlit Prototype (Week 1-2)

#### 3.1 Basic Layout Implementation
```python
def main():
    st.set_page_config(
        page_title="PLC-GBT IDE",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Authentication
    if not authenticate_user():
        return
    
    # Sidebar: File Explorer
    with st.sidebar:
        st.header("Project Explorer")
        selected_file = file_browser_component()
    
    # Main area: Tabbed interface
    tab1, tab2, tab3 = st.tabs(["Code Editor", "Workflow", "Chat"])
    
    with tab1:
        code_editor_interface(selected_file)
    
    with tab2:
        workflow_canvas_interface()
    
    with tab3:
        chat_interface()

if __name__ == "__main__":
    main()
```

#### 3.2 Component Integration
1. **File Browser:** Implement `streamlit-file-browser`
2. **Code Editor:** Add `streamlit-monaco` or Streamlit Elements
3. **Chat Interface:** Use built-in `st.chat_input`/`st.chat_message`
4. **API Integration:** Connect to PLC-GBT REST API

#### 3.3 Authentication Setup
```python
import streamlit_authenticator as stauth

def setup_auth():
    # Configure with your backend auth system
    authenticator = stauth.Authenticate(
        # User data from your API
        get_user_credentials(),
        'plc_gbt_cookie',
        'secret_key',
        cookie_expiry_days=30
    )
    return authenticator
```

### Phase 2: Enhanced Streamlit (Week 3-4)

#### 3.4 Advanced Layout with Streamlit Elements
```python
from streamlit_elements import elements, mui, nivo, sync

def advanced_layout():
    with elements("advanced_ide"):
        # Material UI layout
        with mui.Box(sx={"display": "flex", "height": "100vh"}):
            # App bar
            with mui.AppBar(position="static"):
                create_menu_bar()
            
            # Main content with drawer
            with mui.Box(sx={"display": "flex", "flex": 1}):
                # Left drawer
                with mui.Drawer(variant="permanent"):
                    file_explorer_tree()
                
                # Center area with tabs
                with mui.Box(sx={"flex": 1}):
                    tabbed_editor_interface()
                
                # Right panel for chat
                with mui.Box(sx={"width": 300}):
                    llm_chat_panel()
```

#### 3.5 Workflow Canvas Integration
```python
def workflow_canvas():
    # Try React Flow integration via Streamlit Elements
    with elements("workflow"):
        # Custom React component for node editor
        create_node_editor_component()
```

### Phase 3: Testing & Refinement (Week 5-6)

#### 3.6 Multi-User Testing
1. Deploy Streamlit app on server
2. Test concurrent user sessions
3. Verify session isolation
4. Test API integration under load

#### 3.7 UI/UX Improvements
1. **Theming:** Apply dark theme for engineering users
2. **Custom CSS:** Inject styling for better IDE feel
3. **Keyboard shortcuts:** Add common IDE shortcuts
4. **Performance:** Optimize for large projects

#### 3.8 Feature Validation
- ✅ File operations (open, edit, save)
- ✅ PLC command execution
- ✅ Workflow creation and editing
- ✅ LLM chat integration
- ✅ User authentication and roles
- ✅ Multi-user support

### Phase 4: Evaluation & Decision Point (Week 7)

#### 3.9 Streamlit Assessment
Evaluate if Streamlit meets requirements:

**Success Criteria:**
- Responsive UI with acceptable performance
- All core features functional
- Good user experience for target audience
- Maintainable codebase

**If Successful:** Continue with Streamlit, add advanced features

**If Limited:** Proceed to React-based solution

### Phase 5: Alternative Implementation (Week 8-12, if needed)

#### 3.10 React-Based Solution
If Streamlit proves insufficient:

1. **Setup:** Create React app with TypeScript
2. **Layout:** Implement with Material-UI and Golden Layout
3. **Editor:** Integrate Monaco Editor
4. **Workflow:** Add React Flow for node editor
5. **Chat:** Build custom chat interface
6. **Auth:** Implement JWT-based authentication
7. **API:** Connect to existing REST endpoints

#### 3.11 Template Selection
Consider starting from existing templates:
- **VS Code clone projects** on GitHub
- **React dashboard templates** with sidebar layouts
- **Node-based editor templates** using React Flow

---

## 4. Technical References

### 4.1 Streamlit Components

| Component | Purpose | Repository |
|-----------|---------|------------|
| **streamlit-file-browser** | File explorer tree | [GitHub](https://github.com/pragmatic-streamlit/streamlit-file-browser) |
| **streamlit-elements** | React integration | [GitHub](https://github.com/okld/streamlit-elements) |
| **streamlit-monaco** | Code editor | [PyPI](https://pypi.org/project/streamlit-monaco/) |
| **streamlit-authenticator** | User authentication | [PyPI](https://pypi.org/project/streamlit-authenticator/) |

### 4.2 Open-Source References

| Project | Type | Purpose | URL |
|---------|------|---------|-----|
| **Eclipse Theia** | IDE Framework | VS Code-style platform | [theia-ide.org](https://theia-ide.org/) |
| **Node-RED** | Workflow Editor | Flow-based programming | [sourceforge.net](https://sourceforge.net/projects/node-red-low-code.mirror/) |
| **n8n** | Automation Platform | Modern workflow UI | [infralovers.com](https://www.infralovers.com/blog/2025-05-09-n8n-workflow-automation/) |
| **Monaco Editor** | Code Editor | VS Code editor component | [microsoft.github.io](https://microsoft.github.io/monaco-editor/) |
| **React Flow** | Node Editor | Diagram library | [reactflow.dev](https://reactflow.dev/) |
| **Golden Layout** | Layout Manager | Resizable panels | [golden-layout.github.io](https://golden-layout.github.io/golden-layout/) |

### 4.3 Documentation Links

#### Streamlit Resources
- **Chat Widgets:** [st.chat_input documentation](https://docs.streamlit.io/develop/api-reference/chat/st.chat_input)
- **Multipage Apps:** [Streamlit multipage guide](https://docs.streamlit.io/library/get-started/multipage-apps)
- **Custom Components:** [Component development guide](https://docs.streamlit.io/library/components)

#### React/JavaScript Resources
- **Material-UI:** [MUI component library](https://mui.com/)
- **Blueprint.js:** [Developer tool components](https://blueprintjs.com/)
- **React Router:** [Client-side routing](https://reactrouter.com/)

### 4.4 Architecture Considerations

#### Performance Factors
- **Streamlit:** Server-side rendering, session-based
- **React:** Client-side rendering, more responsive
- **Hybrid:** Streamlit + embedded React components

#### Deployment Options
- **Local:** Single-user development
- **Server:** Multi-user production
- **Cloud:** Scalable deployment
- **Desktop:** Electron wrapper

#### Security Considerations
- **Authentication:** JWT tokens vs. session cookies
- **Authorization:** Role-based access control
- **API Security:** Secure REST endpoint integration
- **Data Protection:** Secure handling of PLC data

---

## Summary

This document provides a comprehensive approach to building a VS Code-style interface for PLC-GBT:

### Recommended Approach
1. **Start with Streamlit** for rapid Python development
2. **Enhance with components** (Elements, Monaco, file browser)
3. **Evaluate performance** and user experience
4. **Migrate to React** if Streamlit proves limiting

### Key Success Factors
- **Progressive enhancement:** Start simple, add complexity as needed
- **Component reuse:** Leverage existing open-source solutions
- **User feedback:** Early testing with target users
- **API-first design:** Maintain separation between UI and backend

### Timeline Estimate
- **Streamlit MVP:** 2-4 weeks
- **Enhanced version:** 4-6 weeks
- **React alternative:** 8-12 weeks (if needed)

The approach balances rapid development (Python/Streamlit) with the flexibility to create a more sophisticated interface (React) if requirements demand it.