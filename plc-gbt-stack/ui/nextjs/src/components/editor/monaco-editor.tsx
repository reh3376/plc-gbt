'use client'

import { useEffect, useRef } from 'react'
import Editor from '@monaco-editor/react'
import type { editor } from 'monaco-editor'
import { PLCLanguages } from '@/lib/utils/plc-languages'
import { useFileStore } from '@/lib/stores/file-store'

interface MonacoEditorProps {
  fileId?: string
  value?: string
  onChange?: (value: string) => void
  language?: string
  readOnly?: boolean
  height?: string | number
}

export function MonacoEditor({ 
  fileId, 
  value = '', 
  onChange, 
  language = 'json',
  readOnly = false,
  height = '100%'
}: MonacoEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)

  const { markFileAsModified, findFileById } = useFileStore()

  const file = fileId ? findFileById(fileId) : null

  // Determine language based on file extension
  const getLanguageFromFile = (fileName: string): string => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'json': return 'json'
      case 'st':
      case 'txt': return 'st' // Structured Text
      case 'ld': return 'xml' // Ladder Logic (as XML)
      case 'fbd': return 'xml' // Function Block (as XML)
      case 'acd':
      case 'l5x': return 'xml' // PLC files are typically XML-based
      default: return 'plaintext'
    }
  }

  const actualLanguage = file ? getLanguageFromFile(file.name) : language

  // Register PLC languages with Monaco
  useEffect(() => {
    if (typeof window !== 'undefined') {
      import('monaco-editor').then((monaco) => {
        // Register Structured Text language
        if (!monaco.languages.getLanguages().find(lang => lang.id === 'st')) {
          monaco.languages.register({ id: 'st' })
          monaco.languages.setMonarchTokensProvider('st', PLCLanguages.structuredText.monarchLanguage)
          monaco.languages.setLanguageConfiguration('st', PLCLanguages.structuredText.configuration)
        }

        // Define custom theme for PLC languages
        monaco.editor.defineTheme('plc-dark', {
          base: 'vs-dark',
          inherit: true,
          rules: [
            { token: 'keyword', foreground: '569cd6', fontStyle: 'bold' },
            { token: 'identifier', foreground: 'cccccc' },
            { token: 'type.identifier', foreground: '4ec9b0' },
            { token: 'number', foreground: 'b5cea8' },
            { token: 'number.hex', foreground: 'b5cea8' },
            { token: 'number.float', foreground: 'b5cea8' },
            { token: 'string', foreground: 'ce9178' },
            { token: 'comment', foreground: '6a9955' },
            { token: 'operator', foreground: 'd4d4d4' },
          ],
          colors: {
            'editor.background': '#1e1e1e',
            'editor.foreground': '#cccccc',
            'editor.lineHighlightBackground': '#2a2d2e',
            'editor.selectionBackground': '#3c3c3c',
            'editor.inactiveSelectionBackground': '#3c3c3c',
            'editorCursor.foreground': '#aeafad',
            'editorWhitespace.foreground': '#404040',
            'editorIndentGuide.background': '#404040',
            'editorIndentGuide.activeBackground': '#707070',
          }
        })
      })
    }
  }, [])

  // Handle editor initialization
  const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor, monaco: typeof import('monaco-editor')) => {
    editorRef.current = editor
    
    // Set custom theme
    monaco.editor.setTheme('plc-dark')
    
    // Configure editor options
    editor.updateOptions({
      minimap: { enabled: true },
      fontSize: 14,
      lineNumbers: 'on',
      renderWhitespace: 'boundary',
      wordWrap: 'on',
      automaticLayout: true,
      scrollBeyondLastLine: false,
      folding: true,
      foldingStrategy: 'indentation',
      showFoldingControls: 'always',
      contextmenu: true,
      parameterHints: { enabled: true },
      quickSuggestions: { other: true, comments: true, strings: true },
      suggestOnTriggerCharacters: true,
      acceptSuggestionOnEnter: 'on',
      tabCompletion: 'on',
      snippetSuggestions: 'top',
      formatOnPaste: true,
      formatOnType: true,
    })

    // Add PLC-specific completions for Structured Text
    if (actualLanguage === 'st') {
      monaco.languages.registerCompletionItemProvider('st', {
        provideCompletionItems: (model, position) => {
          const word = model.getWordUntilPosition(position)
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn
          }

          const suggestions = [
            // PLC Functions
            {
              label: 'TON',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: 'TON(${1:Timer}, ${2:PT:=T#5s});',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Timer On Delay - Delays the true signal by a specified time',
              range: range
            },
            {
              label: 'TOF',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: 'TOF(${1:Timer}, ${2:PT:=T#5s});',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Timer Off Delay - Delays the false signal by a specified time',
              range: range
            },
            {
              label: 'PID',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: 'PID(${1:PID_Instance}, ${2:SetPoint}, ${3:ProcessValue});',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'PID Controller - Proportional, Integral, Derivative control',
              range: range
            }
          ]

          return { suggestions }
        }
      })
    }
  }

  const handleEditorChange = (newValue: string | undefined) => {
    if (newValue !== undefined) {
      onChange?.(newValue)
      
      // Mark file as modified if content has changed
      if (fileId && file && newValue !== value) {
        markFileAsModified(fileId, true)
      }
    }
  }

  // Get the appropriate file content
  const editorValue = value || (file ? 'Loading...' : '// Welcome to PLC-GBT IDE\n// Select a file from the explorer to start editing')

  return (
    <div className="h-full w-full">
      <Editor
        height={height}
        defaultLanguage="json"
        language={actualLanguage}
        value={editorValue}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          theme: 'vs-dark',
          automaticLayout: true,
          contextmenu: !readOnly,
          selectOnLineNumbers: true,
          roundedSelection: false,
          cursorStyle: 'line',
          fontFamily: 'Consolas, "Courier New", monospace',
          fontSize: 14,
          lineHeight: 21,
          letterSpacing: 0.5,
        }}
        loading={
          <div className="h-full w-full flex items-center justify-center bg-[#1e1e1e] text-[#cccccc]">
            <div className="text-center">
              <div className="animate-spin w-8 h-8 border-2 border-[#007acc] border-t-transparent rounded-full mx-auto mb-4"></div>
              <div>Loading Monaco Editor...</div>
            </div>
          </div>
        }
      />
    </div>
  )
} 