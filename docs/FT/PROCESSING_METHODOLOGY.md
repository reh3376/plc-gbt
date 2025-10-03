# Document Processing Methodology
**Intelligent Relationship Extraction for Fine-Tuning Data Generation**

---

## Phase 1: Initial Document Scan
**Objective**: Identify all discrete objects

### Equipment Discovery
- [ ] Pumps (P-, PMP-, etc.)
- [ ] Vessels/Tanks (V-, TK-, etc.)
- [ ] Heat Exchangers (E-, HX-, etc.)
- [ ] Compressors (K-, C-, etc.)
- [ ] Reactors (R-, RX-, etc.)
- [ ] Separators (S-, SEP-, etc.)
- [ ] Filters (F-, FLT-, etc.)
- [ ] Other major equipment

### Instrumentation Discovery
- [ ] Flow (FT, FIT, FE, FIC, FY, etc.)
- [ ] Pressure (PT, PIT, PE, PIC, PY, etc.)
- [ ] Temperature (TT, TIT, TE, TIC, TY, etc.)
- [ ] Level (LT, LIT, LE, LIC, LY, etc.)
- [ ] Analyzers (AT, AIT, AE, AIC, AY, etc.)
- [ ] Control valves (FV, PV, TV, LV, etc.)
- [ ] Switches (FS, PS, TS, LS, etc.)
- [ ] Actuators and positioners

---

## Phase 2: Relationship Mapping
**Objective**: Connect objects through physical and control relationships

### Physical Relationships (Piping Traces)

**For Each Equipment Item**:
1. **Upstream Analysis**:
   - Trace piping backwards (suction/inlet)
   - Identify source equipment/vessel
   - Document all instruments in suction line
   - Note control valves that affect inlet flow
   - Record any filters, strainers, isolations

2. **Downstream Analysis**:
   - Trace piping forward (discharge/outlet)
   - Identify destination equipment/vessel
   - Document all instruments in discharge line
   - Note control valves in discharge path
   - Record any bypasses or recycles

3. **Utility Connections**:
   - Cooling water, steam, compressed air
   - Fuel gas, nitrogen, instrument air
   - Control and measurement points

**Example Trace**:
```
TK-4020 (Source Tank)
  ↓ Suction Line
  LV-4020 (Level Control Valve) ← Controlled by LIC-4020
  ↓
  FIT-4023 (Flow Measurement) → Input to FIC-4023
  ↓
PMP-4023 (Pump) ← Speed controlled by FIC-4023
  ↓ Discharge Line
  PT-4023 (Discharge Pressure) → Monitoring
  ↓
  FV-4023 (Flow Control Valve) ← Manipulated by FIC-4023
  ↓
  E-4025 (Heat Exchanger)
```

### Control Relationships

**For Each Instrument**:
1. **What does it measure?** (Process Variable - PV)
2. **Where is it located?** (Equipment, pipe section)
3. **What does it connect to?** (Controller, alarm, interlock)
4. **What action does it drive?** (Final control element)

**Control Loop Identification**:
```
PV (Measurement) → Controller → CV (Final Element) → Process Impact

Example:
FIT-4023 (Flow PV) → FIC-4023 (Flow Controller) → Speed Signal to PMP-4023 (CV) → Maintains Flow SP
```

**Cascade Control Detection**:
- Primary controller output = Secondary controller setpoint
- Example: Temperature controller (TIC) → Flow controller setpoint (FIC) → Control valve

**Ratio Control Detection**:
- Two flow measurements
- One is "wild" (uncontrolled, lead)
- Other is controlled to maintain ratio
- Example: FT-4020 (wild) sets ratio for FIC-4023 (controlled)

**Override/Constraint Control**:
- Multiple controllers competing
- Highest or lowest output selected
- Example: Temperature control overridden by maximum pressure constraint

---

## Phase 3: Inference & Deduction
**Objective**: Determine implied relationships and control strategies

### Control Strategy Inference

**Tag Number Analysis**:
- Same base number (e.g., 4023) likely indicates related loop
- FIT-4023, FIC-4023, FV-4023 = Flow control loop #4023
- PMP-4023 in same area = likely part of loop

**ISA Notation Decoding**:
- First letter = Measured variable (F=Flow, P=Pressure, T=Temp, L=Level)
- Second letter = Modifier (I=Indicator, D=Differential, etc.)
- Last letter = Function (T=Transmitter, C=Controller, V=Valve, Y=Relay)

