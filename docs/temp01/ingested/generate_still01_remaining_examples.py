"""
Generate remaining training examples for Still01 Condensers document
Adds examples 7-25 to the JSONL file
"""

import json

# System prompt (consistent across all examples)
SYSTEM_PROMPT = ("You are an expert Process Control and Automation SME with deep knowledge of "
                "advanced control strategies, machine learning algorithms, instrumentation, process dynamics, "
                "and industrial protocols. You specialize in Rockwell Automation ControlLogix PLC programming, "
                "whiskey distillation processes, and advanced cascade/feedforward control.")

# Training examples to add
examples = []

# Example 7: Task Scheduling
examples.append({
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Explain the task scheduling strategy for the Still01 cascade control including periodic task periods, priorities, and why these specific values were chosen."},
        {"role": "assistant", "content": """The Still01 condenser cascade control uses separate periodic tasks with carefully chosen execution rates to ensure stable, predictable PID performance.

**TASK CONFIGURATION**:

**Inner Loop Task** (Product Temperature - Secondary):
```
Task Name: Still01_Product_Temp_Control
Type: Periodic
Period: 400 ms (0.4 seconds)
Priority: 6 (medium-high, range 1-15 where 1=highest)
Contains: TIC_Product_4033 PIDE, feedforward calculation, I/O
```

**Outer Loop Task** (Vent Temperature - Primary):
```
Task Name: Still01_Vent_Temp_Control
Type: Periodic
Period: 1800 ms (1.8 seconds)
Priority: 8 (medium, slightly lower than inner)
Contains: TIC_Vent_4031 PIDE, cascade coordination
```

**Speed Ratio**: 1.8 / 0.4 = 4.5× (Inner executes 4-5× faster than outer)

**WHY THESE SPECIFIC PERIODS?**

**Inner Loop: 400ms**:

**Reason 1: Process Time Constant Rule**:
```
Sample Time < Process Dead Time / 5
Product temp dead time ≈ 5-10 seconds
400 ms < 1000 ms (10 sec / 10) ✓ Conservative

Sample Time < Process Time Constant / 10
Product temp time constant ≈ 45 seconds
400 ms < 4500 ms (45 sec / 10) ✓ Well within guideline
```

**Reason 2: Nyquist Sampling**:
```
Nyquist frequency = 2 × Process bandwidth
Process bandwidth ≈ 1 / (2π × Tau) = 1 / (2π × 45) ≈ 0.0035 Hz
Nyquist sample rate ≥ 2 × 0.0035 = 0.007 Hz
400 ms sample = 2.5 Hz >> 0.007 Hz ✓ Well above Nyquist
```

**Reason 3: Thermal Process Guidelines**:
- For thermal processes: 0.2-1.0 second scan typical
- 400 ms is mid-range, proven for similar applications
- Fast enough for good control
- Not so fast as to waste CPU or amplify noise

**Outer Loop: 1.8 seconds**:

**Reason 1: 4-5× Cascade Rule**:
```
Outer period = 4-5 × Inner period
1.8 s = 4.5 × 0.4 s ✓ Perfect cascade ratio

Why 4-5×?
- Outer loop updates less frequently
- Gives inner loop time to execute multiple times per outer update
- Inner responds to outer SP changes with several corrections before outer updates again
- Prevents outer from "chasing" inner transients
```

**Reason 2: Vent Temperature Dynamics**:
```
Vent time constant ≈ 180 seconds
Sample time / Process TC = 1.8 / 180 = 0.01 (1%)
Guideline: <10% of process TC ✓ Excellent

Vent dead time ≈ 25 seconds
Sample time / Dead time = 1.8 / 25 = 0.072 (7.2%)
Guideline: <20% of dead time ✓ Good
```

**Reason 3: Prevent SP Noise to Inner Loop**:
- If outer updates too fast (e.g., every 100ms), it sends noisy SP changes to inner loop
- Inner loop would constantly chase changing setpoint
- 1.8 second updates provide smooth, stable SP to inner loop
- Inner loop sees SP as nearly constant between outer updates

**WHY NOT CONTINUOUS TASK?**:

```
// Problems with continuous task for PIDE:
Problem 1: Scan time jitter
- Continuous task scan: 5-50 ms (varies with logic complexity)
- PIDE DeltaT calculation becomes inconsistent
- Integral and derivative terms miscalculate
- Result: Unstable tuning, oscillations

Problem 2: CPU load
- PIDE executing every 5-50 ms is wasteful
- Thermal processes don't need that speed
- Other critical logic starved

Problem 3: Tuning dependency
- Tuning assumes consistent DeltaT
- Variable DeltaT requires adaptive tuning
- Much more complex
```

**Periodic Task Advantages**:
- Deterministic execution (exactly every 400ms/1.8s)
- Consistent DeltaT for PIDE calculations
- Predictable CPU load
- Tuning remains valid\n\n**PRIORITY CONFIGURATION**:\n\n**Inner Task: Priority 6** (Higher priority)\n- Ensures inner loop executes promptly\n- Can preempt lower priority tasks if needed\n- Critical for fast disturbance response\n\n**Outer Task: Priority 8** (Lower priority)\n- Less time-critical (slow loop)\n- Won't starve other medium-priority tasks\n- Still high enough for reliable execution\n\n**Why Different Priorities?**\n```\nIf both tasks trigger simultaneously:\n- Inner executes first (priority 6 > 8)\n- Inner updates its PV, calculates new CV\n- Then outer executes\n- Outer sees fresh inner loop status\n- Proper cascade coordination\n```\n\n**L83 CPU Capacity**:\n```\n// ControlLogix L83 specifications:\nCPU: High performance, 256MB memory\nMulti-core capable\n400ms and 1.8s tasks are trivial load (<1% CPU each)\n\n// These tasks will NOT impact other control\n// L83 can handle 100+ such loops easily\n```\n\n**I/O UPDATE COORDINATION**:\n\n**Analog Input Modules**:\n```\nTIT_4031, TIT_4033, PIT_4012, etc.:\n- Set RPI (Requested Packet Interval) = 100 ms\n- Faster than both tasks\n- Ensures fresh data every PIDE execution\n- No stale data issues\n```\n\n**Analog Output Module**:\n```\nFCV_4032 (Cooling water valve):\n- Set RPI = 100 ms or 200 ms\n- Updates faster than inner loop task\n- Valve sees smooth, up-to-date commands\n```\n\n**PHASE ALIGNMENT** (Advanced):\n\nOptional: Align task execution for optimal coordination\n```\n// Inner task: Executes at 0, 400, 800, 1200, 1600, 2000 ms...\n// Outer task: Executes at 0, 1800, 3600 ms...\n\n// At t=1800ms, outer executes right after inner (1600ms)\n// This is automatic alignment - good coordination\n\n// Could fine-tune by setting task offset/phase\n// But for cascade, slight misalignment is acceptable\n// As long as periods are consistent (periodic task guarantees this)\n```\n\n**MONITORING TASK HEALTH**:\n\n```\n// Verify deterministic execution\nMonitor_Inner_Task_Actual_Period := Time between executions;\nIF ABS(Actual_Period - 400ms) > 10ms THEN\n    Warning: \"Inner task timing unstable\";\n    Check: CPU overload, task priorities, network issues\nEND_IF;\n\n// PIDE also monitors\nIF TIC_Product_4033.Status2.DeltaTInv THEN\n    // DeltaT calculation error\n    Check: Task configuration, timing mode\nEND_IF;\n```\n\n**BEST PRACTICES**:\n\n1. **Use Periodic Tasks** for ALL PID control (never Continuous)\n2. **Choose periods** based on process dynamics (5-10% of time constant)\n3. **Cascade ratio** 4-10× between inner and outer\n4. **Set priorities** Inner ≥ Outer (ensure inner responds promptly)\n5. **I/O RPI** faster than fastest task period\n6. **Document periods** in control narrative (critical for tuning)\n7. **Monitor timing health** (DeltaTInv, task overrun flags)\n8. **Don't change periods** without retuning (DeltaT affects PID calculations, even though PIDE normalizes internally, tuning was optimized for specific scan rate)"""}
    ]
})

