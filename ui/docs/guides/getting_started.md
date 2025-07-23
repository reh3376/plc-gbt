# Getting Started with Phase 31 Development

> **Phase 31**: Unified Web-Based IDE & User Interface  
> **Framework**: Eclipse Theia + PLC-GBT Extensions  
> **Target Audience**: Developers, Engineers, Contributors  

## 🎯 **Overview**

This guide will walk you through setting up your development environment for Phase 31 of the PLC-GBT project. By the end of this guide, you'll have a fully functional Theia-based IDE development environment with all necessary tools and dependencies.

## 📋 **Prerequisites**

### **System Requirements**
- **Operating System**: macOS, Linux, or Windows 10+ with WSL2
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: At least 10GB free space
- **Network**: Stable internet connection for package downloads

### **Software Dependencies**
- **Node.js**: 18.0.0 or higher
- **npm**: 8.0.0 or higher (or Yarn 1.22.0+)
- **Python**: 3.11+ (for backend integration)
- **Git**: Latest version
- **Docker**: Latest version (for containerized development)
- **VS Code**: Recommended IDE for development

### **Verification Commands**
```bash
# Check versions
node --version     # Should be 18.0.0+
npm --version      # Should be 8.0.0+
python3 --version  # Should be 3.11+
git --version      # Any recent version
docker --version   # Any recent version
```

## 🚀 **Quick Setup**

### **Step 1: Clone and Navigate**
```bash
# Navigate to PLC-GBT repository
cd /path/to/plc-gbt

# Navigate to UI directory
cd ui
```

### **Step 2: Install Dependencies**
```bash
# Install main dependencies
npm install

# Or using Yarn
yarn install

# Install Theia CLI globally
npm install -g @theia/cli
```

### **Step 3: Build and Start Development Server**
```bash
# Build the application
npm run build

# Start development server
npm run start:dev
```

### **Step 4: Access the IDE**
Open your browser and navigate to:
- **Development**: http://localhost:3001
- **Production**: http://localhost:3000

## 🏗️ **Development Environment Setup**

### **Development with Docker (Recommended)**

```bash
# Build development container
docker build -f build/docker/Dockerfile.development -t plc-gbt-theia-dev .

# Run development container
docker run -it \
  -p 3001:3001 \
  -p 8000:8000 \
  -v $(pwd):/app \
  -v /app/node_modules \
  plc-gbt-theia-dev
```

### **Local Development (Alternative)**

```bash
# Install dependencies
npm install

# Start in watch mode for development
npm run watch

# In another terminal, start the application
npm run start:dev
```

## 🔧 **Project Structure Overview**

```
ui/
├── README.md                                    # Main documentation
├── package.json                                 # Main package configuration
├── tsconfig.json                                # TypeScript configuration
├── docs/                                        # Documentation
│   ├── architecture/                            # Technical specifications
│   ├── guides/                                  # Development guides
│   └── api/                                     # API documentation
├── theia/                                       # Theia application
│   ├── workbench/                               # Main Theia app
│   ├── extensions/                              # Custom extensions
│   ├── themes/                                  # UI themes
│   └── language-servers/                       # PLC language support
├── config/                                      # Configuration files
│   ├── development/                             # Dev environment
│   └── production/                              # Prod environment
├── build/                                       # Build configuration
│   ├── webpack/                                 # Webpack configs
│   ├── docker/                                  # Docker files
│   └── scripts/                                 # Build scripts
├── assets/                                      # Static assets
├── tests/                                       # Test suites
└── examples/                                    # Examples and tutorials
```

## 🔌 **Extension Development**

### **Creating a New Extension**

```bash
# Navigate to extensions directory
cd theia/extensions

# Create new extension (example: my-extension)
mkdir my-extension
cd my-extension

# Initialize extension package
npm init -y

# Install Theia dependencies
npm install @theia/core @theia/filesystem
npm install -D @theia/cli typescript
```

### **Extension Package Structure**
```
my-extension/
├── package.json                     # Extension manifest
├── tsconfig.json                    # TypeScript config
├── src/
│   ├── browser/                     # Frontend code
│   │   ├── my-extension-frontend-module.ts
│   │   ├── my-extension-contribution.ts
│   │   └── my-extension-widget.tsx
│   ├── common/                      # Shared interfaces
│   │   ├── protocol.ts
│   │   └── types.ts
│   └── node/                        # Backend code
│       ├── my-extension-backend-module.ts
│       └── my-extension-service.ts
└── README.md                        # Extension documentation
```

### **Basic Extension Template**

```typescript
// src/browser/my-extension-contribution.ts
import { injectable } from '@theia/core/shared/inversify';
import { Command, CommandContribution, CommandRegistry } from '@theia/core/lib/common/command';
import { MenuContribution, MenuModelRegistry } from '@theia/core/lib/common/menu';

const MY_COMMAND: Command = {
  id: 'my-extension.command',
  label: 'My Extension Command'
};

@injectable()
export class MyExtensionContribution implements CommandContribution, MenuContribution {
  
  registerCommands(registry: CommandRegistry): void {
    registry.registerCommand(MY_COMMAND, {
      execute: () => {
        console.log('My extension command executed!');
      }
    });
  }
  
  registerMenus(menus: MenuModelRegistry): void {
    menus.registerMenuAction(CommonMenus.EDIT, {
      commandId: MY_COMMAND.id,
      label: MY_COMMAND.label
    });
  }
}
```