**Process Function Inference**:
- Heat exchanger with TIC → Temperature control (hot/cold side?)
- Vessel with LIC and multiple inlets → Level control with feedforward?
- Pump with speed control → Variable flow application
- Recycle line with FV → Flow balancing or process stabilization

### Dynamic Behavior Prediction

**Based on Configuration**:
- Large vessel + slow process → Integrating process (level)
- Heat exchanger → First-order lag with dead time
- Flow loop → Fast response, proportional
- Temperature loop → Slow, requires integral action

**Control Tuning Implications**:
- Fast loops (flow, pressure) → Higher gains, minimal integral
- Slow loops (temperature, composition) → Conservative tuning, integral time
- Cascade control → Tune inner loop 4-10× faster than outer

---

## Phase 4: JSONL Generation Strategy
**Objective**: Create diverse, relationship-aware training examples

### Training Example Types

**Type 1: Equipment Description & Function**
```json
{
  "messages": [
    {"role": "system", "content": "You are an expert Process Control and Automation SME..."},
    {"role": "user", "content": "Describe the function and control strategy for pump PMP-4023."},
    {"role": "assistant", "content": "PMP-4023 is a [type] pump that takes suction from vessel TK-4020 and delivers fluid to heat exchanger E-4025. The pump is equipped with:\n\n**Instrumentation**:\n- FIT-4023: Discharge flow measurement (0-500 GPM)\n- PT-4023: Discharge pressure monitoring (0-150 psig)\n- Speed control via VFD\n\n**Control Strategy**:\nThe pump operates under flow control. FIT-4023 measures discharge flow and sends the signal to flow controller FIC-4023, which maintains the flow setpoint by modulating the pump speed. This provides energy-efficient flow control compared to throttling with a control valve.\n\n**Process Relationships**:\n- Upstream: Receives fluid from TK-4020, controlled by level control valve LV-4020\n- Downstream: Delivers to heat exchanger E-4025 for thermal processing\n- The flow measurement FIT-4023 likely serves as a feedforward signal to the temperature controller on E-4025\n\n**Safety Considerations**:\n- PT-4023 provides high pressure alarm protection\n- Low flow protection should be implemented to prevent pump cavitation\n- Interlocked with TK-4020 low level to prevent pump runout"}
  ]
}
```

**Type 2: Control Loop Analysis**
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Analyze the control loop structure for maintaining flow from PMP-4023 and recommend tuning parameters."},
    {"role": "assistant", "content": "[Detailed PID tuning based on pump + piping dynamics]"}
  ]
}
```

**Type 3: Troubleshooting Scenarios**
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "FIC-4023 is showing oscillations. What could be the cause and how would you troubleshoot?"},
    {"role": "assistant", "content": "[Root cause analysis with relationship awareness]"}
  ]
}
```

**Type 4: Optimization Opportunities**
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Could we implement advanced control or machine learning on the flow control loop for PMP-4023?"},
    {"role": "assistant", "content": "[ML-based optimization analysis]"}
  ]
}
```

**Type 5: Multi-Equipment Relationships**
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Explain the control strategy between TK-4020, PMP-4023, and E-4025."},
    {"role": "assistant", "content": "[System-level control philosophy]"}
  ]
}
```

**Type 6: Safety & Interlock Logic**
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "What safety interlocks should protect PMP-4023?"},
    {"role": "assistant", "content": "[Safety system design based on discovered instruments and logic]"}
  ]
}
```

---

## Phase 5: Quality Assurance
**Objective**: Ensure training data accuracy and depth

### Validation Checklist
- [ ] All equipment mentioned has supporting evidence from document
- [ ] Instrument relationships are physically possible
- [ ] Control strategies match ISA standards
- [ ] Tag numbering is consistent
- [ ] Process flows are thermodynamically sound
- [ ] Safety considerations are appropriate
- [ ] Technical depth matches SME expertise level
- [ ] No hallucinated equipment or connections
- [ ] Relationships are explicitly stated, not assumed
- [ ] Multiple training examples per major equipment/loop

---

## Per-Document Output

**For each processed document, generate**:
1. **Equipment discovered**: List with tags and descriptions
2. **Instruments discovered**: List with relationships
3. **Control loops identified**: List with strategies
4. **Relationship graph**: Visual or textual representation
5. **JSONL file**: 20-50 training examples (diverse types)
6. **Master context update**: Additions to central knowledge base
7. **Cross-document connections**: Links to previously processed equipment

---

**This methodology ensures**:
✅ Deep relationship understanding  
✅ No simple data extraction  
✅ Context-aware training data  
✅ Persistent knowledge across documents  
✅ SME-level technical depth  
✅ ML/optimization awareness