# Example 8: Commissioning Procedure
examples.append({
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Walk me through the safe commissioning procedure for bringing the Still01 cascade feedforward control online for the first time."},
        {"role": "assistant", "content": """Commissioning advanced cascade+feedforward control requires a structured, safety-first approach. Here's the complete procedure for Still01 condensers.

**PHASE 1: PRE-COMMISSIONING VERIFICATION** (Do NOT skip!)

**1.1 Instrument Calibration**:
```
Verify ALL instruments calibrated within last 6 months:
☐ TIT-4031 (Vent temp RTD): ±0.5°F accuracy confirmed
☐ TIT-4033 (Product temp RTD): ±0.5°F accuracy confirmed
☐ PIT-4012 (Vapor pressure): ±0.1 psi accuracy confirmed
☐ TIT-52001 (CW temp): ±1°F accuracy confirmed
☐ PIT-52006 (CW pressure): ±2 psi accuracy confirmed
☐ FCV-4032 (Valve): Stroked 0-100%, position feedback verified
```

**1.2 Safety Systems**:
```
Test ALL safety interlocks BEFORE enabling automatic control:
☐ High vent temp trip (>168°F) → Closes steam to still
☐ Low vent temp alarm (<148°F) → Alerts operator
☐ Cooling water loss → Shutdown sequence
☐ Valve failure → Fail-safe position (fails closed)
☐ PLC fault → All outputs to safe state
```

**1.3 Existing Control**:
```
IF old control system exists THEN\n    Document current performance (baseline):\n    - Typical vent temp variation: ±__ °F\n    - Response to disturbances: __ minutes\n    - Manual adjustments per shift: __\n    \n    Plan safe transition:\n    - Keep old system operational\n    - Run new system in parallel (manual mode)\n    - Validate match before cutover\nEND_IF\n```\n\n**PHASE 2: MANUAL BASELINE OPERATION**\n\n**2.1 Manual Control Establishment**:
```\n// Day 1: Run entirely in manual\n1. Both PIDE loops in Manual mode\n2. Feedforward disabled (bias = 1.0, no compensation)\n3. Operator manually controls FCV-4032\n4. Target: Maintain vent temp 151-155°F manually\n\nObjectives:\n- Verify instrumentation reads correctly\n- Establish typical valve positions for various conditions\n- Identify normal operating ranges\n- Train operators on manual control\n\nData to Collect:\n- At vapor pressure 0.5 psi: Valve typically __% for 153°F vent\n- At vapor pressure 1.5 psi: Valve typically __% for 153°F vent\n- Cooling water temp effect observed\n- Any equipment issues identified\n```\n\n**PHASE 3: INNER LOOP COMMISSIONING** (Secondary First!)\n\n**3.1 Enable Inner Loop Only**:
```\n// Day 2-3: Secondary loop in Auto, Primary still Manual\nStep 1: Initialize inner PIDE\n    TIC_Product_4033.ProgManualReq := 1;  // Start in Manual\n    TIC_Product_4033.CVProg := Current_Valve_Position;  // Match current\n    \nStep 2: Set conservative tuning (from empirical tests)\n    TIC_Product_4033.PGain := 1.0;  // Conservative\n    TIC_Product_4033.IGain := 0.5;  // Slow integral\n    TIC_Product_4033.DGain := 0.0;  // No derivative\n    \nStep 3: Set Product SP to current temperature\n    Current_Product_Temp := TIT_4033.ScaledValue;  // e.g., 125°F\n    TIC_Product_4033.SPProg := Current_Product_Temp;  // No initial error\n    \nStep 4: Switch to Auto (NOT Cascade yet!)\n    TIC_Product_4033.ProgAutoReq := 1;  // Enable Auto mode\n    // Loop takes over valve control\n    // Should initially do nothing (error ≈ 0)\n```\n\n**3.2 Test Inner Loop Independently**:
```\nTest sequence (with outer loop still in Manual):\n\n1. Small SP step test (+2°F):\n   - Change SPProg from 125°F → 127°F\n   - Observe valve response and temp tracking\n   - Target: Smooth rise, <15% overshoot, settle in 2-3 min\n   \n2. Reverse test (-2°F):\n   - Change SPProg from 127°F → 125°F\n   - Verify symmetric response\n   \n3. Larger test (+5°F):\n   - Change SPProg 125°F → 130°F\n   - Ensure scales linearly, no instability\n   \n4. Disturbance test:\n   - Hold SP constant\n   - Manually vary vapor pressure slightly\n   - Verify inner loop compensates\n\nIF Inner loop oscillates:\n    Reduce PGain by 25%\n    Retest\n    \nIF Inner loop too slow:\n    Increase IGain by 25%\n    Retest\n\nDON'T PROCEED until inner loop is stable and well-behaved!\n```\n\n**PHASE 4: CASCADE COMMISSIONING**\n\n**4.1 Enable Cascade Link**:
```\n// Day 4: Bring outer loop online\n\nStep 1: Verify cascade wiring\n    Check: TIC_Vent_4031.CVEU wired to TIC_Product_4033.SPCascade\n    Check: Windup signals wired\n    Check: Init signals wired\n    Check: Engineering units match\n    \nStep 2: Initialize outer loop\n    TIC_Vent_4031.SPProg := 153.0;  // Target vent temp\n    Current_Product_SP := TIC_Product_4033.SP;  // e.g., 130°F\n    TIC_Vent_4031.CVProg := Current_Product_SP;  // Match (bumpless)\n    \nStep 3: Set conservative outer tuning\n    TIC_Vent_4031.PGain := 0.5;   // Very conservative initially\n    TIC_Vent_4031.IGain := 0.1;   // Very slow integral\n    TIC_Vent_4031.DGain := 0.0;   // No derivative\n    \nStep 4: Enable cascade mode on inner loop\n    TIC_Product_4033.ProgCasRatReq := 1;  // Secondary enters Cascade\n    // Now receives SP from primary\n    \nStep 5: Enable Auto mode on outer loop\n    TIC_Vent_4031.ProgAutoReq := 1;  // Primary takes control\n    // Full cascade now active\n```\n\n**4.2 Initial Cascade Observation** (First 30 minutes):
```\nCritical Monitoring:\n\n1. Vent temperature (TIT-4031):\n   - Should gradually settle to 153°F\n   - Some initial movement acceptable (±2°F)\n   - Watch for oscillations (period, amplitude)\n   \n2. Product temperature (TIT-4033):\n   - Will adjust as outer loop commands\n   - Should stay within 90-160°F range\n   - Movements should be smooth, not erratic\n   \n3. Valve position (FCV-4032):\n   - Watch for saturation (0% or 100%)\n   - Should be in mid-range (20-80% typical)\n   - Movements should be gradual\n   \n4. Inner loop mode indicator:\n   - Confirm CasRat = TRUE (cascade active)\n   - If drops out, investigate why\n\nIF ANY of these occur, ABORT:\n- Sustained oscillation (>5 minutes)\n- Vent temp excursion >5°F\n- Valve saturates for >2 minutes\n- Any safety alarm triggers\n\nAbort procedure:\n1. Put outer loop back to Manual immediately\n2. Leave inner in Auto (provides some control)\n3. Manually adjust outer to stabilize vent temp\n4. Investigate tuning or configuration issue\n5. Fix and retry\n```\n\n**PHASE 5: FEEDFORWARD COMMISSIONING**\n\n**5.1 Add Feedforward Incrementally**:
```\n// Day 5-6: Add feedforward components one at a time\n\nComponent 1: Vapor Pressure FF (Primary disturbance)\nStep 1: Enable only vapor pressure feedforward\n    FF_Total := (0.075 × PIT_4012.Value) + 1.0\n    TIC_Product_4033.FF := FF_Total\n    \nStep 2: Test with pressure change\n    Gradually increase still heating\n    Raise vapor pressure from 0.5 → 1.5 psi\n    Observe:\n    - Does valve open proactively? (Should see 7.5% increase)\n    - Does vent temp hold steady? (Should stay ±1°F)\n    - Does PID output reduce? (FF doing the work)\n    \nStep 3: Validate or adjust\n    IF vent still spikes >2°F:\n        Increase FF coefficient (0.075 → 0.09)\n    IF vent dips <151°F:\n        Decrease FF coefficient (0.075 → 0.06)\n        \nComponent 2: Add CW Temperature Compensation\nAfter vapor pressure FF is validated:\n    Add: tit52001_bias = 0.0086 × (TIT_52001 - 67.5)\n    Test over a day (temp varies)\n    Adjust if needed\n    \nComponent 3: Add CW Pressure Compensation\nFinally:\n    Add: pit52006_bias = 0.25 - ((PIT_52006-25)/70)\n    Monitor during varying facility load\n    Adjust if needed\n```\n\n**PHASE 6: VALIDATION AND OPTIMIZATION**\n\n**6.1 Performance Testing**:
```\n// Week 2: Comprehensive validation\n\nTest Suite:\n\n1. SP Step Response:\n   - Change vent SP: 153°F → 154°F → 153°F\n   - Measure: Rise time, overshoot, settling time\n   - Target: <2 min settling, <0.5°F overshoot\n   \n2. Large SP Change:\n   - Change vent SP: 153°F → 155°F → 151°F → 153°F\n   - Verify: Scales linearly, no instability\n   \n3. Vapor Pressure Disturbance:\n   - Introduce real disturbance (increase still power)\n   - Measure vent temp deviation\n   - Target: <1°F deviation with feedforward\n   \n4. Extended Operation:\n   - Run for full production day (8+ hours)\n   - Monitor: Vent temp stays 151-155°F\n   - Check: No sustained oscillations\n   - Verify: Valve not saturating\n   \n5. Mode Transition Testing:\n   - Cascade → Manual → Cascade\n   - Verify: Bumpless (< 1°F vent temp change)\n   \n6. Fault Recovery:\n   - Simulate sensor fault (disconnect TIT-4033)\n   - Verify: Switches to Manual safely\n   - Reconnect sensor\n   - Verify: Auto-initializes, resumes control\n```\n\n**6.2 Operator Training**:
```\nTrain operators on:\n- Normal operation (cascade in Auto)\n- HMI displays (vent temp, product temp, valve, mode indicators)\n- When to switch to Manual (troubleshooting, maintenance)\n- How to adjust vent SP within 151-155°F range\n- Alarm response (high/low vent temp)\n- What feedforward is doing (explain bias values)\n\nProvide:\n- Operating procedures document\n- Troubleshooting guide\n- Contact for control engineering support\n```\n\n**6.3 Documentation**:
```\nCreate/Update:\n☐ Control narrative (cascade + feedforward strategy explained)\n☐ P&ID markup (show control loops, tags clearly)\n☐ PLC program comments (document all PIDE parameters)\n☐ HMI graphics (intuitive cascade indication)\n☐ Batch records template (log vent temp performance)\n☐ Maintenance procedures (when to retune, how to check)\n☐ Regulatory submissions (FDA if applicable)\n```\n\n**SUCCESS CRITERIA**:\n\n```\nCommissioning is SUCCESSFUL when:\n✅ Vent temp holds 151-155°F for 24 hours continuous operation\n✅ Responds to vapor pressure changes in <1 minute\n✅ No sustained oscillations\n✅ Valve operates 20-80% range (not saturating)\n✅ Feedforward handles >70% of disturbances\n✅ Operators comfortable with system\n✅ All alarms tested and functional\n✅ Documentation complete\n```\n\n**ROLLBACK PLAN**:\n\nIf commissioning fails:\n```\n1. Document failure mode (oscillation, instability, etc.)\n2. Revert to Manual control immediately\n3. Return to previous control method if existed\n4. Analyze data collected\n5. Revise tuning or configuration\n6. Retry when issues resolved\n\n// DO NOT leave plant in unstable automatic control\n// Manual is always acceptable fallback\n```\n\n**POST-COMMISSIONING**:\n\n```\nWeek 2-4: Monitor and optimize\n- Collect performance data\n- Fine-tune gains if minor improvements needed\n- Adjust feedforward coefficients based on seasonal data\n- Train additional operators\n- Create troubleshooting procedures based on observed issues\n\nMonth 2-3: Long-term validation\n- Verify performance across all operating conditions\n- Winter vs summer (cooling water temp)\n- High vs low production rates\n- Document any seasonal adjustments needed\n```\n\n**TIMELINE**:\n```\nDay 1: Pre-commissioning checks, manual operation\nDay 2-3: Inner loop tuning and testing\nDay 4: Cascade commissioning\nDay 5-6: Feedforward calibration\nWeek 2: Validation testing\nWeek 3-4: Optimization and operator training\nMonth 2-3: Long-term performance validation\n```\n\n**Best Practice**: Take your time during commissioning. Rushing leads to unstable control, safety issues, and operator mistrust. A methodical 2-3 week commissioning ensures decades of reliable operation."""}
    ]
})

# Write all examples to file
output_file = "/Users/reh3376/repos/plc-gbt/docs/FT/Still01_Condensers_ft.jsonl"

with open(output_file, 'a', encoding='utf-8') as f:
    for example in examples:
        f.write(json.dumps(example) + '\n')

print(f"Added {len(examples)} more training examples")
print(f"Total examples in file: Check with: grep -c '^{{' {output_file}")