## 🔗 **Backend Integration**

### **API Configuration**
The IDE connects to the PLC-GBT backend through configuration files:

```javascript
// config/development/backend-integration.json
{
  "backend": {
    "baseUrl": "http://localhost:8000",
    "apiVersion": "v1"
  },
  "websocket": {
    "url": "ws://localhost:8000/ws"
  }
}
```

### **Using Backend Services**
```typescript
// Example: Using the Control Loop API
import { inject, injectable } from '@theia/core/shared/inversify';
import { PLCGBTBackendService } from '@plc-gbt/services';

@injectable()
export class ControlLoopManager {
  
  constructor(
    @inject(PLCGBTBackendService) private backend: PLCGBTBackendService
  ) {}
  
  async getControlLoops(): Promise<ControlLoop[]> {
    return this.backend.getControlLoops();
  }
}
```

## 🧪 **Testing**

### **Running Tests**
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=my-extension
```

### **Writing Tests**
```typescript
// src/browser/__tests__/my-extension.test.ts
import { expect } from 'chai';
import { MyExtensionContribution } from '../my-extension-contribution';

describe('MyExtensionContribution', () => {
  let contribution: MyExtensionContribution;
  
  beforeEach(() => {
    contribution = new MyExtensionContribution();
  });
  
  it('should register commands', () => {
    const registry = {
      registerCommand: sinon.spy()
    };
    
    contribution.registerCommands(registry as any);
    
    expect(registry.registerCommand.calledOnce).to.be.true;
  });
});
```

## 🎨 **Styling and Themes**

### **Custom Themes**
```css
/* assets/themes/plc-gbt-dark.css */
.theia-workbench {
  --theia-ui-font-family: 'Roboto', sans-serif;
  --theia-brand-color: #0066cc;
  --theia-accent-color: #ff6b35;
}

.plc-control-panel {
  background: var(--theia-layout-color2);
  border: 1px solid var(--theia-border-color1);
}
```

### **Component Styling**
```typescript
// React component with CSS modules
import styles from './MyComponent.module.css';

export const MyComponent: React.FC = () => (
  <div className={styles.container}>
    <h1 className={styles.title}>PLC-GBT Extension</h1>
  </div>
);
```

## 🔧 **Development Workflow**

### **Daily Development Cycle**

1. **Start Development Environment**
   ```bash
   npm run start:dev
   ```

2. **Make Changes to Extensions**
   - Edit TypeScript/React files
   - Add new features or fix bugs
   - Update tests as needed

3. **Test Changes**
   ```bash
   npm test
   npm run lint
   ```

4. **Build and Verify**
   ```bash
   npm run build
   # Test in browser at localhost:3001
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new PLC validation feature"
   git push origin feature/my-feature
   ```

### **Code Quality Checks**
```bash
# Linting
npm run lint
npm run lint:fix

# Type checking
npx tsc --noEmit

# Formatting
npm run format
npm run format:check
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Node Version Issues**
```bash
# Install Node Version Manager
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install and use Node 18
nvm install 18
nvm use 18
```

#### **Port Already in Use**
```bash
# Kill process on port 3001
lsof -ti:3001 | xargs kill -9

# Or use different port
npm run start:dev -- --port 3002
```

#### **Dependencies Issues**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### **Docker Issues**
```bash
# Rebuild container
docker build --no-cache -f build/docker/Dockerfile.development -t plc-gbt-theia-dev .

# Check container logs
docker logs <container_id>
```

### **Getting Help**

- **Documentation**: Check `docs/` directory
- **Issues**: Create GitHub issue with detailed description
- **Discussions**: Join team discussions on project repository
- **Architecture**: Review `docs/architecture/THEIA_ARCHITECTURE_SPECIFICATION.md`

## 🎯 **Next Steps**

1. **Explore Existing Extensions**: Review the extension code in `theia/extensions/`
2. **Read Architecture Guide**: Study the technical architecture document
3. **Start with Simple Extension**: Create a "Hello World" extension following the template
4. **Join Development**: Contribute to ongoing Phase 31 development
5. **Test Backend Integration**: Ensure API connections work with your local backend

## 🤝 **Contributing**

- Follow the [AI Task Orchestrator methodology](../../../docs/AI_TASK_ORCHESTRATOR_GUIDE.md)
- Ensure all code follows TypeScript best practices
- Maintain 80%+ test coverage
- Update documentation for new features
- Follow industrial safety compliance guidelines

---

**Happy Coding!** 🚀  

Welcome to Phase 31 development. You're now ready to build the future of industrial automation interfaces with PLC-GBT! 